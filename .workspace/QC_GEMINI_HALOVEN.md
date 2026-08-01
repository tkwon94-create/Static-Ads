# QC report — competitor-structure batch rebuilt on Nano Banana Pro

Output: `out_gemini/haloven/` (12 ads) · contact sheet: `out_gemini/haloven_grid.png`
Variants for a flagged ad: `out_gemini/haloven_flagged/`

## Headline result

**Layout text is letter-perfect on all 12.** Every headline, chip, callout, caption,
handwritten line and trust bar matches its prompt exactly and appears exactly once.
Zero duplicated rows, zero ghost lines, zero dropped letters, zero leaked hex codes.
That is the defect class that forced hand-repair on every Higgsfield ad, and it did
not occur once here — including h02, where a human presenter and eleven separate
handwritten strings share one whiteboard.

The remaining defects are all in the **product label** or in **compositing**, not in
the ad copy.

## Per-ad status

| Ad | Layout text | Product label | Status |
|---|---|---|---|
| h01 quote hero | exact | real pixels | clean |
| h02 whiteboard | exact | real pixels | clean |
| h03 test grid | exact | real pixels | clean |
| h04 timestamp | exact | real pixels | clean |
| h05 comment reply | exact | model-drawn, accurate | clean |
| h06 pov callouts | exact | model-drawn, **garbled** | **flagged** |
| h07 don't try | exact | real pixels | clean |
| h08 marker | exact | real pixels | clean |
| h09 time promise | exact | real pixels | clean |
| h10 portrait quote | exact | real pixels | **flagged** (smear) |
| h11 dark hero | exact | model-drawn, **3 typos** | **flagged** |
| h12 poster | exact | real pixels | clean |

9 clean, 3 flagged.

## The three flagged ads

**h06 — label microcopy garbled.** The ad itself is one of the strongest in the
batch: ref-25's warm morning light, steam off the mug, four exact callouts. But the
tube is model-drawn and its small print reads `(31)BlbExe WaterHeartleaf)` and
`3DKLF CLERA`. The placeholder route was tried and produced a worse result (a large
pink shape surviving next to a badly-placed tube), so this is the better of two
imperfect versions. Illegible at feed size, wrong at full size.

**h10 — real label, but a composite smear.** Best casting in the batch: a genuine
30-year-old in a real nursery, unretouched, every line exact. The tube is the real
photo and the label is pixel-perfect. But a reddish-brown smear sits under the brush
tip across her hands, left where the crimson placeholder blended into her sweater.
Regenerated more than twice; per the standing QC rule I stopped and flagged rather
than spend further. Both candidates are kept in `out_gemini/haloven_flagged/`:
- `h10_shipped_composited.png` — correct label, smear under the tip (shipped)
- `h10_ALT_direct_render.png` — clean photo, but an **invented label** with a
  decorative medallion that is not the real product

**h11 — three label typos.** `ingredienta`, `seslp`, and the closing paren of
`(V)BioExo-Water` rendered as `J`. Everything else — headline, stat strip, trust
line, dramatic lighting — is clean. A placeholder rerun was attempted and failed
badly (cropped tube, and the words `PIII badged` printed onto the label as leaked
instruction text), so the direct render is kept.

## What changed in the pipeline

- **Prompts rebuilt** (`build_haloven_prompts.py`). No hex code appears in any
  layout body now — the old prompts wrote `#C14201` as an instruction while the
  footer forbade rendering hex codes. Added a per-ad ATMOSPHERE block written from
  looking at each reference. Removed h02's stale magenta-placeholder line, h09's
  "Based on clinical testing." (a lab claim) and h04's guarantee-shaped
  "OR EASY RETURNS".
- **Compositing** (`composite_gemini.py`). Three bugs found and fixed by measurement:
  1. The strict magenta mask missed *shaded* placeholder pixels → purple bruise on h08.
  2. A widened global hue mask then erased h02's red X marks — red ink at b/r 0.46
     overlaps crimson placeholder at b/r 0.53, so no global threshold separates them.
     Fixed by confining the sweep to the placeholder's own bounding box.
  3. Clearing the whole box fixes h10 but smears detail elsewhere (it wiped h03's
     winner cell and ate part of h10's own bottom trust line), so it is opt-in
     per ad via `--fullbox`, never global.

## Still open

- Copy on h01, h05 and h10 is assistant-written first-person, not real reviews —
  unchanged from the previous handoff, still needs your approval.
- The Gemini key was pasted into an earlier chat and now has billing attached.
  Worth rotating.
