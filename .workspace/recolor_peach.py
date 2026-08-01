#!/usr/bin/env python3
"""Pull drifted peach fields back to the exact brand peach E8B093.

Nano Banana Pro renders the peach background consistently too orange — it holds red
and green but drops blue, so h08 came back #F0A860 (blue 96) and h07 #D8A878
(blue 120) against a target blue of 147. The result reads as a warmer, more
saturated orange than the site's primary color.

This corrects it deterministically rather than by regenerating: find the dominant
warm field, compute its offset from the target, and apply that offset to every
pixel near it, feathered by distance so gradients, shading and the soft vignette
survive. Flat fields land on the exact brand value; shaded areas keep their
relative modelling.

Deliberately does NOT touch:
  - the product tube (real photographed pixels — near-white, excluded by the
    saturation floor)
  - brand orange C14201 accents (far from the peach field, outside the radius)
  - text, photos of people, or any ad whose dominant color is not a warm peach

    python3 .workspace/recolor_peach.py --dir out_gemini/haloven --out out_gemini/haloven_recolored
"""
import argparse
import os

import numpy as np
from PIL import Image

TARGET = np.array([0xE8, 0xB0, 0x93], dtype=float)   # E8B093


def dominant_warm(a, quant=24):
    """Most common quantized color, if it is a warm peach-ish field."""
    q = (a // quant * quant).reshape(-1, 3)
    keys, counts = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-counts)
    for i in order[:6]:
        r, g, b = keys[i].astype(float)
        share = counts[i] / len(q)
        if share < 0.20:
            break
        # Must be a genuine peach BACKGROUND, not any warm pixel:
        #  - light (r >= 170). Without this, h06's dark wood table (#603018)
        #    was read as a peach field and 66% of the photo got shifted.
        #  - already near the target. It is supposed to BE the brand peach,
        #    just drifted; anything far away is a different color entirely.
        #  - covering at least a fifth of the frame. h03's winner-cell tint is
        #    only 8.8% of pixels while faces are far more, so correcting on it
        #    dragged skin tones along.
        if (r > g > b and (r - b) > 40 and r >= 170
                and np.linalg.norm(keys[i].astype(float) - TARGET) < 100):
            # Use the MEAN of the pixels in this bucket, not the bucket's lower
            # corner. The corner sits up to `quant`-1 below the true field color,
            # so deriving the offset from it overshoots every channel — that is
            # what pushed h07 further from target (dE 15 -> 24) on the first pass.
            flat = a.reshape(-1, 3)
            sel = np.all((flat // quant * quant) == keys[i], axis=1)
            return flat[sel].mean(axis=0), share
    return None, 0.0


def recolor(path, out_path, radius=78.0, feather=42.0):
    im = Image.open(path).convert("RGB")
    a = np.asarray(im).astype(float)

    src, share = dominant_warm(a)
    if src is None:
        im.save(out_path)
        return None

    delta = TARGET - src
    if np.abs(delta).max() < 4:
        im.save(out_path)
        return src, share, delta, 0.0

    dist = np.sqrt(((a - src) ** 2).sum(axis=2))
    # 1 inside the field, ramping to 0 across the feather band
    w = np.clip((radius + feather - dist) / feather, 0.0, 1.0)

    # never touch near-neutral pixels: that is the white tube, white text and
    # the whiteboard. Saturation floor keeps the correction on colored fields.
    mx = a.max(axis=2)
    mn = a.min(axis=2)
    sat = (mx - mn) / np.maximum(mx, 1e-6)
    w = w * np.clip((sat - 0.08) / 0.10, 0.0, 1.0)

    out = np.clip(a + delta[None, None, :] * w[:, :, None], 0, 255)
    Image.fromarray(out.astype(np.uint8)).save(out_path)
    return src, share, delta, float(w.mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    def h(c):
        return "#%02X%02X%02X" % tuple(int(v) for v in c)

    for fn in sorted(f for f in os.listdir(a.dir) if f.endswith(".png")):
        res = recolor(os.path.join(a.dir, fn), os.path.join(a.out, fn))
        if res is None:
            print(f"{fn[:26]:28} no warm field — copied unchanged")
        else:
            src, share, delta, cov = res
            print(f"{fn[:26]:28} {h(src)} -> #E8B093   "
                  f"field {share*100:4.1f}%   shifted {cov*100:4.1f}% of pixels")


if __name__ == "__main__":
    main()
