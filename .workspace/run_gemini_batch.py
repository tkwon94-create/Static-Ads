#!/usr/bin/env python3
"""Run a whole ad batch through Gemini (Nano Banana Pro) on your own machine.

The Claude Code sandbox cannot reach generativelanguage.googleapis.com, so this is
the local driver. Stdlib only — no pip installs.

Setup:
    export GEMINI_API_KEY='...'            # aistudio.google.com -> Get API Key
    python3 .workspace/run_gemini_batch.py --self-test

Run the competitor-structure batch (12 ads, ~$1.70):
    python3 .workspace/run_gemini_batch.py --batch haloven

Use the real competitor screenshots as references instead of the library analogues —
this is the thing Higgsfield could not do. Put their PNGs in a folder named by ad id
(h01.png, h02.png, ...) and point at it:
    python3 .workspace/run_gemini_batch.py --batch haloven --refs-dir ~/haloven_ads

Other batches:
    --batch postpartum      10 postpartum-angle ads
    --batch original        the original 20

Useful flags:
    --only h03,h11          just these ads
    --out DIR               output directory (default: out_gemini/<batch>)
    --retries N             attempts per ad (default 2)
    --placeholder           product as magenta placeholder, for compositing later
                            (use only if Pro garbles the tube label)
"""
import argparse
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, ".claude/skills/winning-statics/scripts/generate_static.py")
REFDIR = os.path.join(ROOT, ".claude/skills/winning-statics/references")
PRODUCT = os.path.join(ROOT, ".workspace/inputs/laventra_user_tube.png")

# id, prompt file (without .txt), reference filename, aspect ratio
HALOVEN = [
    ("h01", "h01_quote_hero",      "ref-40-oversized-quote-lead.png",           "4:5"),
    ("h02", "h02_whiteboard",      "ref-38-expert-whiteboard-checklist.png",    "4:5"),
    ("h03", "h03_test_grid",       "ref-04-ranked-test-grid.png",               "1:1"),
    ("h04", "h04_timestamp",       "ref-30-problem-fix-result.png",             "4:5"),
    ("h05", "h05_comment_reply",   "ref-46-story-ama-frame.png",                "4:5"),
    ("h06", "h06_pov_callouts",    "ref-25-lifestyle-first-person-overlay.png", "4:5"),
    ("h07", "h07_dont_try",        "ref-47-objection-kill-split.png",           "1:1"),
    ("h08", "h08_marker",          "ref-32-hand-drawn-marker-annotation.png",   "1:1"),
    ("h09", "h09_time_promise",    "ref-50-benefit-checklist-portrait.png",     "4:5"),
    ("h10", "h10_selfie_checklist","ref-19-portrait-quote-attribution.png",     "1:1"),
    ("h11", "h11_dark_hero",       "ref-02-claim-stat-strip.png",               "4:5"),
    ("h12", "h12_poster",          "ref-06-authority-private-notes.png",        "4:5"),
]

POSTPARTUM = [
    ("p01", "p01_anatomy",   "ref-49-shock-education-split.png",          "1:1"),
    ("p02", "p02_follicle",  "ref-22-visceral-organ-concern.png",         "1:1"),
    ("p03", "p03_blame",     "ref-01-two-figure-blame-reframe.png",       "1:1"),
    ("p04", "p04_ama",       "ref-40-oversized-quote-lead.png",           "1:1"),
    ("p05", "p05_postit",    "ref-14-post-it-handwritten-note.png",       "1:1"),
    ("p06", "p06_portrait",  "ref-19-portrait-quote-attribution.png",     "1:1"),
    ("p07", "p07_editorial", "ref-03-cultural-secret-long-headline.png",  "1:1"),
    ("p08", "p08_lifestyle", "ref-25-lifestyle-first-person-overlay.png", "1:1"),
    ("p09", "p09_stat",      "ref-02-claim-stat-strip.png",               "1:1"),
    ("p10", "p10_cooling",   "ref-39-sensory-fear-claim.png",             "1:1"),
]

ORIGINAL = [
    ("01", "01_anatomy",        "ref-09-anatomy-self-diagnosis.png",          "1:1"),
    ("02", "02_follicle_concern","ref-22-visceral-organ-concern.png",         "1:1"),
    ("03", "03_flashlight",     "ref-31-flashlight-label-expose.png",         "1:1"),
    ("04", "04_blame_reframe",  "ref-01-two-figure-blame-reframe.png",        "1:1"),
    ("05", "05_staged_timeline","ref-10-staged-transformation-timeline.png",  "1:1"),
    ("06", "06_lineart",        "ref-44-line-art-progress-map.png",           "1:1"),
    ("07", "07_daygrid",        "ref-11-day-stamped-healing-grid.png",        "1:1"),
    ("08", "08_split",          "ref-15-split-face-comparison.png",           "1:1"),
    ("09", "09_testimonial",    "ref-19-portrait-quote-attribution.png",      "1:1"),
    ("10", "10_postit",         "ref-14-post-it-handwritten-note.png",        "1:1"),
    ("11", "11_ama",            "ref-46-story-ama-frame.png",                 "1:1"),
    ("12", "12_complement",     "ref-41-complement-table.png",                "1:1"),
    ("13", "13_whiteboard",     "ref-38-expert-whiteboard-checklist.png",     "1:1"),
    ("14", "14_callout",        "ref-12-formula-callout-x-pattern.png",       "1:1"),
    ("15", "15_reasons",        "ref-42-numbered-reasons-why.png",            "1:1"),
    ("16", "16_claim_stat",     "ref-02-claim-stat-strip.png",                "1:1"),
    ("17", "17_typescale",      "ref-36-type-scale-contrast-claim.png",       "1:1"),
    ("18", "18_price",          "ref-13-price-anchor-slash.png",              "1:1"),
    ("19", "19_editorial",      "ref-03-cultural-secret-long-headline.png",   "1:1"),
    ("20", "20_checklist",      "ref-50-benefit-checklist-portrait.png",      "1:1"),
]

BATCHES = {
    "haloven":    (HALOVEN,    ".workspace/haloven_prompts"),
    "postpartum": (POSTPARTUM, ".workspace/postpartum_prompts"),
    "original":   (ORIGINAL,   ".workspace/laventra_prompts"),
}

# Appended when --placeholder is used: reproduces the Higgsfield-era composite path,
# where the model leaves a magenta block and the real tube is pasted in afterwards.
PLACEHOLDER = (
    "\n\nPRODUCT PLACEHOLDER — IMPORTANT: Do NOT draw the product tube or any product at "
    "all. In the exact position, size, and orientation where the product should appear, "
    "paint a single SOLID FLAT pure magenta shape (maximum red, zero green, maximum blue; "
    "no gradient, no text, no shadow on it). Render everything else — headlines, body text, "
    "people, icons, background — normally and completely. The magenta shape must be the only "
    "magenta in the whole image. Never write any color name or hex code as visible text.\n"
)


def check_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        sys.exit("GEMINI_API_KEY is not set.\n"
                 "  export GEMINI_API_KEY='...'   # aistudio.google.com -> Get API Key")
    return key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", choices=sorted(BATCHES), default="haloven")
    ap.add_argument("--only", default="", help="comma-separated ad ids, e.g. h03,h11")
    ap.add_argument("--out", default="")
    ap.add_argument("--refs-dir", default="",
                    help="folder of your own reference images named <id>.png (e.g. h01.png)")
    ap.add_argument("--retries", type=int, default=2)
    ap.add_argument("--placeholder", action="store_true",
                    help="magenta placeholder instead of the product (composite it in later)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    check_key()

    if a.self_test:
        sys.exit(subprocess.call([sys.executable, GEN, "--self-test"]))

    ads, prompt_dir = BATCHES[a.batch]
    prompt_dir = os.path.join(ROOT, prompt_dir)
    out_dir = a.out or os.path.join(ROOT, "out_gemini", a.batch)
    os.makedirs(out_dir, exist_ok=True)
    only = {x.strip() for x in a.only.split(",") if x.strip()}

    todo = [ad for ad in ads if not only or ad[0] in only]
    print(f"batch={a.batch}  ads={len(todo)}  out={out_dir}")
    print(f"estimated cost ~${0.14 * len(todo):.2f} (plus retries)\n")

    ok, failed = [], []
    for num, pf, ref, ratio in todo:
        # your own screenshot wins over the bundled library reference
        reference = os.path.join(a.refs_dir, f"{num}.png") if a.refs_dir else ""
        if not (reference and os.path.exists(reference)):
            reference = os.path.join(REFDIR, ref)

        prompt_path = os.path.join(prompt_dir, f"{pf}.txt")
        if not os.path.exists(prompt_path):
            print(f"{num}: missing prompt {prompt_path}"); failed.append(num); continue

        if a.placeholder:
            with open(prompt_path) as f:
                text = f.read() + PLACEHOLDER
            prompt_path = os.path.join(out_dir, f".{num}_prompt.txt")
            with open(prompt_path, "w") as f:
                f.write(text)

        out_path = os.path.join(out_dir, f"{num}_{pf}.png")
        cmd = [sys.executable, GEN,
               "--reference", reference,
               "--product", PRODUCT,
               "--prompt-file", prompt_path,
               "--aspect-ratio", ratio,
               "--out", out_path]

        for attempt in range(1, a.retries + 1):
            print(f"{num} {pf} ({ratio})  attempt {attempt}/{a.retries} ...")
            if subprocess.call(cmd) == 0:
                print(f"  -> {out_path}")
                ok.append(num)
                break
        else:
            print(f"  !! {num} failed after {a.retries} attempts")
            failed.append(num)

    print(f"\ndone. {len(ok)} generated -> {out_dir}")
    if failed:
        print("failed: " + ",".join(failed))
        print(f"retry with: --only {','.join(failed)}")
    print("\nQC every image before spending: product label fidelity, exact spelling of every "
          "quoted line, no duplicated or ghost text, no leaked hex codes.")
    if a.placeholder:
        print("Placeholder mode: composite the real tube with composite() in "
              ".workspace/gold_standard_ads.py")


if __name__ == "__main__":
    main()
