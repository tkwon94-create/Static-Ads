#!/usr/bin/env python3
"""Winning-Statics generation via the user's Higgsfield account (platform.higgsfield.ai).

Stdlib only. Credentials come from HF_API_KEY and HF_API_SECRET (a key id and its
secret) and never touch the chat or any file.

What was verified against the live API (July 2026):
  - Auth header is `Authorization: Key {key}:{secret}`.
  - A real (non-default) User-Agent is REQUIRED — Cloudflare returns 403 "error
    code: 1010" for the default Python-urllib agent. This script sets one.
  - Image-to-image (the skill's core: send the reference static + product photo)
    runs on `/v1/text2image/{model}` with body
    {"params": {"prompt", "input_images":[{"type":"image_url","image_url":URL}], "aspect_ratio"}}.
    It returns a job-set {"id", "jobs":[{"status","results":{"raw":{"url"}}}]},
    polled at `/v1/job-sets/{id}`.
  - input_images must be PUBLIC http(s) URLs — data: URIs are rejected. Local
    files are uploaded first via `/files/generate-upload-url` (presigned S3 PUT),
    which returns a public CloudFront URL. Pass already-hosted images with
    --image-url to skip the upload.
  - Nano Banana **Pro** is NOT exposed on this API; use `nano-banana` (Google's
    image-edit model) or `seedream`. Run --list-catalog to probe what your key has.

Note on locked-down networks: some managed environments allow platform.higgsfield.ai
but block the S3 upload host and the CloudFront result host. There, uploads and
downloads fail even though generation succeeds. Host inputs on a public URL you
control (e.g. a public GitHub raw URL) and pass --image-url, and fetch the result
URL this script prints from a machine without that egress firewall.

Usage:
  python3 higgsfield_backend.py --self-test
  python3 higgsfield_backend.py --list-catalog
  python3 higgsfield_backend.py \
      --model nano-banana \
      --image-url https://.../ref-13-price-anchor-slash.png \
      --image-url https://.../product.png \
      --prompt-file /tmp/prompt_01.txt --aspect-ratio 1:1 --out out/static_01.png
  # or with local files (needs egress to the S3 upload host):
  python3 higgsfield_backend.py --model nano-banana \
      --image references/ref-13-price-anchor-slash.png --image product.png ...

Exit codes: 0 success, 1 credentials problem, 2 generation problem.
"""

import argparse
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request

BASE = "https://platform.higgsfield.ai"
DEFAULT_MODEL = os.environ.get("HIGGSFIELD_MODEL", "nano-banana")
USER_AGENT = "higgsfield-client-py/1.0"
POLL_SECONDS = 5
POLL_TIMEOUT = 900


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def get_creds():
    key = os.environ.get("HF_API_KEY", "").strip()
    secret = os.environ.get("HF_API_SECRET", "").strip()
    if not key or not secret:
        fail("KEY ERROR: set HF_API_KEY and HF_API_SECRET (key id + secret from cloud.higgsfield.ai).", 1)
    if key.lower().startswith(("your", "xxx", "placeholder", "changeme", "<")):
        fail(f"KEY ERROR: HF_API_KEY is placeholder text ('{key[:8]}...'). Paste your real key.", 1)
    return key, secret


def api(method, url, key, secret, body=None, raw_body=None, content_type=None):
    headers = {"Authorization": f"Key {key}:{secret}", "User-Agent": USER_AGENT, "Accept": "application/json"}
    data = None
    if raw_body is not None:
        data = raw_body
        headers["Content-Type"] = content_type
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                payload = resp.read()
                return json.loads(payload) if payload and content_type is None else payload
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")
            if e.code in (401, 403) and "1010" in text:
                fail("BLOCKED: Cloudflare rejected the request (1010). A real User-Agent is required — this script sets one; if you see this, the network may be interfering.", 2)
            if e.code in (401, 403) and ("invalid credentials" in text.lower() or "credential" in text.lower()):
                fail("KEY ERROR: Higgsfield rejected the credentials. Re-copy key and secret from cloud.higgsfield.ai.", 1)
            if e.code == 403 and "allowlist" in text.lower():
                fail(f"NETWORK ERROR: this environment's egress policy blocks {url.split('/')[2]}. Host inputs on a public URL (--image-url) and download results elsewhere.", 2)
            if e.code == 404:
                fail(f"MODEL ERROR: {url} not found. Nano Banana Pro is not on this API — try --model nano-banana or --list-catalog.", 2)
            if e.code == 402 or "credit" in text.lower():
                fail("BILLING ERROR: not enough Higgsfield credits. Top up at cloud.higgsfield.ai (the developer API uses a separate wallet from the consumer app).", 1)
            if e.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            fail(f"API ERROR (HTTP {e.code}): {text[:300]}", 2)
        except urllib.error.URLError as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            fail(f"NETWORK ERROR: {e.reason}", 2)


def upload(path, key, secret):
    ct = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    info = api("POST", f"{BASE}/files/generate-upload-url", key, secret, body={"content_type": ct})
    with open(path, "rb") as f:
        blob = f.read()
    # presigned S3 PUT: the URL carries its own auth; adding the Higgsfield
    # Authorization header makes S3 reject with "Only one auth mechanism allowed"
    req = urllib.request.Request(info["upload_url"], data=blob,
        headers={"Content-Type": ct, "User-Agent": USER_AGENT}, method="PUT")
    with urllib.request.urlopen(req, timeout=300) as resp:
        resp.read()
    return info["public_url"]


def generate(args):
    key, secret = get_creds()
    prompt = args.prompt
    if args.prompt_file:
        with open(args.prompt_file) as f:
            prompt = f.read()
    if not prompt:
        fail("No prompt (use --prompt or --prompt-file).")

    urls = list(args.image_url or [])
    for p in args.image or []:
        urls.append(upload(p, key, secret))
    if not urls:
        fail("No input images. Pass --image-url (public URL) or --image (local file to upload).")

    payload = {"params": {
        "prompt": prompt,
        "input_images": [{"type": "image_url", "image_url": u} for u in urls],
        "aspect_ratio": args.aspect_ratio,
    }}
    js = api("POST", f"{BASE}/v1/text2image/{args.model}", key, secret, body=payload)
    sid = js.get("id")
    if not sid:
        fail("GENERATION ERROR: submit returned no job-set id:\n" + json.dumps(js)[:400])
    print(f"submitted job-set {sid}")

    start = time.time()
    while time.time() - start < POLL_TIMEOUT:
        time.sleep(POLL_SECONDS)
        st = api("GET", f"{BASE}/v1/job-sets/{sid}", key, secret)
        job = st["jobs"][0]
        status = job["status"]
        if status == "completed":
            url = job["results"]["raw"]["url"]
            print(f"COMPLETED: {url}")
            try:
                data = api("GET", url, key, secret, content_type="image/png")
                os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
                with open(args.out, "wb") as f:
                    f.write(data)
                print(f"OK: wrote {args.out} ({len(data)} bytes)")
            except SystemExit:
                print(f"NOTE: could not download here (egress-blocked). Fetch the URL above from an unrestricted machine.")
            return
        if status == "nsfw":
            fail("SAFETY BLOCK: Higgsfield moderation declined this image (credits refunded). Rephrase the claim or switch reference.")
        if status == "failed":
            fail("GENERATION ERROR: the job failed (credits refunded). Retry, or try a sibling reference.")
    fail(f"TIMEOUT: job-set {sid} not finished after {POLL_TIMEOUT}s.")


def list_catalog(key, secret):
    """Probe common image model routes to see which this account can reach."""
    candidates = ["nano-banana", "seedream", "soul"]
    print("Probing /v1/text2image/{model} (422 = reachable, needs params; 404 = not available):")
    for m in candidates:
        try:
            api("POST", f"{BASE}/v1/text2image/{m}", key, secret, body={"params": {"prompt": "x"}})
            print(f"  {m}: reachable")
        except SystemExit:
            print(f"  {m}: see message above")
    print("Full gallery: https://cloud.higgsfield.ai/explore (API model id = the model page's URL slug).")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--list-catalog", action="store_true")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"model id (default {DEFAULT_MODEL})")
    p.add_argument("--image", action="append", help="local image file, uploaded to Higgsfield's CDN first")
    p.add_argument("--image-url", action="append", help="already-public image URL (skips upload)")
    p.add_argument("--prompt")
    p.add_argument("--prompt-file")
    p.add_argument("--aspect-ratio", default="1:1")
    p.add_argument("--out")
    args = p.parse_args()

    if args.self_test:
        key, secret = get_creds()
        print(f"credentials present (key {len(key)} chars, secret {len(secret)} chars).")
        list_catalog(key, secret)
        print("Self-test PASSED.")
        return
    if args.list_catalog:
        list_catalog(*get_creds())
        return
    if not args.out:
        p.error("--out is required (or use --self-test / --list-catalog)")
    generate(args)


if __name__ == "__main__":
    main()
