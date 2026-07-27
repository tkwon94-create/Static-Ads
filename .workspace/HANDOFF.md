# Handoff to a local Claude Code session

You're continuing work started in a locked web sandbox. Goal: produce **20 winning
static ads** for the LAVENTRA Grow:Turn Ampoule (postpartum & menopause hair-shedding,
US market, 1:1). Everything is already set up in this repo — you just need an
environment that can reach image APIs and download results (this local machine can;
the web sandbox couldn't, which is why this was handed off).

## The one hard problem to solve
Base Nano Banana / Seedream **redraw and garble the product tube's label**. The user has
ONLY a Higgsfield key (no Google/Gemini key), so use the gold-standard composite path,
which needs nothing but Higgsfield:

**PRIMARY PATH — Gold standard, pixel-perfect product (Higgsfield only).**
- `.workspace/gold_standard_ads.py` (needs `pip install pillow`). For each ad it has
  Higgsfield generate ONLY the layout (background + text) with a **magenta placeholder**
  where the product goes — no tube drawn — then downloads it and composites the REAL
  product PNG into that zone. The tube is your exact pixels, never redrawn or re-lettered.
- Uses `HF_API_KEY`/`HF_API_SECRET` only. Model `nano-banana` (or `seedream`).
- IMPORTANT: the magenta-detect/composite step was written but never runnable in the
  sandbox (no image download there). **Test on ad #16 first, view the result, and fix the
  magenta-bbox / scale / background-trim logic as needed** before running all 20. Iterate
  with your own eyes — that's the whole advantage of running locally.
- Remaining weakness: the layout's OWN text (headlines, stat numbers) is still rendered by
  base Nano Banana and may have minor garbling. Regenerate any weak layout (cheap), or
  tighten its prompt. The PRODUCT itself will always be perfect since it's composited.

**Optional upgrade (only if the user later gets a Google key):** Nano Banana Pro via
`GEMINI_API_KEY` + `.claude/skills/winning-statics/scripts/generate_static.py`
(`gemini-3-pro-image-preview`) renders in-layout text far better. Not required — the
gold-standard path already gives a perfect product without it.

## Assets already in the repo
- Product photo (label already corrected to "(V)BioExo-Water(Heartleaf)"):
  `.workspace/inputs/laventra_user_tube.png`
- 20 prompts: `.workspace/laventra_prompts/*.txt` (01–20)
- 50 references: `.claude/skills/winning-statics/references/ref-*.png` (+ LIBRARY.md)
- Ad→reference→prompt mapping: see `.workspace/laventra_batch20v2.py`
- The plan (families, angles, copy) and all protocols: `SKILL.md` + `references/LIBRARY.md`

## Higgsfield API recipe (verified July 2026)
- Auth: `Authorization: Key {key}:{secret}`; a real `User-Agent` header is REQUIRED
  (Cloudflare returns 403/1010 otherwise).
- Image-to-image: `POST /v1/text2image/{model}` with
  `{"params":{"prompt","input_images":[{"type":"image_url","image_url":URL}],"aspect_ratio"}}`
  → returns a job-set; poll `GET /v1/job-sets/{id}`; result at `jobs[0].results.raw.url`.
- input_images must be **public URLs** (data: URIs rejected). Locally you can upload via
  `POST /files/generate-upload-url` (presigned S3 PUT) then use the returned public_url —
  that upload works locally (the sandbox's egress blocked the S3 host).
- Nano Banana **Pro is NOT on Higgsfield** — only base `nano-banana` and `seedream`.
- Full details: `.claude/skills/winning-statics/HIGGSFIELD_SETUP.md`

## Copy/protocol reminders (from the training doc)
- Real reviewer quotes on testimonials (Debra R. etc.), no invented customers.
- Swap the UK regulator badge for real trust (4.8★ / free shipping / easy returns) — never invent badges.
- Realism protocol ON for real humans (natural skin, no smoothing); OFF for illustrated/cartoon refs.
- Verbatim quoted text in prompts; US spelling & $ currency; clinical stats exactly
  (75.61% shedding, 89.04% flakiness, 113.70% hydration).
- QC each output: label fidelity, spelling, structural match, same-person across before/after panels.
