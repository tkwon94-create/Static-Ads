#!/usr/bin/env python3
"""Re-run specific haloven ads with a placeholder instruction strong enough to
survive prompts where the tube is held, gripped, or sits inside a photo cell.

The generic PLACEHOLDER text in run_gemini_batch.py says "do not draw the product,
paint a magenta shape instead". In prompts that describe a hand holding the tube,
Nano Banana Pro resolves that conflict in favour of the hand and draws the product
anyway — which is why h03, h05 and h06 came back with no magenta zone and
model-drawn labels.

This variant restates the rule in terms of the held object itself, and repeats it
at the very end of the prompt where it is least likely to be diluted.

    python3 .workspace/rerun_placeholder.py --only h03,h05,h06,h11
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, ".workspace"))
from run_gemini_batch import HALOVEN, REFDIR, GEN, PRODUCT  # noqa: E402

PROMPT_DIR = os.path.join(ROOT, ".workspace/haloven_prompts")

STRONG = """

PRODUCT PLACEHOLDER — THIS RULE OVERRIDES EVERY OTHER INSTRUCTION ABOUT THE PRODUCT.
Do NOT draw the product tube. Do NOT draw its label, its wordmark, its badge, its
brush tip or any writing on it. Wherever the description above says the product
appears — including when it is held in a hand, gripped by fingers, resting on a
surface or sitting inside a photo cell — instead paint a SINGLE SOLID FLAT PURE
MAGENTA RECTANGLE occupying exactly that position, size and orientation.

SHAPE — this matters as much as the color. The rectangle must be UPRIGHT and TALLER
THAN IT IS WIDE, in the proportion 4 wide by 5 tall, matching the tube it stands in
for. Do not make it square, do not make it wide, do not make it fill more area than
the tube itself would. Anything the rectangle covers beyond the tube's own outline
has to be reconstructed afterwards and will show as a smear.

Pure magenta means maximum red, zero green, maximum blue. Absolutely flat: no
gradient, no shading, no highlight, no reflection, no mirrored image in a glossy
surface, no drop shadow, no contact shadow, no text and no texture on or under it.
Its edges are hard and clean. Surfaces near it — counters, tables, tiles — stay their
own natural color and reflect nothing.

If a hand appears, the hand grips the magenta rectangle exactly as it would grip
the tube — fingers wrapping its edges naturally — but the object itself is nothing
but flat magenta. Render the hand, the person, the environment, all headlines, all
body text, all chips, icons and bars normally and completely.

This magenta rectangle must be the only magenta anywhere in the image. Nothing else
in the frame may be magenta, pink, purple or violet.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "out_gemini/haloven_layouts"))
    ap.add_argument("--retries", type=int, default=2)
    a = ap.parse_args()

    want = {x.strip() for x in a.only.split(",") if x.strip()}
    os.makedirs(a.out, exist_ok=True)
    tmp = os.path.join(a.out, "_strong")
    os.makedirs(tmp, exist_ok=True)

    ok, failed = [], []
    for num, pf, ref, ratio in HALOVEN:
        if num not in want:
            continue
        with open(os.path.join(PROMPT_DIR, f"{pf}.txt")) as f:
            text = f.read().rstrip() + STRONG
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
            print(f"{num} {pf} ({ratio})  attempt {attempt}/{a.retries} ...")
            if subprocess.call(cmd) == 0:
                ok.append(num)
                break
        else:
            failed.append(num)

    print(f"\nregenerated: {', '.join(ok) or 'none'}")
    if failed:
        print(f"failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
