# Static-Ads

Home of the **Winning-Statics** Claude Code skill: it recreates proven, high-performing static image ads for your product from a library of 50 real winning statics (9 concept families), generating with Google's Nano Banana Pro image model on your own API key.

## The skill

The skill lives at [`.claude/skills/winning-statics/`](.claude/skills/winning-statics/), so any Claude Code session opened in this repository picks it up automatically. To install it elsewhere, copy that folder into your Claude Code skills directory (`~/.claude/skills/`), or save the packaged `.skill` file.

- [`SKILL.md`](.claude/skills/winning-statics/SKILL.md) — the workflow: intake → plan → generation → quality control → iterate
- [`references/LIBRARY.md`](.claude/skills/winning-statics/references/LIBRARY.md) — the 50-reference catalog across 9 families
- [`GEMINI_SETUP.md`](.claude/skills/winning-statics/GEMINI_SETUP.md) — one-time Google API key setup (5 minutes) and troubleshooting
- [`HIGGSFIELD_SETUP.md`](.claude/skills/winning-statics/HIGGSFIELD_SETUP.md) — alternative backend billed to your Higgsfield account (`HF_API_KEY`/`HF_API_SECRET`)
- [`scripts/`](.claude/skills/winning-statics/scripts/) — stdlib-only generation scripts (Gemini and Higgsfield), each with a `--self-test`

## Quick start

1. Set up one backend: `GEMINI_SETUP.md` (Google API key → `GEMINI_API_KEY`) or `HIGGSFIELD_SETUP.md` (Higgsfield key + secret → `HF_API_KEY`/`HF_API_SECRET`), then run the matching self-test.
2. Open Claude Code and say something like: **"make me 20 statics for my product"**.
3. The skill collects your product photo, website, site PDF snapshot, and angle; shows you the batch plan before spending anything; generates; quality-checks; and iterates on your winners.

Expect roughly $0.13–0.14 per image on your Google key (about $4 for a 30-image batch).
