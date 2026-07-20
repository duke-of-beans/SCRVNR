<div align="center">

![SCRVNR Logo](branding/logos/Logo%20Full%20Trans.png)

# SCRVNR

**Version:** 1.0.0 | **Status:** Production Ready

*Authentic Voice, Automatically Learned*

</div>

---

## What Is SCRVNR?

SCRVNR is a voice synthesis system that captures and reproduces **your** authentic
writing style across all communication contexts. Feed it samples of your writing,
and it learns your patterns — contractions, sentence rhythm, register shifts,
forbidden phrases — then applies them consistently every time you generate content.

It learns from every output, continuously improving authenticity through automatic
pattern extraction and database-driven learning.

---

## The Problem

AI-generated content sounds like AI. Even when the facts are right, the voice is
wrong — too formal, too hedged, too generic. Copy-pasting into your style after
the fact is friction you shouldn't have.

SCRVNR inverts this: your voice is the input, not an afterthought.

---

## Environments

SCRVNR separates voice into five contexts, each with independent calibration:

| Environment | Use Cases |
|-------------|-----------|
| `career` | Cover letters, LinkedIn posts, professional bios |
| `personal` | Emails to friends, social posts, casual writing |
| `dev` | READMEs, technical docs, commit messages |
| `research` | Papers, reports, analytical writing |
| `work` | Internal comms, proposals, client-facing docs |

Each environment has its own contraction rate, formality level, sentence length
targets, and forbidden pattern list — all learned from your samples.

---

## Quick Start

### 1. Configure your voice

Edit `SCRVNR_INSTRUCTIONS.md` to replace the placeholder voice profile with your
own writing samples and style notes. The more examples you provide, the more
accurate the synthesis.

### 2. Generate content via Claude (primary method)

Load `SCRVNR_INSTRUCTIONS.md` in a Claude session. SCRVNR auto-detects the
environment from your request and applies the right voice profile.

```
"write a cover letter for this role"
"draft a LinkedIn post about X"
"write a README for my project"
"help me write an email to [person]"
```

Claude generates content inline, validates against 7 quality checks, and
auto-samples the output for continuous learning.

### 3. Generate via CLI

```bash
python tools/orchestrator.py generate --env career --context cover_letter
```

Output saved to `outputs/`. Valid environments: `career`, `personal`, `dev`,
`research`, `work`.

---

## Other CLI Commands

```bash
# Validate an existing file against your voice profile
python tools/quality_gate.py output.md --env personal

# Analyze voice characteristics of a document
python tools/orchestrator.py analyze document.docx --env work
# Returns: contraction rate, forbidden pattern hits, voice confidence score

# Detect environment from a text snippet
python tools/environment_detector.py "write a cover letter for VP Operations"
# Returns: detected environment + confidence score (e.g. career: 0.95)

# Check system health
python tools/orchestrator.py status
# Returns: database record counts, recent sample summary, pattern confidence
```

**Windows note:** Prefix with `set PYTHONIOENCODING=utf-8 &&` to avoid Unicode
errors in cmd.

---

## How It Learns

Every generated output is automatically sampled and analyzed. Pattern confidence
scores update over time. The longer you use it, the more accurate it gets.

Learning pipeline:

```
Your samples → Pattern extraction → Environment database
                                           ↓
New request → Environment detection → Voice calibration → Generated content
                                                                ↓
                                               Quality gates → Auto-sample → Database update
```

---

## Quality Gates

Every output is validated against 7 checks before delivery:

- Contraction rate within environment baseline
- Forbidden phrase detection
- Sentence length distribution
- Register consistency
- Voice confidence score threshold
- Pattern density
- Authenticity delta vs. raw AI output

---

## Architecture

```
SCRVNR/
├── core/               Voice engine and pattern matching
├── environments/       Per-context calibration configs
├── learning/           Auto-sampling and database update pipeline
├── tools/              CLI: orchestrator, quality_gate, environment_detector
├── outputs/            Generated content (gitignored)
└── SCRVNR_INSTRUCTIONS.md   The voice profile Claude reads
```

---

## Setup

```bash
# Requirements: Python 3.10+
pip install -r requirements.txt

# Initialize the database
python tools/orchestrator.py init

# Check everything is working
python tools/orchestrator.py status
```

---

## License

MIT — Use it, fork it, train it on your own voice.

## Author

[@duke-of-beans](https://github.com/duke-of-beans)
