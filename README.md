# Static-Ads

Home of the **Winning-Statics** Claude Code skill: it recreates proven, high-performing static image ads for your product from a library of 50 real winning statics (9 concept families), generating with Google's Nano Banana Pro image model on your own API key.

## The skill

The skill lives at [`.claude/skills/winning-statics/`](.claude/skills/winning-statics/), so any Claude Code session opened in this repository picks it up automatically. To install it elsewhere, copy that folder into your Claude Code skills directory (`~/.claude/skills/`), or save the packaged `.skill` file.

- [`SKILL.md`](.claude/skills/winning-statics/SKILL.md) — the workflow: intake → plan → generation → quality control → iterate
- [`references/LIBRARY.md`](.claude/skills/winning-statics/references/LIBRARY.md) — the 50-reference catalog across 9 families
- [`GEMINI_SETUP.md`](.claude/skills/winning-statics/GEMINI_SETUP.md) — one-time API key setup (5 minutes) and troubleshooting
- [`scripts/generate_static.py`](.claude/skills/winning-statics/scripts/generate_static.py) — stdlib-only generation script + self-test

## Quick start

1. Follow `GEMINI_SETUP.md` once (free Google AI Studio account → API key → `GEMINI_API_KEY` env var → self-test).
2. Open Claude Code and say something like: **"make me 20 statics for my product"**.
3. The skill collects your product photo, website, site PDF snapshot, and angle; shows you the batch plan before spending anything; generates; quality-checks; and iterates on your winners.

Expect roughly $0.13–0.14 per image on your Google key (about $4 for a 30-image batch).
