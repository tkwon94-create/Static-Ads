#!/usr/bin/env python3
"""Convert ads to a true 1:1 square at Meta's 1080x1080 spec without losing content.

Cropping 4:5 to 1:1 removes 19% of the height, and every one of these ads uses that
space: h05 would lose a caption bubble, h06 its trust card, h01 its attribution line,
h04 an entire panel. So the canvas is EXTENDED sideways instead of cropped.

The extension is not a flat bar. Each side is grown from the image's own edge column,
mirrored and progressively blurred outward, so a flat or gradient background (h01, h09,
h11, h12) continues seamlessly and a photographic one (h05, h06, h10) fades into a soft
continuation of its own edge tones rather than hitting a hard border.

    python3 .workspace/to_square.py --dir out_gemini/final --out out_gemini/square_1080
"""
import argparse
import os

import numpy as np
from PIL import Image, ImageFilter

TARGET = 1080


def extend_sides(im, target_w, sample=14):
    """Grow the image to target_w by continuing each ROW's own edge colour outward.

    The first attempt mirrored the edge columns. That duplicates whatever sits near
    the border — on h04 and h05 it produced legible REVERSED TEXT in the margins, and
    on h02 a second copy of the window frame. Sampling a per-row colour instead
    continues the background's vertical variation (h04's three panels each keep their
    own tone) while inventing no content at all.
    """
    w, h = im.size
    if w >= target_w:
        return im
    pad = target_w - w
    left, right = pad // 2, pad - pad // 2

    a = np.asarray(im.convert("RGB")).astype(float)
    lcol = a[:, :sample, :].mean(axis=1)      # (h,3) average of leftmost columns
    rcol = a[:, -sample:, :].mean(axis=1)

    # smooth vertically so per-row noise does not band the margin
    k = 9
    pad_edge = np.pad(lcol, ((k // 2, k // 2), (0, 0)), mode="edge")
    lcol = np.stack([np.convolve(pad_edge[:, c], np.ones(k) / k, "valid") for c in range(3)], 1)
    pad_edge = np.pad(rcol, ((k // 2, k // 2), (0, 0)), mode="edge")
    rcol = np.stack([np.convolve(pad_edge[:, c], np.ones(k) / k, "valid") for c in range(3)], 1)

    out = np.zeros((h, target_w, 3), dtype=float)
    out[:, left:left + w, :] = a
    if left:
        out[:, :left, :] = lcol[:, None, :]
    if right:
        out[:, target_w - right:, :] = rcol[:, None, :]

    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    # soften only the two seams so the join is invisible
    blur = np.asarray(img.filter(ImageFilter.GaussianBlur(6))).astype(float)
    ramp = np.zeros(target_w)
    band = 26
    if left:
        ramp[max(0, left - band):left + band] = np.hanning(min(2 * band, left + band - max(0, left - band)))
    if right:
        r0 = target_w - right
        ramp[max(0, r0 - band):min(target_w, r0 + band)] = np.hanning(
            min(target_w, r0 + band) - max(0, r0 - band))
    wgt = ramp[None, :, None]
    merged = np.asarray(img).astype(float) * (1 - wgt) + blur * wgt
    return Image.fromarray(np.clip(merged, 0, 255).astype(np.uint8))


def squarify(path, out_path, size=TARGET):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    if w == h:
        im.resize((size, size), Image.LANCZOS).save(out_path, quality=95)
        return "resized"
    if w > h:                      # landscape: extend vertically (none here, but safe)
        im = im.transpose(Image.ROTATE_90)
        im = extend_sides(im, im.height)
        im = im.transpose(Image.ROTATE_270)
    else:
        im = extend_sides(im, h)
    im.resize((size, size), Image.LANCZOS).save(out_path, quality=95)
    return "extended"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--size", type=int, default=TARGET)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for fn in sorted(f for f in os.listdir(a.dir) if f.endswith(".png")):
        src = os.path.join(a.dir, fn)
        w, h = Image.open(src).size
        how = squarify(src, os.path.join(a.out, fn), a.size)
        print(f"  {fn[:26]:28} {w}x{h} -> {a.size}x{a.size}  ({how})")


if __name__ == "__main__":
    main()
