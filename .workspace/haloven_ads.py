#!/usr/bin/env python3
"""Haloven-structure recreations for Laventra. Same gold-standard pipeline
(magenta placeholder layout -> composite the real tube), with per-ad aspect
ratios matching the competitor originals."""
import argparse, os, sys, io, time, importlib.util
spec = importlib.util.spec_from_file_location("gsa", os.path.join(os.path.dirname(__file__), "gold_standard_ads.py"))
gsa = importlib.util.module_from_spec(spec); spec.loader.exec_module(gsa)
from PIL import Image

# num, prompt file, reference, uses_product, aspect_ratio
ADS = [
 ("h01","h01_quote_hero",     "ref-40-oversized-quote-lead.png",        True, "3:4"),
 ("h02","h02_whiteboard",     "ref-38-expert-whiteboard-checklist.png", True, "3:4"),
 ("h03","h03_test_grid",      "ref-04-ranked-test-grid.png",            True, "1:1"),
 ("h04","h04_timestamp",      "ref-30-problem-fix-result.png",          True, "3:4"),
 ("h05","h05_comment_reply",  "ref-46-story-ama-frame.png",             True, "3:4"),
 ("h06","h06_pov_callouts",   "ref-25-lifestyle-first-person-overlay.png", True, "3:4"),
 ("h07","h07_dont_try",       "ref-47-objection-kill-split.png",        True, "1:1"),
 ("h08","h08_marker",         "ref-32-hand-drawn-marker-annotation.png", True, "1:1"),
 ("h09","h09_time_promise",   "ref-50-benefit-checklist-portrait.png",  True, "3:4"),
 ("h10","h10_selfie_checklist","ref-19-portrait-quote-attribution.png", True, "1:1"),
 ("h11","h11_dark_hero",      "ref-02-claim-stat-strip.png",            True, "3:4"),
 ("h12","h12_poster",         "ref-06-authority-private-notes.png",     True, "3:4"),
]

def gen(num, pf, ref, usep, ar, model, k, s, extra):
    prompt = open(f".workspace/haloven_prompts/{pf}.txt").read()
    if usep: prompt += gsa.PLACEHOLDER
    if extra: prompt += "\n\n" + extra
    body = {"params": {"prompt": prompt,
            "input_images": [{"type": "image_url", "image_url": f"{gsa.RAW}/{gsa.REFDIR}/{ref}"}],
            "aspect_ratio": ar}}
    js = gsa.api("POST", f"{gsa.BASE}/v1/text2image/{model}", k, s, body); sid = js["id"]
    for _ in range(120):
        time.sleep(5)
        st = gsa.api("GET", f"{gsa.BASE}/v1/job-sets/{sid}", k, s); job = st["jobs"][0]
        if job["status"] == "completed": return gsa.download(job["results"]["raw"]["url"])
        if job["status"] in ("failed", "nsfw"):
            print(f"  {num} layout {job['status']}"); return None
    print(f"  {num} timeout"); return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", default=".workspace/inputs/laventra_user_tube.png")
    ap.add_argument("--out", default=".workspace/out_hv")
    ap.add_argument("--model", default="seedream")
    ap.add_argument("--only", default="")
    ap.add_argument("--extra", default="")
    a = ap.parse_args()
    k, s = gsa.creds(); os.makedirs(a.out, exist_ok=True)
    product = Image.open(a.product)
    only = set(x.strip() for x in a.only.split(",") if x.strip())
    for num, pf, ref, usep, ar in ADS:
        if only and num not in only: continue
        print(f"{num} {pf} ({ar}) ...")
        layout = gen(num, pf, ref, usep, ar, a.model, k, s, a.extra)
        if layout is None: continue
        ldir = os.path.join(a.out, "layouts"); os.makedirs(ldir, exist_ok=True)
        open(os.path.join(ldir, f"{num}_{pf}.layout.png"), "wb").write(layout)
        out = os.path.join(a.out, f"laventra_{num}_{pf}.png")
        if usep:
            ok = gsa.composite(layout, product, out)
            print(f"  saved {out} ({'product composited' if ok else 'NO magenta zone'})")
        else:
            Image.open(io.BytesIO(layout)).convert("RGB").save(out); print(f"  saved {out}")
    print("done ->", a.out)

if __name__ == "__main__":
    main()
