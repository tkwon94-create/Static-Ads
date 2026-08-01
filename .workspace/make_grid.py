#!/usr/bin/env python3
"""Build a labeled contact sheet from a folder of finished ads.

    python3 .workspace/make_grid.py --dir out_gemini/haloven --out out_gemini/haloven_grid.png
"""
import argparse
import os

from PIL import Image, ImageDraw

CELL = 460
PAD = 14
LABEL = 26


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=4)
    a = ap.parse_args()

    files = sorted(f for f in os.listdir(a.dir) if f.lower().endswith(".png"))
    if not files:
        raise SystemExit(f"no PNGs in {a.dir}")

    cols = min(a.cols, len(files))
    rows = (len(files) + cols - 1) // cols
    W = cols * (CELL + PAD) + PAD
    H = rows * (CELL + LABEL + PAD) + PAD

    sheet = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(sheet)

    for i, fn in enumerate(files):
        im = Image.open(os.path.join(a.dir, fn)).convert("RGB")
        im.thumbnail((CELL, CELL), Image.LANCZOS)
        cx = PAD + (i % cols) * (CELL + PAD)
        cy = PAD + (i // cols) * (CELL + LABEL + PAD)
        sheet.paste(im, (cx + (CELL - im.width) // 2, cy + (CELL - im.height) // 2))
        draw.rectangle([cx, cy, cx + CELL, cy + CELL], outline=(210, 210, 210))
        draw.text((cx + 2, cy + CELL + 6), fn.replace(".png", ""), fill=(20, 20, 20))

    sheet.save(a.out)
    print(f"{len(files)} ads -> {a.out}  ({sheet.width}x{sheet.height})")


if __name__ == "__main__":
    main()
