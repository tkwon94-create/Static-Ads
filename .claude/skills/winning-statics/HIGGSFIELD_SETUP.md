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
