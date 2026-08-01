#!/usr/bin/env python3
"""Composite the real product tube into a layout so it looks photographed, not pasted.

Replaces composite_gemini.py. Four changes, each fixing a defect the user found:

1. OCCLUSION. The old compositor pasted the tube as a solid rectangle over the whole
   placeholder box, which buried the fingers gripping it — on h10 she appeared to hold
   a torso-sized slab with no visible hands. Pro draws fingers wrapping the magenta
   block, and those finger pixels are skin, not magenta. So the paste is stencilled:
   the tube goes down, then every non-magenta pixel from inside the box is restored on
   top. Fingers survive, the tube sits behind them, the grip reads real.

2. SCALE. The old compositor sized the tube to FILL the placeholder box, so the model's
   arbitrary block dictated physical size — huge on h10, thumbnail on h09. Scale now
   comes from the frame with a per-ad override, clamped to a plausible range.

3. SEATING. A composited object with no contact shadow reads as a sticker. A soft
   directional shadow is laid under the tube before it is pasted.

4. SCENE MATCH. The product photo is studio-lit on white, razor sharp and neutral. The
   scenes are warm, softly lit and carry camera grain. The tube is matched to the local
   scene: white balance pulled toward the surrounding pixels, a touch of blur to sit on
   the same focal plane, and grain matched to the plate.

    python3 .workspace/composite_v2.py --layouts DIR --out DIR \
            --scale h09=0.40,h10=0.26 --light h02=left
"""
import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gold_standard_ads import find_magenta, inpaint, prep_product  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCT = os.path.join(ROOT, ".workspace/inputs/laventra_user_tube.png")

# Fraction of frame height the tube should occupy. Physical plausibility, not the
# model's whim. A 100 ml tube is roughly hand-length, so in a portrait with a person
# it should read small; in a flat product hero it can carry the frame.
DEFAULT_SCALE = 0.32
SCALE_MIN, SCALE_MAX = 0.10, 0.62


def magenta_pixels(img, box, margin=18):
    """Boolean mask of placeholder pixels, confined to the placeholder's own box.

    Confined because a global hue test cannot separate the crimson placeholder
    (b/r 0.53 on h10) from red dry-erase ink (b/r 0.46 on h02) — a global pass
    erased h02's X marks. Inside the box there is no such ambiguity.
    """
    a = np.asarray(img.convert("RGB")).astype(int)
    H, W = a.shape[:2]
    l, t, r, b = box
    x0, x1 = max(0, l - margin), min(W - 1, r + margin)
    y0, y1 = max(0, t - margin), min(H - 1, b + margin)

    win = a[y0:y1 + 1, x0:x1 + 1]
    cr, cg, cb = win[:, :, 0], win[:, :, 1], win[:, :, 2]
    # magenta / crimson / pink: red and blue both above green. Skin fails this
    # (blue sits below green on skin), so fingers are preserved.
    # Aggressive on purpose. Fingers are now protected geometrically (holes_inside),
    # not by hue, so this no longer has to stay clear of skin — and a timid threshold
    # is what left pink residue around the tube base on h04 and h10. Skin still fails
    # the test anyway: on skin blue sits below green.
    m = ((cr - cg) >= 8) & ((cb - cg) >= 3)

    full = np.zeros((H, W), dtype=bool)
    full[y0:y1 + 1, x0:x1 + 1] = m

    # Grow outward through CONNECTED placeholder-coloured pixels. find_magenta's box
    # covers the block itself, but Pro often paints a shaded skirt or cast beyond it,
    # and those pixels sat outside the window and survived as the pink slabs under the
    # tube on h08, h09 and h10. Growing only through contiguous magenta-ish pixels
    # picks that up without ever going global (which is what erased h02's X marks).
    loose = ((a[:, :, 0] - a[:, :, 1]) >= 6) & ((a[:, :, 2] - a[:, :, 1]) >= 1)
    seed = full.copy()
    stack = [tuple(v) for v in np.argwhere(seed)]
    while stack:
        y, x = stack.pop()
        for ny, nx in ((y+1, x), (y-1, x), (y, x+1), (y, x-1)):
            if 0 <= ny < H and 0 <= nx < W and loose[ny, nx] and not seed[ny, nx]:
                seed[ny, nx] = True
                stack.append((ny, nx))
    full = seed

    ys2, xs2 = np.nonzero(full)
    if len(ys2):
        x0, x1 = int(xs2.min()), int(xs2.max())
        y0, y1 = int(ys2.min()), int(ys2.max())
    return full, (x0, y0, x1, y1)


def holes_inside(mask, win):
    """Pixels enclosed BY the placeholder but not part of it — i.e. fingers crossing it.

    Found by flooding the non-mask area inward from the window border: anything the
    flood cannot reach is surrounded by placeholder and therefore sits in front of it.
    """
    x0, y0, x1, y1 = win
    sub = mask[y0:y1 + 1, x0:x1 + 1]
    h, w = sub.shape
    free = ~sub
    reached = np.zeros_like(free)
    stack = []
    for x in range(w):
        for y in (0, h - 1):
            if free[y, x]:
                stack.append((y, x)); reached[y, x] = True
    for y in range(h):
        for x in (0, w - 1):
            if free[y, x] and not reached[y, x]:
                stack.append((y, x)); reached[y, x] = True
    while stack:
        y, x = stack.pop()
        for ny, nx in ((y+1, x), (y-1, x), (y, x+1), (y, x-1)):
            if 0 <= ny < h and 0 <= nx < w and free[ny, nx] and not reached[ny, nx]:
                reached[ny, nx] = True
                stack.append((ny, nx))
    holes = free & ~reached
    out = np.zeros_like(mask)
    out[y0:y1 + 1, x0:x1 + 1] = holes
    return out


def contact_shadow(size, w, h, cx, cy, direction="left"):
    """Soft elliptical shadow under the product, offset away from the key light.

    A composited object with no shadow reads as a sticker — this is the single
    strongest cue that the tube was pasted rather than photographed.
    """
    W, H = size
    sh = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(sh)
    ex, ey = int(w * 0.48), max(3, int(h * 0.06))
    off = int(w * (0.12 if direction == "left" else -0.12))
    base_y = cy + h // 2
    d.ellipse([cx + off - ex, base_y - ey, cx + off + ex, base_y + ey], fill=165)
    return sh.filter(ImageFilter.GaussianBlur(max(5, int(h * 0.05))))


def match_scene(prod_rgba, plate, cx, cy, strength=0.16, blur=0.5, grain=None):
    """Nudge the product toward the scene's colour, softness and grain.

    Kept deliberately gentle. At 0.55 the white tube took on the sweater's beige and
    read as translucent — worse than the mismatch it was correcting. The goal is a
    hint of the room's warmth on the product's own highlights, not a colour transfer.
    """
    pa = np.asarray(prod_rgba).astype(float)
    rgb, alpha = pa[:, :, :3], pa[:, :, 3:4] / 255.0

    # local scene colour: a ring of plate pixels around where the product will sit
    W, H = plate.size
    ph, pw = pa.shape[:2]
    x0 = max(0, cx - pw); x1 = min(W, cx + pw)
    y0 = max(0, cy - ph); y1 = min(H, cy + ph)
    ring = np.asarray(plate.convert("RGB")).astype(float)[y0:y1, x0:x1]
    if ring.size:
        scene = ring.reshape(-1, 3).mean(axis=0)
        # only the product's own light areas should take the cast, so weight by
        # luminance — the label's dark ink must stay dark
        lum = rgb.mean(axis=2, keepdims=True) / 255.0
        cast = (scene - rgb.mean(axis=(0, 1))) * strength
        rgb = np.clip(rgb + cast[None, None, :] * lum, 0, 255)

    out = Image.fromarray(np.concatenate([rgb, alpha * 255], axis=2).astype(np.uint8))
    if blur:
        out = out.filter(ImageFilter.GaussianBlur(blur))
    if grain:
        n = np.random.default_rng(7).normal(0, grain, (out.height, out.width, 1))
        o = np.asarray(out).astype(float)
        o[:, :, :3] = np.clip(o[:, :, :3] + n, 0, 255)
        out = Image.fromarray(o.astype(np.uint8))
    return out


def plate_grain(plate, box):
    """Estimate the scene's film/sensor noise so the paste can carry the same.

    Measured as the residual after a small blur — that isolates high-frequency
    noise from real detail and from the scene's tonal gradient.
    """
    g = plate.convert("L")
    x0, y0, x1, y1 = box
    pad = 40
    crop = (max(0, x0 - pad), max(0, y0 - pad),
            min(g.width, x1 + pad), min(g.height, y1 + pad))
    if crop[2] - crop[0] < 8 or crop[3] - crop[1] < 8:
        return 1.2
    win = g.crop(crop)
    resid = np.asarray(win).astype(float) - np.asarray(
        win.filter(ImageFilter.GaussianBlur(2))).astype(float)
    return float(np.clip(resid.std(), 0.5, 3.5))


def place_file(layout_path, product, out_path, xf, yf, scale,
               direction="left"):
    """Composite into a scene generated with NO product and clear space reserved.

    Nothing to mask and nothing to inpaint, so this cannot leave residue — which is
    why it is the right mode for any ad where the placeholder kept turning into a
    held sign. Position is given as fractions of the frame.
    """
    layout = Image.open(layout_path).convert("RGBA")
    W, H = layout.size
    prod = prep_product(product)
    target_h = int(H * float(np.clip(scale, SCALE_MIN, SCALE_MAX)))
    k = target_h / prod.height
    prod = prod.resize((max(1, int(prod.width * k)), max(1, target_h)), Image.LANCZOS)
    pw, ph = prod.size
    cx, cy = int(W * xf), int(H * yf)

    sh = contact_shadow((W, H), pw, ph, cx, cy, direction)
    black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    base = Image.composite(Image.alpha_composite(layout, black), layout, sh)
    prod = match_scene(prod, base, cx, cy,
                       grain=plate_grain(layout, (cx - pw, cy - ph, cx + pw, cy + ph)))
    base.alpha_composite(prod, (cx - pw // 2, cy - ph // 2))
    base.convert("RGB").save(out_path)
    return True


def composite_file(layout_path, product, out_path, scale=DEFAULT_SCALE,
                   direction="left", shadow=True, match=True, at=None):
    layout = Image.open(layout_path).convert("RGBA")
    strict, box = find_magenta(layout)
    if strict is None:
        layout.convert("RGB").save(out_path)
        return False

    W, H = layout.size
    mask_arr, win = magenta_pixels(layout, box)
    if mask_arr.sum() < 200:
        layout.convert("RGB").save(out_path)
        return False

    ys, xs = np.nonzero(mask_arr)
    l, t, r, b = int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())
    cx, cy = (l + r) // 2, (t + b) // 2

    # 1. remove the placeholder entirely, reconstructing what was behind it
    grown = Image.fromarray((mask_arr * 255).astype(np.uint8)).filter(
        ImageFilter.MaxFilter(7))
    base = inpaint(layout, grown).convert("RGBA")

    # 2. size the tube from the FRAME, not from the box
    prod = prep_product(product)
    target_h = int(H * float(np.clip(scale, SCALE_MIN, SCALE_MAX)))
    k = target_h / prod.height
    prod = prod.resize((max(1, int(prod.width * k)), max(1, target_h)), Image.LANCZOS)
    pw, ph = prod.size
    # `at` overrides where the tube lands. The placeholder's own centroid is not always
    # a good seat: on h02 Pro painted the block floating in front of the pen tray, so
    # inheriting that position hung the tube below the shelf no matter how well the
    # magenta was removed. Position is (x_frac, y_frac) of the frame, of the tube's BASE.
    if at is not None:
        cx = int(W * at[0])
        cy = int(H * at[1]) - ph // 2
    px, py = cx - pw // 2, cy - ph // 2

    # 3. seat it
    shadowed_layout = layout
    if shadow:
        sh = contact_shadow((W, H), pw, ph, cx, cy, direction)
        black = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        base = Image.composite(Image.alpha_composite(base, black), base, sh)
        shadowed_layout = Image.composite(
            Image.alpha_composite(layout, black), layout, sh)

    # 4. match the scene, then paste
    if match:
        prod = match_scene(prod, base, cx, cy, grain=plate_grain(layout, win))
    base.alpha_composite(prod, (px, py))

    # 5. restore only what was genuinely IN FRONT of the placeholder — fingers
    #    crossing it. Those are HOLES inside the magenta shape, not the background
    #    around it. Restoring the whole non-magenta box instead re-imported the
    #    surrounding plate and left a visible rectangular seam where the contact
    #    shadow had been painted and was then overwritten.
    front = holes_inside(mask_arr, win)
    if front.any():
        front_img = Image.fromarray((front * 255).astype(np.uint8)).filter(
            ImageFilter.GaussianBlur(0.8))
        # take the fingers from the SHADOWED plate so the shadow stays continuous
        base = Image.composite(shadowed_layout, base, front_img)

    base.convert("RGB").save(out_path)
    return True


def parse_kv(s, cast=float):
    out = {}
    for part in s.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = cast(v.strip())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--layouts", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--product", default=PRODUCT)
    ap.add_argument("--scale", default="", help="per-ad frame fraction, e.g. h09=0.40,h10=0.26")
    ap.add_argument("--light", default="", help="per-ad key light side, e.g. h02=left")
    ap.add_argument("--default-scale", type=float, default=DEFAULT_SCALE)
    ap.add_argument("--at", default="",
                    help="override paste position for placeholder ads: id=xfrac:ybasefrac")
    ap.add_argument("--place", default="",
                    help="ads with no placeholder: id=xfrac:yfrac:scale, e.g. h09=0.26:0.74:0.34")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    product = Image.open(a.product)
    scales = parse_kv(a.scale)
    lights = parse_kv(a.light, str)

    places = {}
    for part in a.place.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            xf, yf, sc = (float(t) for t in v.split(":"))
            places[k.strip()] = (xf, yf, sc)

    ats = {}
    for part in a.at.split(","):
        if "=" in part:
            k, v = part.split("=", 1)
            ats[k.strip()] = tuple(float(t) for t in v.split(":"))

    done, skipped = [], []
    for fn in sorted(f for f in os.listdir(a.layouts) if f.endswith(".png")):
        ad = fn[:3]
        if ad in places:
            xf, yf, sc = places[ad]
            place_file(os.path.join(a.layouts, fn), product,
                       os.path.join(a.out, fn), xf, yf, sc,
                       direction=lights.get(ad, "left"))
            print(f"  {fn[:26]:28} placed      scale={sc:.2f} at ({xf:.2f},{yf:.2f})")
            done.append(fn)
            continue
        ok = composite_file(os.path.join(a.layouts, fn), product,
                            os.path.join(a.out, fn),
                            scale=scales.get(ad, a.default_scale),
                            direction=lights.get(ad, "left"),
                            at=ats.get(ad))
        if ok:
            print(f"  {fn[:26]:28} composited  scale={scales.get(ad, a.default_scale):.2f}")
            done.append(fn)
        else:
            print(f"  {fn[:26]:28} no placeholder — copied through")
            skipped.append(fn)

    print(f"\n{len(done)} composited -> {a.out}")
    if skipped:
        print("no placeholder: " + ", ".join(s[:3] for s in skipped))


if __name__ == "__main__":
    main()
