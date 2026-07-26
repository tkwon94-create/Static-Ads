# Gold-Standard Laventra Statics (pixel-perfect product)

This produces the 20 ads with your **real product tube composited in pixel-perfect** —
no AI model ever redraws the tube or its label, so the garbled-label problem is gone.

It must run somewhere images can be downloaded (your own computer or any unrestricted
environment). The web sandbox can't (its firewall blocks the image CDN), which is the
only reason this isn't already done for you.

## Fastest way: run Claude Code locally in this repo
1. On your computer: `git clone` this repo (or `git pull` if you already have it) and
   `git checkout claude/skill-installation-h9wqve`.
2. Open Claude Code in the repo folder and say: "run the gold-standard Laventra batch."
   A local Claude session can download, QC, and composite — and hand you finished files.

## Or run the script yourself
```bash
pip install pillow
export HF_API_KEY=your_key_id
export HF_API_SECRET=your_secret
# product photo = a clean straight-on tube (the one in .workspace/inputs/laventra_user_tube.png works)
python3 .workspace/gold_standard_ads.py \
    --product .workspace/inputs/laventra_user_tube.png \
    --out out/ --model nano-banana
# redo just some:  --only 14,16,20
```
Outputs land in `out/`. Each ad's product is your exact pixels; everything else
(headlines, people, background) is generated. Concepts with no product (#01,#02,#03,#07)
are saved straight from the layout.

## How it works
For each ad the script asks the model to leave a solid magenta placeholder where the
product goes (drawing no tube), downloads the layout, finds the magenta box, and drops
your real product PNG into it — scaled, background-trimmed, centered.
