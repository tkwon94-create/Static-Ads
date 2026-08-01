# Handoff — Laventra static ads, continuing on Gemini

Read this first, then `.workspace/RUN_GEMINI.md` for the local runbook.

## Where the work stands

**54 finished ads are delivered and committed.** Nothing is lost or pending.

| Folder | Count | What | Engine |
|---|---|---|---|
| `.workspace/out/` | 20 | Original batch, 9 concept families, 1:1 | Higgsfield |
| `.workspace/out_postpartum/` | 10 | Postpartum-angle batch, 1:1 | Higgsfield |
| `.workspace/out_haloven/` | 12 | Competitor-structure batch, 1:1 + 3:4 | Higgsfield |
| `out_gemini/haloven/` | 12 | **Competitor-structure batch rebuilt** | Nano Banana Pro |

The Gemini rebuild of the competitor batch is done: 9 clean, 3 flagged. Read
`.workspace/QC_GEMINI_HALOVEN.md` for the per-ad verdict. Layout text came back
letter-perfect on all 12 — the defect class that forced hand-repair on every
Higgsfield ad did not occur once. Every remaining defect is in the product label
or in compositing, not the copy.

Matching prompts live in `.workspace/laventra_prompts/`, `.workspace/postpartum_prompts/`,
`.workspace/haloven_prompts/`. Review grids: `.workspace/*_review_grid.png`.

## The product

`.workspace/inputs/laventra_user_tube.png` — LAVENTRA GROW:TURN AMPOULE, a white squeeze
tube with a built-in comb/brush tip. The ingredient line was corrected to read
"(V)BioExo-Water(Heartleaf)"; the pre-fix original is kept as `laventra_user_tube_TYPO_BACKUP.png`.
In every delivered ad the tube is the user's real pixels, composited in — never model-drawn.

## Brand and strategy (settled with the user, do not re-litigate)

- **Palette, exact hex:** primary peach `#E8B093`, brand orange `#C14201`, badge orange
  `#B95618`, text `#000000`, product white `#F5F5F6`, background `#FFFFFF`.
  Pass these as painting instructions, never as content — an early run printed the codes as
  visible text in the ads. The prompts already carry guardrail wording; keep it.
- **Primary demographic: postpartum moms, ~27–38.** Derived from the user's own site
  (trylaventra.shop) — the copy names postpartum shedding, the first FAQ is about
  breastfeeding safety, discovery is TikTok-native, and every face on the page is that age.
  Menopause converts on proof but the page under-serves her.
- **One enemy, in every ad:** the masking kit — dry shampoo, volume powder, root spray,
  buns/hats, biotin gummies.
- **One emotional stake:** the shower-drain dread / feeling like herself again. Sell the
  second-order feeling, not the attribute.
- **Spine:** problem relocation — "Your hair isn't the problem. Your scalp is."
- **Trust language is vague-but-safe by the user's choice:** "4.8★ rated", "Thousands of new
  moms", "Free shipping", "Easy returns". No review counts, no guarantee term, no lab or
  provenance claims. Competitors always genericized.

## Open items

1. **Rotate both API keys.** The Higgsfield key and a Gemini key were pasted into the prior
   chat (the Gemini one also appears in a screenshot). Treat both as compromised.
2. **Copy the user still needs to approve** — first-person lines written by the assistant, not
   real reviews: `h01`, `h05`, `h10`, and postpartum `p04`, `p08`.
3. **Site claim conflict:** the hero badge says "2381+ Reviews" but the widget shows 21. Also
   the site misspells "Heartleaf Exomes" (should be exosomes). Both are the user's to fix.
4. **Human-featuring formats are the fragile ones.** Selfies, portraits and long caption text
   repeatedly came back garbled or with subjects ~20 years older than briefed on the
   Higgsfield models. Specifying an age as a number ("aged 30") worked better than a
   description. This is the main thing Nano Banana Pro is expected to improve.

## What's next: rebuild on Gemini (Nano Banana Pro)

Why: Pro renders in-layout text far better. Every defect that needed hand-repair in the
delivered batches — duplicated rows, dropped letters, ghost lines, garbled captions — is a
text-rendering failure. Pro also takes local files as references and supports 4:5.

**There is no egress blocker. Do not repeat this mistake.** An earlier handoff claimed
the sandbox could not reach `generativelanguage.googleapis.com`. It can. The bare URL
returns 403 because Google requires an API key — `"Method doesn't allow unregistered
callers"` — not because the proxy refuses CONNECT. Test with the key in the header:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models      # 200
```

Image models also need billing enabled on the key's project; on free tier they return
429 with `limit: 0`, which never clears by waiting.

**To run:**

```bash
export GEMINI_API_KEY='...'
python3 .workspace/run_gemini_batch.py --self-test           # ~$0.14
python3 .workspace/run_gemini_batch.py --batch haloven       # 12 ads, ~$1.70
```

Add `--refs-dir <folder>` with the user's own competitor screenshots named `h01.png`,
`h02.png`, … to do literal 1:1 recreations. That was impossible on Higgsfield, which only
accepts public URLs — the delivered batch used the closest library analogues instead.

Pro does garble the tube label, worse the smaller the tube sits in frame, so the
placeholder-plus-composite path is the default rather than a fallback. Full mechanics,
including when the strong-placeholder variant is needed and when it backfires, are in
`.workspace/RUN_GEMINI.md`.

## What's next

1. **Rebuild the postpartum 10 on Gemini** — same command, `--batch postpartum`.
2. **Rebuild the original 20 on Gemini** — `--batch original`.
3. **A genuinely new batch** — 21 of the library's 50 references are still unused by any
   batch (05, 07, 08, 16, 17, 18, 20, 21, 23, 24, 26, 27, 28, 29, 33, 34, 35, 37, 43,
   45, 48), so a fresh set is possible without repeating a single structure. Note the
   library's own rule: never serve ref-26 alongside ref-10, which the original batch used.
4. **Resolve the three flagged competitor ads** (h06, h10, h11) — see the QC report.

## QC standard to hold

Inspect every generated image before showing the user. Check: product label fidelity against
the real photo, every quoted string letter-perfect and appearing exactly once, no duplicated
or ghost text, no leaked hex codes, no reference-ad contamination (other brands' words,
products or badges bleeding through), realistic skin on humans, correct subject age.
Regenerate up to twice, then repair deterministically with Pillow, then flag honestly rather
than shipping something broken.
