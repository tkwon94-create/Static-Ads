#!/usr/bin/env python3
"""Composite the real product tube into Gemini layouts generated with --placeholder.

run_gemini_batch.py --placeholder makes Nano Banana Pro paint a flat magenta block
where the product belongs. This pastes the user's real tube photo into that block, so
the label is the user's exact pixels and no model ever draws it.

Reuses find_magenta / inpaint / prep_product from gold_standard_ads.py — the same
pipeline the delivered Higgsfield batches used.

    python3 .workspace/composite_gemini.py --layouts out_gemini/haloven_layouts \
                                           --out     out_gemini/haloven
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image, ImageFilter  # noqa: E402
from gold_standard_ads import find_magenta, inpaint, prep_product  # noqa: E402

PRODUCT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       ".workspace/inputs/laventra_user_tube.png")


def composite_file(layout_path, product, out_path, pad=0.0):
    """Paste `product` into the magenta zone of `layout_path`. Returns True on success."""
    layout = Image.open(layout_path).convert("RGBA")
    mask, box = find_magenta(layout)
    if mask is None:
        layout.convert("RGB").save(out_path)
        return False

    l, t, r, b = box
    bw, bh = r - l + 1, b - t + 1

    # dilate to swallow anti-aliased magenta fringes, then inpaint the hole away
    mask = mask.filter(ImageFilter.MaxFilter(9))
    base = inpaint(layout, mask).convert("RGBA")

    prod = prep_product(product)
    # optional inset so the tube doesn't touch the placeholder's edges
    tw, th = bw * (1 - pad), bh * (1 - pad)
    scale = min(tw / prod.width, th / prod.height)
    nw, nh = max(1, int(prod.width * scale)), max(1, int(prod.height * scale))
    prod = prod.resize((nw, nh), Image.LANCZOS)

    base.alpha_composite(prod, (l + (bw - nw) // 2, t + (bh - nh) // 2))
    base.convert("RGB").save(out_path)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layouts", required=True, help="dir of magenta-placeholder layouts")
    ap.add_argument("--out", required=True, help="dir to write finished ads into")
    ap.add_argument("--product", default=PRODUCT)
    ap.add_argument("--pad", type=float, default=0.0,
                    help="fractional inset inside the placeholder box, e.g. 0.06")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    product = Image.open(a.product)

    done, missing = [], []
    for fn in sorted(os.listdir(a.layouts)):
        if not fn.lower().endswith(".png"):
            continue
        src = os.path.join(a.layouts, fn)
        dst = os.path.join(a.out, fn)
        if composite_file(src, product, dst, a.pad):
            print(f"  composited {fn}")
            done.append(fn)
        else:
            print(f"  !! NO magenta zone in {fn} — copied through unchanged")
            missing.append(fn)

    print(f"\n{len(done)} composited -> {a.out}")
    if missing:
        print("no placeholder found (regenerate these): " + ", ".join(missing))


if __name__ == "__main__":
    main()
