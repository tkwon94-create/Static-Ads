# Handoff to a local Claude Code session

You're continuing work started in a locked web sandbox. Goal: produce **20 winning
static ads** for the LAVENTRA Grow:Turn Ampoule (postpartum & menopause hair-shedding,
US market, 1:1). Everything is already set up in this repo — you just need an
environment that can reach image APIs and download results (this local machine can;
the web sandbox couldn't, which is why this was handed off).

## The one hard problem to solve
Base Nano Banana / Seedream **redraw and garble the product tube's label**. Two good fixes,
both work locally:

**Option A — Nano Banana Pro (recommended, best all-round quality).**
- Get a Google AI Studio key (`GEMINI_API_KEY`). Google's API is reachable locally and
  returns the image **inline** (base64) — so you can view, QC, and save real files.
- Use `.claude/skills/winning-statics/scripts/generate_static.py` (already written for
  the Gemini image API). Model: `gemini-3-pro-image-preview` (Nano Banana Pro).
- Feed each reference + the product photo; it renders text far better than base models.

**Option B — Gold standard, pixel-perfect product.**
- `.workspace/gold_standard_ads.py` (needs `pip install pillow`). It generates each
  layout on Higgsfield with a **magenta placeholder** where the product goes (no tube
  drawn), downloads it, and composites the REAL product PNG into that zone. So the tube
  is exact pixels, never redrawn.
- NOTE: the magenta-detect/composite step was written but never runnable in the sandbox
  (no image download there) — **test it on ad #16 first, view the result, and fix the
  bbox/scale logic as needed** before running all 20.
- Higgsfield billed to `HF_API_KEY`/`HF_API_SECRET`. Model `nano-banana` or `seedream`.

Best of both: run Option A for the no-product concepts and Option B for the
product-hero ones — or just do Option A everywhere and only fall back to B if a
specific tube still looks wrong.

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
