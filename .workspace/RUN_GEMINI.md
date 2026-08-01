# Running the ad batch on Gemini (Nano Banana Pro) — local machine

The Claude Code sandbox cannot reach `generativelanguage.googleapis.com` (blocked by the
org's egress policy, and environment settings are locked). Gemini therefore has to run on
your own machine. Everything needed is already in this repo.

**Why bother:** Nano Banana Pro renders in-layout text far better than the Higgsfield models
(base `nano-banana` / `seedream`). Every defect that had to be hand-repaired in the delivered
batch — duplicated rows, dropped letters, ghost lines, garbled captions — is a text-rendering
failure that Pro largely avoids. It also accepts local files as references and supports 4:5.

## One-time setup

```bash
git clone <this repo>            # or: git pull
cd Static-Ads
git checkout claude/laventra-static-ads-higgsfield-sumwzb

python3 --version                # 3.9+ ; the script is stdlib-only, no pip installs
export GEMINI_API_KEY='...'      # from aistudio.google.com -> Get API Key
```

Verify access (generates one small image, ~$0.14):

```bash
python3 .claude/skills/winning-statics/scripts/generate_static.py --self-test
```

## Generate one ad

```bash
python3 .claude/skills/winning-statics/scripts/generate_static.py \
  --reference .claude/skills/winning-statics/references/ref-02-claim-stat-strip.png \
  --product   .workspace/inputs/laventra_user_tube.png \
  --prompt-file .workspace/haloven_prompts/h11_dark_hero.txt \
  --aspect-ratio 4:5 \
  --out out/h11_dark_hero.png
```

To recreate a competitor ad **literally**, pass their screenshot as the reference instead:

```bash
  --reference /path/to/haloven_dark_hero.png
```

That is the one thing Higgsfield could not do — it required public URLs, so the delivered
batch used the closest library analogues instead.

## Generate all 12

`.workspace/haloven_ads.py` drives the Higgsfield path. For Gemini, loop the prompts —
ad number, prompt file, reference, aspect ratio are listed in `ADS` inside that script:

```bash
mkdir -p out
while IFS=, read -r num prompt ref ratio; do
  python3 .claude/skills/winning-statics/scripts/generate_static.py \
    --reference ".claude/skills/winning-statics/references/$ref" \
    --product   .workspace/inputs/laventra_user_tube.png \
    --prompt-file ".workspace/haloven_prompts/$prompt.txt" \
    --aspect-ratio "$ratio" \
    --out "out/${num}_${prompt}.png"
done <<'EOF'
h01,h01_quote_hero,ref-40-oversized-quote-lead.png,4:5
h02,h02_whiteboard,ref-38-expert-whiteboard-checklist.png,4:5
h03,h03_test_grid,ref-04-ranked-test-grid.png,1:1
h04,h04_timestamp,ref-30-problem-fix-result.png,4:5
h05,h05_comment_reply,ref-46-story-ama-frame.png,4:5
h06,h06_pov_callouts,ref-25-lifestyle-first-person-overlay.png,4:5
h07,h07_dont_try,ref-47-objection-kill-split.png,1:1
h08,h08_marker,ref-32-hand-drawn-marker-annotation.png,1:1
h09,h09_time_promise,ref-50-benefit-checklist-portrait.png,4:5
h10,h10_selfie_checklist,ref-19-portrait-quote-attribution.png,1:1
h11,h11_dark_hero,ref-02-claim-stat-strip.png,4:5
h12,h12_poster,ref-06-authority-private-notes.png,4:5
EOF
```

Cost: ~$0.13–0.14 per image, so ~$1.70 for the 12, plus retries. Bills your Google key,
not the Higgsfield credits.

## Two differences from the Higgsfield run

1. **No magenta-placeholder compositing.** The Higgsfield path had the model paint a magenta
   block where the product goes, then pasted your real tube in (`.workspace/gold_standard_ads.py`)
   — necessary because base models garbled the label. Pro reproduces a supplied product photo
   much more faithfully, so the prompts here ask for the product directly. **Check the label on
   every output.** If Pro garbles it, reuse the composite pipeline: append the `PLACEHOLDER`
   text from `gold_standard_ads.py` to each prompt, then run `composite()` from that module on
   the result.
2. **4:5 works.** Higgsfield's API rejects it and forced 3:4 on the delivered batch.

## Where things are

| Path | What |
|---|---|
| `.workspace/inputs/laventra_user_tube.png` | product photo, label typo corrected |
| `.workspace/haloven_prompts/` | the 12 competitor-structure prompts (locked hex palette) |
| `.workspace/postpartum_prompts/` | the 10 postpartum-angle prompts |
| `.workspace/laventra_prompts/` | the original 20 prompts |
| `.workspace/out_haloven/` | 12 delivered competitor-structure ads |
| `.workspace/out_postpartum/` | 10 delivered postpartum ads |
| `.workspace/out/` | the original 20 ads |
| `.workspace/gold_standard_ads.py` | magenta-placeholder + composite pipeline |

## Brand palette (already in every prompt)

primary peach `#E8B093` · brand orange `#C14201` · badge orange `#B95618` ·
text `#000000` · product white `#F5F5F6` · background `#FFFFFF`

Pass colors as instructions, never as content — an earlier run printed the hex codes as
visible text in the ads. The prompts already carry the guardrail wording.
