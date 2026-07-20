---
name: SCRVNR
description: Personal voice synthesis system — learns your authentic writing style from samples and reproduces it consistently across career, personal, dev, research, and work contexts with automatic quality validation and continuous learning.
author: duke-of-beans
homepage: https://github.com/duke-of-beans/SCRVNR
license: MIT
---

# SCRVNR Skills

## Voice-Authentic Content Generation

Generate written content that sounds like you, not like AI. SCRVNR loads your
voice profile, detects the appropriate environment (career, personal, dev,
research, work), applies calibrated patterns, and validates the output against
7 quality gates before delivery.

## Continuous Voice Learning

Every generated output is automatically sampled, analyzed, and fed back into the
pattern database. Contraction rates, sentence rhythm, forbidden phrases, and
register calibration all improve over time with use.

## Environment-Aware Style Switching

Automatically shifts register, formality, and sentence structure based on the
writing context — cover letter vs. README vs. casual email — all from the same
underlying voice profile.

---

## Prompts

- "Write a cover letter for this role in my voice"
- "Draft a LinkedIn post about X"
- "Write a README for my project"
- "Help me write a professional email to [person]"
- "Validate this draft against my voice profile"
- "Analyze the voice characteristics of this document"
- "Generate a bio for my dev portfolio"

---

## Resources

- `SCRVNR_INSTRUCTIONS.md` — Voice profile and environment configs (customize this)
- `core/` — Voice engine and pattern matching
- `environments/` — Per-context calibration settings
- `learning/` — Auto-sampling and database update pipeline
- `tools/orchestrator.py` — Main CLI entry point
- `tools/quality_gate.py` — Standalone validation tool
