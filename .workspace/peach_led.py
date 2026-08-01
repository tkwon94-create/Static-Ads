#!/usr/bin/env python3
"""Regenerate the ads that carry almost none of the brand peach, with peach as the
dominant ground.

Measured share of pixels near E8B093 in the delivered batch:
    h11 0.2%   h12 3.6%   h01 4.7%   h10 6.6%   h02 8.9%
versus h08 82%, h07 69%, h09 51%. Those five read as a different brand from the site.

Color-correcting them is not an option — they have no peach field to correct. The
ground itself has to be peach, which means the background instruction in each prompt
has to change, and the type contrast has to invert with it (off-white type on a dark
field becomes near-black type on a peach field, or it disappears).

    python3 .workspace/peach_led.py --only h01,h02,h10,h11,h12
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, ".workspace"))
from run_gemini_batch import HALOVEN, REFDIR, GEN, PRODUCT  # noqa: E402
from rerun_placeholder import STRONG  # noqa: E402

PROMPT_DIR = os.path.join(ROOT, ".workspace/haloven_prompts")

# Per-ad ground rewrite. Each entry replaces the background/atmosphere direction
# with one that makes peach the dominant field, and fixes the type contrast that
# depended on the old ground.
GROUND = {
    "h01_quote_hero": """

BRAND GROUND — THIS OVERRIDES THE BACKGROUND AND TYPE COLORS DESCRIBED ABOVE.
The background is NOT dark. Fill the entire frame with a rich, warm peach field —
the brand's primary peach, a soft dusty terracotta-pink, not orange and not brown.
Keep the cinematic lighting: a brighter warm pool of light blooms behind the product
and the peach deepens gently toward the corners, with soft atmospheric haze. Still
dramatic, still premium, but built from light and shadow WITHIN the peach rather
than from darkness.

Because the ground is now light, the type inverts: set the quote in deep near-black
instead of off-white, and set the emphasised middle line in the deep brand orange.
The attribution line beneath is near-black. Peach must be the single most dominant
color in the finished image, covering most of the frame.
""",
    "h02_whiteboard": """

BRAND GROUND — THIS OVERRIDES THE ROOM DESCRIPTION ABOVE.
The room's wall is painted a warm peach — the brand's primary peach, a soft dusty
terracotta-pink. The wall fills the frame behind and around the whiteboard and is the
dominant color of the photograph. Keep the whiteboard itself white, the marker writing
black, the X marks red and the check green, and keep the daylight natural and flat.
Her top is a plain neutral cream or soft grey, never a color that competes with the
wall. Peach must be the single most dominant color in the finished image.
""",
    "h10_selfie_checklist": """

BRAND GROUND — THIS OVERRIDES THE ENVIRONMENT DESCRIPTION ABOVE.
The room she stands in is painted a warm peach — the brand's primary peach, a soft
dusty terracotta-pink — and the light falling through the window is warm, so the
walls, the hallway behind her and the depth of the room all read peach. Keep the
photograph filmic and documentary, keep the real domestic clutter, keep her skin
natural and unretouched. Her sweater is a plain soft cream that sits quietly against
the peach. The quote type stays off-white and must remain clearly legible against the
warmer ground — place it over the deeper, more shadowed part of the wall. Peach must
be the single most dominant color in the finished image.
""",
    "h11_dark_hero": """

BRAND GROUND — THIS OVERRIDES THE BACKGROUND AND TYPE COLORS DESCRIBED ABOVE.
The background is NOT charcoal and NOT dark. Fill the entire frame with the brand's
primary peach — a soft dusty terracotta-pink — as a clean, even, premium field with a
gentle vignette deepening toward the corners. The product sits centered in a soft pool
of slightly brighter light with a clean contact shadow beneath it. Keep the restraint
and the symmetry; the authority now comes from space and precision rather than darkness.

Because the ground is light, every piece of type inverts to deep near-black: the
headline, the small line beneath it, the three stat labels and the bottom trust line.
The thin vertical hairlines between the stat columns are near-black at low opacity.
The small stat icons are near-black line drawings. Peach must be the single most
dominant color in the finished image, covering most of the frame.
""",
    "h12_poster": """

BRAND GROUND — THIS OVERRIDES THE PAPER COLOR DESCRIBED ABOVE.
The sheet is printed on warm peach paper — the brand's primary peach, a soft dusty
terracotta-pink — rather than off-white or parchment. Keep the real paper fiber
texture, the faint aging toward the edges, the binder clip and the soft shadow of a
pinned sheet. All ink on it stays deep near-black: the serif headline, its hand-ruled
underline, the sub-line, the five hand-lettered labels and the curving arrows. The
footer bar stays solid brand orange with white caps text. Peach must be the single
most dominant color in the finished image.
""",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=",".join(sorted(
        {"h01", "h02", "h10", "h11", "h12"})))
    ap.add_argument("--out", default=os.path.join(ROOT, "out_gemini/peach_layouts"))
    ap.add_argument("--no-placeholder", action="store_true")
    ap.add_argument("--retries", type=int, default=2)
    a = ap.parse_args()

    want = {x.strip() for x in a.only.split(",") if x.strip()}
    os.makedirs(a.out, exist_ok=True)
    tmp = os.path.join(a.out, "_prompts")
    os.makedirs(tmp, exist_ok=True)

    ok, failed = [], []
    for num, pf, ref, ratio in HALOVEN:
        if num not in want:
            continue
        if pf not in GROUND:
            print(f"{num}: no peach-led ground written for {pf}, skipping")
            continue

        with open(os.path.join(PROMPT_DIR, f"{pf}.txt")) as f:
            text = f.read().rstrip() + GROUND[pf]
        if not a.no_placeholder:
            text += STRONG
        ppath = os.path.join(tmp, f"{num}.txt")
        with open(ppath, "w") as f:
            f.write(text)

        out_path = os.path.join(a.out, f"{num}_{pf}.png")
        cmd = [sys.executable, GEN,
               "--reference", os.path.join(REFDIR, ref),
               "--product", PRODUCT,
               "--prompt-file", ppath,
               "--aspect-ratio", ratio,
               "--out", out_path]
        for attempt in range(1, a.retries + 1):
            print(f"{num} {pf} ({ratio}) peach-led  attempt {attempt}/{a.retries} ...")
            if subprocess.call(cmd) == 0:
                ok.append(num)
                break
        else:
            failed.append(num)

    print(f"\ngenerated: {', '.join(ok) or 'none'}")
    if failed:
        print(f"failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
