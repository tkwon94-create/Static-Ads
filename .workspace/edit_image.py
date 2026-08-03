#!/usr/bin/env python3
"""Edit an existing ad in place instead of regenerating it.

Regenerating from a prompt produces a NEW scene — different framing, different
props, different light — even when the prompt is unchanged. When the note is
"keep it exactly as it is but change one thing", the source image has to be the
input, not the prompt.

    python3 .workspace/edit_image.py --image in.png \
        --instruction "Remove the woman. Change nothing else." --out out.png
"""
import argparse
import base64
import os
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".claude/skills/winning-statics/scripts"))
from generate_static import (  # noqa: E402
    b64_image_part, call_api, extract_image, get_key,
)

PRESERVE = (
    "\n\nThis is an EDIT of the attached image, not a new image. Reproduce the "
    "attached image exactly as it is — same framing, same crop, same composition, "
    "same lighting, same colours, same depth of field, same props in the same "
    "positions, same product in the same place at the same size and angle, and "
    "every word of text identical, in the same typeface, at the same size, in the "
    "same position. Change ONLY what the instruction above asks for. Everything "
    "else must be pixel-for-pixel the same as the attached image."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--instruction", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--aspect-ratio", default="")
    ap.add_argument("--ref", default="", help="second image, e.g. the real product photo")
    a = ap.parse_args()

    key = get_key()
    parts = [b64_image_part(a.image)]
    if a.ref:
        parts.append(b64_image_part(a.ref))
    parts.append({"text": a.instruction + PRESERVE})
    payload = {"contents": [{"parts": parts}]}
    if a.aspect_ratio:
        payload["generationConfig"] = {
            "imageConfig": {"aspectRatio": a.aspect_ratio}
        }

    result = call_api(key, payload)
    data = extract_image(result)
    with open(a.out, "wb") as f:
        f.write(data)
    print(f"OK: wrote {a.out} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
