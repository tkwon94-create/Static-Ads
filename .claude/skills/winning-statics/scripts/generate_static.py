#!/usr/bin/env python3
"""Winning-Statics image generation via Google's Nano Banana Pro (Gemini image model).

Stdlib only — no pip installs needed. The API key is read from the
GEMINI_API_KEY environment variable and never touches the chat or any file.

Usage:
  # Generate one static from a reference + product photo + swap instructions
  python3 generate_static.py \
      --reference references/ref-13-price-anchor-slash.png \
      --product /path/to/product.png \
      --prompt-file /tmp/prompt_01.txt \
      --aspect-ratio 1:1 \
      --out out/static_01.png

  # Or pass the prompt inline
  python3 generate_static.py --reference ... --product ... --prompt "..." --out ...

  # Verify setup (key present, model reachable; generates one tiny test image ~$0.14)
  python3 generate_static.py --self-test

Exit codes: 0 success, 1 setup/key problem, 2 generation problem.
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

MODEL = "gemini-3-pro-image-preview"  # Nano Banana Pro
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
MAX_RETRIES = 3


def fail(msg, code=2):
    print(msg, file=sys.stderr)
    sys.exit(code)


def get_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        fail(
            "KEY ERROR: GEMINI_API_KEY is not set.\n"
            "Set it in your shell profile and open a NEW terminal.\n"
            "See GEMINI_SETUP.md for the click-by-click walkthrough.",
            code=1,
        )
    return key


def b64_image_part(path):
    ext = os.path.splitext(path)[1].lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(ext)
    if mime is None:
        fail(f"Unsupported image type: {path} (use png/jpg/webp)")
    with open(path, "rb") as f:
        data = f.read()
    return {"inline_data": {"mime_type": mime, "data": base64.b64encode(data).decode()}}


def classify_http_error(status, body):
    text = body.lower()
    if status == 400 and "api_key_invalid" in text:
        return "KEY ERROR: API key not valid. Re-copy it from aistudio.google.com (see GEMINI_SETUP.md).", 1
    if status == 403:
        if "billing" in text or "free tier" in text:
            return "BILLING ERROR: this model needs billing enabled on your Google project (see GEMINI_SETUP.md step 4).", 1
        return "PERMISSION ERROR: your key can't use this model. Check the key's project in AI Studio.", 1
    if status == 404:
        return f"MODEL ERROR: model not found ({MODEL}). Update MODEL at the top of this script to the current Nano Banana Pro id.", 2
    if status == 429:
        if "billing" in text or "free tier" in text or "plan" in text:
            return "BILLING ERROR: image generation isn't available on the free tier — enable billing (GEMINI_SETUP.md step 4).", 1
        return "QUOTA ERROR: rate limited. Retrying usually fixes this; if it never clears, check your quota in AI Studio.", 2
    return f"API ERROR (HTTP {status}): {body[:500]}", 2


def call_api(key, payload):
    url = ENDPOINT.format(model=MODEL)
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
        method="POST",
    )
    last_msg, last_code = "NETWORK ERROR: could not reach the API.", 2
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            last_msg, last_code = classify_http_error(e.code, body)
            # retry only transient statuses
            if e.code not in (429, 500, 502, 503, 504) or attempt == MAX_RETRIES:
                fail(last_msg, last_code)
        except urllib.error.URLError as e:
            last_msg = f"NETWORK ERROR: {e.reason}. Check your connection/proxy/VPN."
            if attempt == MAX_RETRIES:
                fail(last_msg, 2)
        wait = 2 ** attempt
        print(f"  transient error, retrying in {wait}s ({attempt}/{MAX_RETRIES})...", file=sys.stderr)
        time.sleep(wait)
    fail(last_msg, last_code)


def extract_image(result):
    for cand in result.get("candidates", []):
        reason = cand.get("finishReason", "")
        if reason in ("SAFETY", "PROHIBITED_CONTENT", "IMAGE_SAFETY"):
            fail(
                "SAFETY BLOCK: the model declined this image. Rephrase the claim "
                "(health/medical wording trips this most often) or pick a different reference."
            )
        for part in cand.get("content", {}).get("parts", []):
            inline = part.get("inlineData") or part.get("inline_data")
            if inline and inline.get("data"):
                return base64.b64decode(inline["data"])
    fb = result.get("promptFeedback", {})
    if fb.get("blockReason"):
        fail(f"SAFETY BLOCK: prompt blocked ({fb['blockReason']}). Rephrase and retry.")
    fail("GENERATION ERROR: the response contained no image. Full response:\n" + json.dumps(result)[:1000])


def generate(args):
    key = get_key()
    prompt = args.prompt
    if args.prompt_file:
        with open(args.prompt_file) as f:
            prompt = f.read()
    if not prompt:
        fail("No prompt given (use --prompt or --prompt-file).")

    parts = [b64_image_part(args.reference)]
    if args.product:
        parts.append(b64_image_part(args.product))
    for extra in args.extra_image or []:
        parts.append(b64_image_part(extra))
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": args.aspect_ratio},
        },
    }
    result = call_api(key, payload)
    img = extract_image(result)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "wb") as f:
        f.write(img)
    print(f"OK: wrote {args.out} ({len(img)} bytes)")


def self_test():
    key = get_key()
    print(f"1/2 GEMINI_API_KEY found ({len(key)} chars).")
    payload = {
        "contents": [{"parts": [{"text": 'Generate a simple flat test image: a green circle on a white background with the word "READY" under it.'}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": "1:1"},
        },
    }
    result = call_api(key, payload)
    img = extract_image(result)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "self_test_output.png")
    with open(out, "wb") as f:
        f.write(img)
    print(f"2/2 Model reachable — test image written to {out}")
    print("Self-test PASSED. You're ready to generate statics.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--self-test", action="store_true", help="verify key + model access with one tiny image")
    p.add_argument("--reference", help="path to the winning reference static (sent as an image)")
    p.add_argument("--product", help="path to the user's product photo (sent as an image)")
    p.add_argument("--extra-image", action="append", help="additional input image (repeatable), e.g. real customer photos")
    p.add_argument("--prompt", help="swap instructions; put any text that must appear in the image in verbatim quotes")
    p.add_argument("--prompt-file", help="read the prompt from a file instead")
    p.add_argument("--aspect-ratio", default="1:1", help="1:1, 4:5, 3:4, 9:16, 16:9... (default 1:1)")
    p.add_argument("--out", help="output PNG path")
    args = p.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.reference or not args.out:
        p.error("--reference and --out are required (or use --self-test)")
    generate(args)


if __name__ == "__main__":
    main()
