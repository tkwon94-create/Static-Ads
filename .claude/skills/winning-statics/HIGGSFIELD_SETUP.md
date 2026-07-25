# Alternative Backend: Your Higgsfield Account

If you'd rather bill generation to your Higgsfield account than a Google API key, the skill can generate through Higgsfield's platform API (`platform.higgsfield.ai`), which hosts Google's Nano Banana models among many others.

## Setup

1. Sign in at [cloud.higgsfield.ai](https://cloud.higgsfield.ai) and create an **API key + secret** (account/API settings).
2. Set both environment variables:
   - `HF_API_KEY` — the key
   - `HF_API_SECRET` — the secret

   Local terminal: add `export HF_API_KEY=...` / `export HF_API_SECRET=...` to your shell profile and open a new terminal.

   Claude Code cloud sessions: edit your environment at claude.ai/code → your environment → settings → environment variables, then start a fresh session. **The variables must hold the real values — template text like `your_key_here` will be detected and rejected by the self-test.**
3. Verify: `python3 scripts/higgsfield_backend.py --self-test`
   This confirms the credentials are present, not placeholders, and accepted by Higgsfield — and prints the model ids your account can use.

Your key and secret never go into the chat or into any file — the script reads them from your environment only.

## How the skill uses it

- Backend selection: the skill uses Gemini when `GEMINI_API_KEY` is set, otherwise Higgsfield when `HF_API_KEY`/`HF_API_SECRET` are set. If both are set, it asks which account to bill.
- Default model is `google/nano-banana-pro` (override with the `HIGGSFIELD_MODEL` env var or `--model`). Run `--list-models` once to confirm the exact id your account exposes — model ids match the URL path on each model's page at cloud.higgsfield.ai/explore.
- Higgsfield takes input images **by URL**. The script converts local files (reference static + your product photo) to `data:` URIs automatically; if a model rejects those (HTTP 422), host the images somewhere reachable and pass `--image-url` instead.
- Jobs are asynchronous: the script submits, polls until `completed`, and downloads the result. `nsfw` and `failed` statuses refund credits on Higgsfield's side and are reported honestly.

## Troubleshooting

| What the script prints | The fix |
|---|---|
| `KEY ERROR: ... not set` | Set both `HF_API_KEY` and `HF_API_SECRET`, open a new terminal/session |
| `KEY ERROR: ... placeholder text` | The variables still contain template text — paste the real values |
| `KEY ERROR: Higgsfield rejected the credentials` | Re-copy key and secret from cloud.higgsfield.ai (both must match the same key) |
| `BILLING ERROR: not enough credits` | Top up credits at cloud.higgsfield.ai |
| `MODEL ERROR: ... not found` | Run `--list-models`; set the right id via `--model` or `HIGGSFIELD_MODEL` |
| `REQUEST ERROR (HTTP 422)` about images | The model wants hosted URLs — use `--image-url` with public https links |
| `SAFETY BLOCK` | Rephrase the claim (health/medical wording most often) or switch reference |

## Verified reality (July 2026)

- **Nano Banana *Pro* is not on Higgsfield's developer API.** Generation runs on `nano-banana` (Google's image-edit model) or `seedream`. Text rendering on base Nano Banana is good but a notch below Pro — for the crispest headline/stat text, the Gemini backend (`GEMINI_API_KEY`, Nano Banana Pro direct from Google) is stronger.
- **Image-to-image endpoint:** `POST /v1/text2image/{model}` with `{"params":{"prompt","input_images":[{"type":"image_url","image_url":URL}],"aspect_ratio"}}`; returns a job-set polled at `/v1/job-sets/{id}`; result at `jobs[0].results.raw.url`.
- **Inputs must be public http(s) URLs** (data: URIs are rejected). Local files auto-upload via `/files/generate-upload-url`.
- **A real User-Agent is required** or Cloudflare returns 403 (error 1010). The script sets one.
- **Locked-down networks:** if your environment's egress policy allows `platform.higgsfield.ai` but blocks the S3 upload host / CloudFront result host, uploads and downloads fail even though generation works. Host inputs on a public URL (`--image-url`) and open the printed result URLs from an unrestricted machine — or run this skill locally.
