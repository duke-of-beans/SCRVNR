# CLAUDE_INSTRUCTIONS.md — SCRVNR
## Pre-Flight Checklist
- **Production URL**: N/A (local tooling, not deployed)
- **Package Manager**: pip (Python 3.12 at `D:\Programs\Python312\python.exe`) — no lockfile, deps installed globally with `--break-system-packages`
- **Deploy Flow**: `git add -A` → write commit message to `.git\COMMIT_MSG_TEMP` → `git commit -F .git\COMMIT_MSG_TEMP` → `git push origin main`
- **Repo URL**: https://github.com/duke-of-beans/SCRVNR
- **Git Identity**: `dk.dkes@hotmail.com` / `David Kirsch`

## Project Overview
SCRVNR is a voice synthesis system that captures and reproduces David's authentic voice. It is NOT an app or a service — it's a toolchain and data system that other projects consume.

**Architecture**: SQLite database (`learning/voice.db`) containing voice patterns, forbidden patterns, quality samples, and (as of VFP-04) quantitative voice profiles derived from 42,363 David-authored messages across 11 registers. Python CLI tools at `tools/`. Environment calibration YAMLs at `environments/`.

**Voice Fingerprint Research** (active): `research/voice_fingerprint/` contains the VFP pipeline — corpus extraction, register tagging, feature extraction, and profile generation. Governed by `SCRVNR_VOICE_FINGERPRINT_SPEC.md`. The voice profile (`voice_profile.json`) is the quantitative target for the rarity centrifuge.

## Key Files
| File | Purpose |
|------|---------|
| `SCRVNR_INSTRUCTIONS.md` | v1.0 instructions (pre-VFP, lightweight router for Claude sessions) |
| `learning/voice.db` | SQLite: 9 tables, 4 views. Core voice data. |
| `core/protocols/MASTER_PROTOCOL.md` | Generation orchestrator |
| `core/protocols/forbidden-patterns.md` | Anti-patterns (blocking) |
| `environments/{env}/calibration.yaml` | Per-environment voice params |
| `research/voice_fingerprint/voice_profile.json` | Quantitative voice profile (VFP-04) |
| `research/voice_fingerprint/voice_signature.md` | Human-readable voice signature |
| `research/voice_fingerprint/SCRVNR_VOICE_FINGERPRINT_SPEC.md` | Governing spec for VFP pipeline |

## Registers (expanded from original 5 environments)
TECH, CASUAL, PROFESSIONAL, MECHANICAL, INVESTIGATE, ACADEMIC, ARGUMENTATIVE, CREATIVE_DIRECTION, PERSONAL, FRUSTRATED

## Conventions
- Shell: cmd (not PowerShell)
- Python: always `D:\Programs\Python312\python.exe` (not bare `python`)
- `.jsonl` corpus files are gitignored — they live on disk only
- Charts and `.md` reports are committed
- voice.db schema changes require a migration script in `learning/scripts/`

## Related Projects
- **ContentStudio/MorphemeG**: SCRVNR is the origin architecture for Voice Layer (VOICE_LAYER_SPEC.md)
- **GregLite/Gregore**: future Rosetta integration for live voice profile updates (backlogged)
- **Easter Agency**: Wave 2 proof mandate depends on SCRVNR + ContentStudio composition
