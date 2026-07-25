---
name: winning-statics
description: Recreate proven, high-performing static image ads for the user's product using a library of 50 real winning statics (9 concept families) and Google's Nano Banana Pro image model. Use this skill whenever the user asks for static ads, image ads, ad creatives, statics, ad batches, before/after ads, testimonial ads, comparison ads, or anything like "make me N statics/ads for my product" — even if they don't name the skill. Generates on the user's own key — GEMINI_API_KEY (see GEMINI_SETUP.md) or a Higgsfield account via HF_API_KEY/HF_API_SECRET (see HIGGSFIELD_SETUP.md).
---

# Winning-Statics

This skill recreates proven, high-performing static image ads for the user's product. It does **not** brainstorm ad concepts from imagination. It takes 50 real winning statics — captured from live ad libraries with their performance receipts — and replicates their structure, hierarchy, and psychology with the user's product, brand colors, copy angle, and market. The 80/20 of ad creative is not inventing the wheel; it is putting the user's tire on a wheel that is already rolling.

Every generation call sends the **actual reference image** to the model — it sees the winning ad with its own eyes and rebuilds it around the user's product, rather than working from a lossy text description.

**Cost transparency, up front, always:** generation uses the user's own Google API key at roughly $0.13–0.14 per image (about $4 for a 30-image batch), and a large batch takes real minutes to generate and quality-check. Say this before generating. Surprise bills kill trust.

## Files in this skill

- `references/` — the 50 winning reference statics, named `ref-NN-slug.png`
- `references/LIBRARY.md` — the full catalog: 9 families, every reference's mechanism, when to use it, and its per-reference recreation notes. **Read this before planning any batch.**
- `GEMINI_SETUP.md` — one-time Google API key setup walkthrough and error troubleshooting table
- `HIGGSFIELD_SETUP.md` — alternative backend billed to the user's Higgsfield account
- `scripts/generate_static.py` — Gemini generation script (stdlib only). Self-test: `python3 scripts/generate_static.py --self-test`
- `scripts/higgsfield_backend.py` — Higgsfield generation script (stdlib only). Self-test: `python3 scripts/higgsfield_backend.py --self-test`

**Backend selection:** use Gemini when `GEMINI_API_KEY` is set; use Higgsfield when `HF_API_KEY`/`HF_API_SECRET` are set (the script rejects placeholder values and says so). If both are set, ask the user which account to bill. Cost framing differs: Gemini bills ~$0.13–0.14/image to their Google key; Higgsfield deducts account credits per generation (failed/moderated jobs are refunded by Higgsfield).

## The workflow, start to finish

### Step 1 — Intake

Collect, in plain language (ask only for what's missing):

1. **Product image** — a clean product photo. This is the single biggest quality lever: the model preserves the product with the fidelity of the photo it is fed. If the photo is blurry, say so now — no prompt can fix it.
2. **Website address** — for claims, tone, and offer terms.
3. **Full-page PDF snapshot of their site** — the reliable source for brand colors, typography feel, claims, and guarantee terms (works even when the live site blocks automated visitors). Suggest GoFullPage or Print-to-PDF if they don't have one.
4. **Avatar and angle** — in plain words, like briefing a freelancer ("stay-at-home moms with foot pain; angle is all-day comfort without ugly orthopedic looks"). The more specific the human, the sharper the headlines.
5. **Advertising market** — US, UK, AUS, CA, or other. Drives spelling, currency, seasonal timing.
6. **Aspect ratio** — 1:1, 4:5, or a mix.
7. **Quantity** and **diversity preference** — if the user doesn't want to make expert decisions, use the **Smart Mix** default: spread the batch across concept families weighted toward how aware their customer is (problem-aware skews to Problem-Agitation, Illustrated Mechanism, Editorial; solution-aware skews to Comparison, Callouts, Testimonial; most-aware skews to Big-Claim Hero and offer formats). If the user knows exactly what they want ("6 post-it notes, 4 comparisons, 10 before/afters"), obey exactly.

More is not automatically better: a well-spread 20 across four families usually teaches more than an unfocused 50 — say so when a user over-orders.

### Step 2 — The plan (before spending their money)

Before any API call, show a table: each planned image, which reference it is built from, which family it belongs to, and the angle note. Let the user veto anything; re-plan instantly. Honest-depth rule: family depth varies (Big-Claim Product Hero is the deepest at 13 references; Editorial/Advertorial holds only 2) — when a user asks for a large single-family batch, tell them the structural variety ceiling honestly.

Never place ref-10 and ref-26 in the same batch (same skeleton, kept as a variant example). Weight ref-20 down unless specifically requested — it is stored as a deliberate low-performer teaching contrast.

### Step 3 — Generation

Each image = reference static + user's product photo + precise swap instructions:

- Swap in the user's product, brand colors, headline, and market's spelling/currency.
- Any text that must appear in the image is specified **verbatim in quotes** in the prompt — that is how Nano Banana Pro renders text most accurately.
- Apply the protocols below (realism, localization, borrowed authority, testimonials).
- Call the selected backend script per image (see each script's `--help`). Keys come from environment variables only (`GEMINI_API_KEY`, or `HF_API_KEY`/`HF_API_SECRET`) — never ask for them in chat, never write them to a file.

### Step 4 — Quality control

Inspect every generated image (view the file) before showing the user. Check:

- Product label fidelity against the supplied product photo
- Text spelling — every word, exactly as specified
- Structural match to the reference layout
- Realistic human skin where humans appear (no plastic AI smoothing)
- No leftover wrong-market elements (currency, spelling, badges from the reference)
- Format-specific checks called out in LIBRARY.md (e.g. same-person identity across panels)

Failures are regenerated up to **twice** with corrective instructions. Anything still failing is flagged honestly instead of slipped into the pile. If a concept keeps failing on this product — some products photograph poorly into certain layouts — say so and suggest the nearest family that suits the product's shape instead of silently delivering junk.

### Step 5 — Iterate

When the user reports winners ("3, 7, and 12 performed"), produce variations of just those — same reference skeleton with adjusted angles, or siblings from the same family. This loop is where real testing programs live; remind the user it exists.

## The protocols

**Human realism.** Whenever a reference involves real human skin, faces, or bodies, inject instructions for natural texture: visible pores, fine lines, imperfect lighting, no beauty-filter smoothing. In before/after formats, additionally protect the 'before' from being accidentally beautified, and lock identity across panels (same face, hair, accessories, angle). If the reference is deliberately illustrated or cartoon, the protocol stands down — realistic skin on a cartoon would be wrong. LIBRARY.md marks which references trigger this.

**Localization.** Mechanical market swaps (spelling, currency, country names, seasonal timing) happen automatically from the market answer. Regulatory badges and credentials are **never invented** — if a reference carries a UK pharmacy registration and the user sells in the US, ask what real equivalent they hold; if none, swap that element for their review score or guarantee.

**Borrowed authority.** A few references lean on press logos or named personalities. Replicate the structure but replace borrowed authority with the user's real proof or generic trust elements — a recreated ad wearing someone else's credibility is a liability, not an asset.

**Testimonial integrity.** Testimonial-format references are replicated as *formats*. Quote text and attributions come from the user's real reviews, or are clearly proposed as placeholder copy for their approval. Never invent customers as fact.

**Competitor marks.** In comparison formats, competitor trademarks get genericized on recreation — the layout is replicated, other brands' marks are not.

**Platform note.** Some ad platforms restrict certain formats (like before/afters in some health verticals). Generate exactly what the user asks for and attach a one-line heads-up where relevant — never alter their creative unprompted.

## When something goes wrong

Key errors, quota errors, and billing errors each print a specific message from the script; GEMINI_SETUP.md's troubleshooting table maps each one to its fix. Generation quality issues are handled by the QC pass above.

**Ownership:** everything generated belongs to the user's account and their Google key. This skill ships with zero information about any other person's brand — the user's inputs in the conversation are its only source of brand data, by design.
