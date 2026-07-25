# One-Time Setup: Your Google API Key

This walkthrough is written for someone who has never touched an API. Five minutes, one time, done.

The Winning-Statics skill generates images with Google's **Nano Banana Pro** image model, billed to your own Google account. You pay only for what you generate — roughly **$0.13–0.14 per image** (about $4 for a 30-image batch).

## Click-by-click

1. **Create a free account** at [aistudio.google.com](https://aistudio.google.com) (sign in with any Google account).
2. Click **Get API Key** (key icon in the left sidebar).
3. Click **Create API Key** and copy the key it shows you. Treat it like a password.
4. **Enable billing** on the project when prompted. You only pay for what you generate — while you're in the billing console, **set a budget alert** (e.g. $10/month) so nothing ever surprises you.
5. **Store the key in an environment variable called `GEMINI_API_KEY`:**

   **Mac / Linux** — add this line to `~/.zshrc` (Mac) or `~/.bashrc` (Linux), then open a new terminal:
   ```bash
   export GEMINI_API_KEY="paste-your-key-here"
   ```

   **Windows (PowerShell):**
   ```powershell
   [Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "paste-your-key-here", "User")
   ```
   Then restart your terminal.

6. **Ask Claude to run the self-test:** "run the winning-statics self-test". It runs:
   ```bash
   python3 scripts/generate_static.py --self-test
   ```
   which verifies the key is present and can reach the model, then generates one tiny test image (~$0.14).

**Your key never goes into the chat or into any file** — the script reads it from your environment only. If Claude ever asks you to paste your key into the conversation, refuse; that is not how this skill works.

## Troubleshooting table

| What the script prints | What it means | The fix |
|---|---|---|
| `KEY ERROR: GEMINI_API_KEY is not set` | The environment variable isn't visible to this terminal | Re-do step 5, then open a **new** terminal (old terminals don't see new variables) |
| `KEY ERROR: API key not valid` (HTTP 400, `API_KEY_INVALID`) | The key was mistyped, truncated, or revoked | Copy the key again from AI Studio, re-set the variable; if it persists, create a fresh key |
| `PERMISSION ERROR` (HTTP 403) | The key exists but this project can't use the model | In AI Studio, confirm the key belongs to the project you enabled billing on |
| `QUOTA ERROR: rate limited` (HTTP 429, `RESOURCE_EXHAUSTED`) | Too many requests per minute, or the free tier has no image quota | Wait a minute and retry (the script does this automatically 3 times); if it never clears, billing isn't enabled — see next row |
| `BILLING ERROR` (HTTP 429/403 mentioning billing or free tier) | Image generation requires a billed project | Finish step 4 — enable billing and set a budget alert |
| `MODEL ERROR: model not found` (HTTP 404) | The model name changed or isn't available in your region | Update `MODEL` at the top of `scripts/generate_static.py` to the current Nano Banana Pro model id listed at ai.google.dev |
| `SAFETY BLOCK: the model declined this image` | The prompt or reference tripped a content filter | Rephrase the claim (health/medical claims trip this most often), or pick a different reference |
| `NETWORK ERROR` | No route to the API | Check your connection / proxy / VPN |

Anything else: run the self-test and read its output — every failure mode prints one of the messages above.
