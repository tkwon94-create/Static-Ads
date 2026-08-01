# Running an ad batch on Gemini (Nano Banana Pro)

**Gemini runs in-session. It is not blocked.** An earlier version of this file said the
Claude Code sandbox could not reach `generativelanguage.googleapis.com` and that Gemini
had to run on your own machine. That was wrong, and it cost a session's worth of time.

The confusion is a 403. This command:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" --max-time 20 \
  https://generativelanguage.googleapis.com/v1beta/models
```

returns **403** — but that is *Google* rejecting an unauthenticated request
(`"Method doesn't allow unregistered callers"`), not the proxy refusing CONNECT. The
proxy handshake succeeds (`HTTP/1.1 200 Connection Established`). The same URL **with**
the key returns 200.

To actually test reachability, send the key:

```bash
curl -sS -o /dev/null -w "%{http_code}\n" \
  -H "x-goog-api-key: $GEMINI_API_KEY" \
  https://generativelanguage.googleapis.com/v1beta/models      # expect 200
```

A bare-403 means "no credentials", not "blocked".

## Setup

```bash
export GEMINI_API_KEY='...'                       # aistudio.google.com -> Get API Key
python3 .workspace/run_gemini_batch.py --self-test # ~$0.14, writes a test image
```

**Image models require billing.** On a free-tier key every image model returns HTTP 429
with `limit: 0` — that means "not available on this tier at all", not "you ran out
today". Waiting does nothing; enable billing on the key's Google Cloud project.

## Generate a batch

```bash
python3 .workspace/run_gemini_batch.py --batch haloven      # 12 ads, ~$1.70
python3 .workspace/run_gemini_batch.py --batch postpartum   # 10 ads
python3 .workspace/run_gemini_batch.py --batch original     # 20 ads
```

Useful flags: `--only h03,h11` · `--out DIR` · `--retries N` · `--placeholder`.

## The product tube: two paths

Pro renders in-layout text extremely well but still garbles the **product label**, and
it garbles it worse the smaller the tube sits in frame. Two ways to handle it.

**Path A — composite the real tube (preferred).** Generate with a magenta placeholder,
then paste the real photo in, so the label is your exact pixels:

```bash
python3 .workspace/run_gemini_batch.py --batch haloven --placeholder \
        --out out_gemini/haloven_layouts
python3 .workspace/composite_gemini.py --layouts out_gemini/haloven_layouts \
        --out out_gemini/haloven
```

Pro sometimes ignores the placeholder when the prompt says the tube is *held in a hand*
— it draws the product instead and the composite finds no magenta zone. For those ads
use the stronger wording, which restates the rule in terms of the held object and pins
the placeholder's aspect to 4:5 so less area needs reconstructing:

```bash
python3 .workspace/rerun_placeholder.py --only h03,h05,h06
```

**Path B — direct render.** Let Pro draw the tube. Fine when the tube is large in frame
(h05, h12 came back essentially letter-perfect); unreliable when small. Always zoom to
100% and read the microcopy — `SCALP CLERA`, `(V)BioExo-Water(Heartleaf)`, the body
paragraph. That is where garbling shows first.

Do not use the strong placeholder wording on a full-bleed hero. On h11 it produced a
cropped tube with the words `PIII badged` printed onto the label as leaked instruction
text.

### composite_gemini.py flags

`--fullbox h10` clears the placeholder's entire bounding box instead of sweeping by hue.
Needed only when the placeholder blended into a warm subject and left residue no color
test can see (h10's crimson bled into a brown sweater and came back reddish-brown, blue
*below* green). It costs real detail — it smeared h03's winner cell and ate part of
h10's own bottom trust line — so keep it per-ad, never global.

`--pad 0.06` insets the tube inside the placeholder box.

## Prompts

`.workspace/build_haloven_prompts.py` generates the 12 competitor-structure prompts and
self-checks that no `#` survives in any layout body. Two rules it enforces, both learned
the hard way:

- **Never write a hex code in the layout body.** The old prompts said "a thick `#C14201`
  border" while the footer forbade rendering hex codes — that is how codes leaked into
  an earlier run as visible text. Name colors in words; the codes appear only in the
  final painting-instruction block.
- **Never leave placeholder wording in a non-placeholder prompt.** h02 carried a stale
  magenta line that contradicted its own instruction to render the tube.

Higgsfield-era originals are preserved in `.workspace/haloven_prompts_higgsfield/`.

## QC standard

Inspect every image before showing the user: label fidelity against the real photo, every
quoted line letter-perfect and appearing exactly once, no duplicated or ghost text, no
leaked hex codes, no reference-ad contamination, realistic skin, correct subject age
(specify age as a number — "aged 30" works, descriptions do not). Regenerate up to twice,
then repair deterministically, then flag honestly rather than shipping something broken.

`python3 .workspace/make_grid.py --dir out_gemini/haloven --out grid.png` builds a
labeled contact sheet for a first pass, but it is not a substitute for viewing each ad
at full size — the h02 X-mark regression and h10's smear were both invisible at
thumbnail scale.

## Brand palette

peach `#E8B093` · brand orange `#C14201` · badge orange `#B95618` ·
text `#000000` · product white `#F5F5F6` · background `#FFFFFF`

Pass colors as painting instructions, never as content.
