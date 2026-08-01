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


def sweep_box(img, mask, box, margin=26, full=False):
    """Loosely sweep placeholder-colored pixels, but ONLY inside the placeholder's
    own bounding box (plus a margin, and the band beneath it where a reflection
    falls). Everything outside that window is left alone.

    A global color test cannot do this job. Nano Banana Pro paints the placeholder
    anywhere from pure magenta to a dark crimson — h10's measured (145,25,78),
    b/r = 0.53 — while h02's red dry-erase X marks measure b/r = 0.46 median.
    The two ranges overlap, so any threshold loose enough to clear h10's crimson
    also erases h02's X marks (which is exactly what happened). Confining the
    sweep to the box find_magenta already located removes the conflict: the X
    marks are nowhere near the tube, so they are never considered.
    """
    im = img.convert("RGB")
    px = im.load()
    W, H = im.size
    mp = mask.load()
    l, t, r, b = box
    x0, x1 = max(0, l - margin), min(W - 1, r + margin)
    y0 = max(0, t - margin)
    y1 = min(H - 1, b + int((b - t) * 0.55) + margin)

    # Default: sweep pink/magenta/crimson hues only — red and blue both above
    # green. This is right for almost every ad and leaves the scene intact.
    #
    # full=True instead clears the entire box. Needed only where the placeholder
    # blended into a warm subject and left residue no magenta test can see: on
    # h10 the crimson bled into a brown sweater and came back reddish-brown, blue
    # BELOW green. Clearing the box fixes that but costs real detail — it smeared
    # the winner cell on h03 — so it stays opt-in per ad, never global.
    if full:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                mp[x, y] = 255

    for y in range(max(0, y0 - margin), min(H, y1 + margin)):
        for x in range(max(0, x0 - margin), min(W, x1 + margin)):
            cr, cg, cb = px[x, y]
            if (cr - cg) >= 12 and (cb - cg) >= 8:
                mp[x, y] = 255
    return mask.filter(ImageFilter.MaxFilter(9 if not full else 5))


def magenta_mask(img, pad=20):
    """Mask every magenta/purple pixel at ANY lightness, plus a margin.

    gold_standard_ads.find_magenta thresholds on saturated magenta and sweeps up
    only *light* pink shading (it requires r>170). Nano Banana Pro shades the
    placeholder block, so the dark side of it — and the cast shadow the model
    draws under it — survived and left a purple bruise under the brush tip on h08.

    The whole brand palette is safe against a two-sided hue test: peach, brand
    orange and badge orange all have blue BELOW green (E8B093 -> b-g = -29,
    C14201 -> -65), while magenta and purple have blue and red both ABOVE green.

    But "blue and red both above green" alone is NOT enough. A red dry-erase X on
    h02's whiteboard measures roughly r-g = 140, b-g = 20 — it clears a loose
    (b-g) > 18 bar, and a global mask duly erased all three X marks. The
    distinguishing property is that magenta has blue roughly EQUAL to red, while
    any red or pink ink has blue far below red. So the test also demands a high
    blue floor relative to red, which the X marks fail and shaded magenta passes.
    """
    im = img.convert("RGB")
    px = im.load()
    W, H = im.size
    m = Image.new("L", (W, H), 0)
    mp = m.load()
    hits = 0
    for y in range(H):
        for x in range(W):
            r, g, b = px[x, y]
            if ((r - g) > 25 and (b - g) > 40 and b >= 0.55 * r
                    and max(r, g, b) > 40):
                mp[x, y] = 255
                hits += 1
    if hits < (W * H) // 4000:
        return None
    # grow generously so anti-aliased fringes and the drawn contact shadow go too
    return m.filter(ImageFilter.MaxFilter(2 * (pad // 2) + 1))

PRODUCT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       ".workspace/inputs/laventra_user_tube.png")


def add_reflection(img, mask, box, margin=24):
    """Sweep up the placeholder's washed-out reflection on glossy surfaces.

    On h04 the tube sits on a polished bathroom counter and the model dutifully
    reflected the magenta block in it. A reflection is magenta blended toward the
    surface, so it lands far below the hue threshold that catches the block itself
    — it survived as a pink triangle under the brush tip.

    Chasing it with a lower global threshold is not safe: the red "7:12 AM" chip
    measures b-g = 6 and would be eaten too. So this pass is confined to the
    placeholder's own neighbourhood (plus the band beneath it, where a reflection
    falls) and additionally rejects saturated reds — a reflection is desaturated,
    the chip is not (r-g = 105).
    """
    im = img.convert("RGB")
    px = im.load()
    W, H = im.size
    mp = mask.load()
    l, t, r, b = box
    x0, x1 = max(0, l - margin), min(W - 1, r + margin)
    y0 = max(0, t - margin)
    y1 = min(H - 1, b + int((b - t) * 0.6) + margin)   # reflections fall downward

    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cr, cg, cb = px[x, y]
            # desaturated, and blue must sit close to red — a pink reflection
            # does, red ink does not (same trap that erased h02's X marks)
            if ((cr - cg) >= 5 and (cb - cg) >= 5 and (cr - cg) < 60
                    and cb >= 0.7 * cr):
                mp[x, y] = 255
    return mask.filter(ImageFilter.MaxFilter(7))


def composite_file(layout_path, product, out_path, pad=0.0, full=False):
    """Paste `product` into the magenta zone of `layout_path`. Returns True on success."""
    layout = Image.open(layout_path).convert("RGBA")
    mask, box = find_magenta(layout)
    if mask is None:
        layout.convert("RGB").save(out_path)
        return False

    l, t, r, b = box
    bw, bh = r - l + 1, b - t + 1

    # Sweep the placeholder's own neighbourhood loosely — shaded body, soft
    # fringe and glossy reflection all go — without touching red ink elsewhere.
    mask = sweep_box(layout, mask, box, full=full)
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
    ap.add_argument("--fullbox", default="",
                    help="comma-separated ad ids to clear the whole placeholder box for")
    ap.add_argument("--pad", type=float, default=0.0,
                    help="fractional inset inside the placeholder box, e.g. 0.06")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    product = Image.open(a.product)

    full_ids = {x.strip() for x in a.fullbox.split(",") if x.strip()}
    done, missing = [], []
    for fn in sorted(os.listdir(a.layouts)):
        if not fn.lower().endswith(".png"):
            continue
        src = os.path.join(a.layouts, fn)
        dst = os.path.join(a.out, fn)
        use_full = any(fn.startswith(i) for i in full_ids)
        if composite_file(src, product, dst, a.pad, use_full):
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
