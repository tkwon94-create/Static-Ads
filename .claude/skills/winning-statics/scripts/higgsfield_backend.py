#!/usr/bin/env python3
"""Winning-Statics generation via the user's Higgsfield account (platform.higgsfield.ai).

Stdlib only. Credentials come from the HF_API_KEY and HF_API_SECRET environment
variables and never touch the chat or any file.

Higgsfield is an async job API: submit -> poll -> download. Input images are
passed by URL (`image_url` / `image_urls`); this script also tries data: URIs
for local files, and tells you plainly if the model rejects them.

Usage:
  # Discover the exact image-edit model ids available to this account
  python3 higgsfield_backend.py --list-models

  # Verify credentials
  python3 higgsfield_backend.py --self-test

  # Generate one static (reference + product photo as URLs or local files)
  python3 higgsfield_backend.py \
      --model google/nano-banana-pro \
      --image references/ref-13-price-anchor-slash.png \
      --image /path/to/product.png \
      --prompt-file /tmp/prompt_01.txt \
      --aspect-ratio 1:1 \
      --out out/static_01.png

Exit codes: 0 success, 1 credentials problem, 2 generation problem.
"""

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "https://platform.higgsfield.ai"
DEFAULT_MODEL = os.environ.get("HIGGSFIELD_MODEL", "google/nano-banana-pro")
POLL_SECONDS = 4
POLL_TIMEOUT = 600


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def get_creds():
    key = os.environ.get("HF_API_KEY", "").strip()
    secret = os.environ.get("HF_API_SECRET", "").strip()
    if not key or not secret:
        fail(
            "KEY ERROR: HF_API_KEY / HF_API_SECRET are not set.\n"
            "Get them from your Higgsfield account (cloud.higgsfield.ai -> API keys)\n"
            "and set both environment variables, then retry.",
            code=1,
        )
    placeholderish = ("your", "xxx", "placeholder", "changeme", "<")
    if key.lower().startswith(placeholderish) or secret.lower().startswith(placeholderish):
        fail(
            "KEY ERROR: HF_API_KEY / HF_API_SECRET contain placeholder text\n"
            f"  (HF_API_KEY starts with '{key[:8]}...').\n"
            "Replace them with your real Higgsfield key and secret. In a Claude Code\n"
            "cloud session, edit the environment's variables at claude.ai/code ->\n"
            "your environment -> settings, then start a fresh session.",
            code=1,
        )
    return key, secret


def request(method, url, key, secret, payload=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": f"Key {key}:{secret}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if e.code in (401, 403) or "invalid credentials" in body.lower():
            fail("KEY ERROR: Higgsfield rejected the credentials. Re-copy key and secret from cloud.higgsfield.ai.", 1)
        if e.code == 404:
            fail(f"MODEL ERROR: {url} not found. Run --list-models to see the exact model ids your account has.", 2)
        if e.code == 402 or "credit" in body.lower():
            fail("BILLING ERROR: not enough Higgsfield credits. Top up at cloud.higgsfield.ai.", 1)
        if e.code == 422:
            fail(
                "REQUEST ERROR: the model rejected the payload (HTTP 422):\n" + body[:800] +
                "\nIf this mentions image_url/image_urls, the model may not accept data: URIs — "
                "pass publicly reachable https URLs with --image-url instead.", 2)
        fail(f"API ERROR (HTTP {e.code}): {body[:500]}", 2)
    except urllib.error.URLError as e:
        fail(f"NETWORK ERROR: {e.reason}. Check your connection/proxy.", 2)


def to_image_url(path_or_url):
    if path_or_url.startswith(("http://", "https://", "data:")):
        return path_or_url
    if not os.path.exists(path_or_url):
        fail(f"File not found: {path_or_url}")
    mime = mimetypes.guess_type(path_or_url)[0] or "image/png"
    with open(path_or_url, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def poll(status_url, key, secret):
    start = time.time()
    while time.time() - start < POLL_TIMEOUT:
        result = request("GET", status_url, key, secret)
        status = result.get("status")
        if status == "completed":
            return result
        if status == "nsfw":
            fail("SAFETY BLOCK: Higgsfield's moderation declined this image (credits refunded). "
                 "Rephrase the claim or pick a different reference.")
        if status == "failed":
            fail("GENERATION ERROR: the job failed on Higgsfield's side (credits refunded). "
                 "Retry once; if it persists, try a sibling reference.")
        time.sleep(POLL_SECONDS)
    fail("TIMEOUT: job still not finished after 10 minutes. Check it later via: " + status_url)


def download(url, out):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with urllib.request.urlopen(url, timeout=300) as resp, open(out, "wb") as f:
        data = resp.read()
        f.write(data)
    return len(data)


def generate(args):
    key, secret = get_creds()
    prompt = args.prompt
    if args.prompt_file:
        with open(args.prompt_file) as f:
            prompt = f.read()
    if not prompt:
        fail("No prompt given (use --prompt or --prompt-file).")

    urls = [to_image_url(p) for p in (args.image or [])] + (args.image_url or [])
    payload = {"prompt": prompt}
    if args.aspect_ratio:
        payload["aspect_ratio"] = args.aspect_ratio
    if len(urls) == 1:
        payload["image_url"] = urls[0]
    elif len(urls) > 1:
        payload["image_urls"] = urls
    for kv in args.param or []:
        if "=" not in kv:
            fail(f"--param expects key=value, got: {kv}")
        k, v = kv.split("=", 1)
        try:
            payload[k] = json.loads(v)
        except ValueError:
            payload[k] = v

    submit = request("POST", f"{BASE}/{args.model}", key, secret, payload)
    status_url = submit.get("status_url") or f"{BASE}/requests/{submit.get('request_id')}/status"
    print(f"submitted: request_id={submit.get('request_id')} status={submit.get('status')}")
    result = poll(status_url, key, secret)

    images = result.get("images") or []
    if not images:
        fail("GENERATION ERROR: job completed but returned no images:\n" + json.dumps(result)[:800])
    n = download(images[0]["url"], args.out)
    print(f"OK: wrote {args.out} ({n} bytes)")
    for i, extra in enumerate(images[1:], start=2):
        alt = os.path.splitext(args.out)[0] + f"_{i}" + os.path.splitext(args.out)[1]
        download(extra["url"], alt)
        print(f"    also wrote {alt}")


def list_models(key, secret):
    for path in ("/models", "/v1/models", "/models/list"):
        try:
            result = request("GET", BASE + path, key, secret)
            print(json.dumps(result, indent=2))
            return
        except SystemExit:
            continue
    print(
        "Could not find a model-listing endpoint. Browse your available models at\n"
        "https://cloud.higgsfield.ai/explore — the API model id matches the URL path\n"
        "of the model page (e.g. google/nano-banana-pro).",
        file=sys.stderr,
    )


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--self-test", action="store_true", help="verify credentials are present, real, and accepted")
    p.add_argument("--list-models", action="store_true", help="list model ids available to this account")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"model id (default {DEFAULT_MODEL}; override with HIGGSFIELD_MODEL)")
    p.add_argument("--image", action="append", help="local image file (reference static, product photo); sent as data: URI")
    p.add_argument("--image-url", action="append", help="publicly reachable https image URL")
    p.add_argument("--prompt", help="swap instructions; put any text that must appear in the image in verbatim quotes")
    p.add_argument("--prompt-file", help="read the prompt from a file instead")
    p.add_argument("--aspect-ratio", default="1:1", help="1:1, 4:5, 16:9... (default 1:1)")
    p.add_argument("--param", action="append", help="extra payload field as key=value (value parsed as JSON when possible)")
    p.add_argument("--out", help="output image path")
    args = p.parse_args()

    if args.self_test:
        key, secret = get_creds()
        print(f"1/2 credentials found (key {len(key)} chars, secret {len(secret)} chars) and not placeholders.")
        list_models(key, secret)
        print("2/2 Higgsfield accepted the credentials. Self-test PASSED.")
        return
    if args.list_models:
        list_models(*get_creds())
        return
    if not args.out:
        p.error("--out is required (or use --self-test / --list-models)")
    generate(args)


if __name__ == "__main__":
    main()
