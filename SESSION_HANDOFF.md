# SCRVNR v2.0 — Session Handoff
## For: Next Claude instance building SCRVNR v2.0
## From: Session that designed the VFP pipeline and v2.0 architecture (2026-07-15/16)

---

## READ THESE FILES IN THIS ORDER

1. `D:\Projects\SCRVNR\CLAUDE_INSTRUCTIONS.md` — Pre-Flight, project overview, key files
2. `D:\Projects\SCRVNR\STATUS.md` — Current state, what's shipped, what's specced
3. `D:\Projects\SCRVNR\BACKLOG.md` — Sprint queue with priorities
4. `D:\Projects\SCRVNR\SCRVNR_V2_ARCHITECTURE.md` — THE GOVERNING SPEC. Read in full before writing any code. 9 sections covering 6 subsystems, generation pipeline, product architecture, tech requirements, implementation plan, success criteria, open questions, system relationships, research citations.
5. `D:\Projects\SCRVNR\research\voice_fingerprint\SCRVNR_VOICE_FINGERPRINT_SPEC.md` — VFP pipeline spec (already executed, context for what produced the data)
6. `D:\Projects\SCRVNR\research\voice_fingerprint\voice_profile.md` — Human-readable voice profile with per-register stats
7. `D:\Projects\SCRVNR\research\voice_fingerprint\voice_signature.md` — David's rarity spikes, typo fingerprint, em-dash audit

## CONTEXT THAT ISN'T IN THE FILES

### Origin story
David read a newsletter about the StoryScope study (UMD + Google DeepMind, arXiv:2604.03136) which proved AI writing has a measurable shape — a symmetric blob at the 0.5 vocabulary rarity median — vs human writing which has a "kite shape" clustered at 0.71. David asked what we could learn from it. One session later: 5 VFP sprints (corpus assembly → register tagging → feature extraction → profile generation → integration), a full centrifuge module, and a v2.0 architecture spec informed by PEARL, PROSE, CIPHER, and EMG-RAG.

### The critical authorship insight
David corrected an early assumption: most text attributed to David is actually Claude-authored. Published essays = Claude prose + David architecture/rarity spikes. CLAUDE_INSTRUCTIONS.md = Claude-written. Git commits = Claude via smart_commit. Research papers = ~95% Claude. The REAL David voice corpus is his Human: turns in chat (29,612 messages), GPT user turns (10,871), SMS sent messages (1,609), and pre-AI documents (.doc files from AIS era). The correction-pair insight (CIPHER) extends this: David's corrections to Claude output are worth MORE than his raw samples because they contain both the wrong answer and the right answer.

### What the centrifuge proved
We scored "Crazy In Tents" (David's flagship investigative essay, ~7,000 words, published at davidkirsch.me). Best score: 0.47 against CREATIVE_DIRECTION register. This confirmed it's hybrid writing (David's architecture, Claude's prose). A surgical contraction pass was attempted but David correctly identified it as a patch, not a rewrite. The real quality leap requires the v2.0 generation pipeline: few-shot retrieval + preference description + correction learning changing the INPUT to generation, not just the evaluation of the output.

### What David wants
SCRVNR v2.0 built. Not as a concept. As working code. The v2.0 architecture spec (SCRVNR_V2_ARCHITECTURE.md) defines 5 implementation sprints. Start with SCRVNR-V2-01 (Correction Capture) — highest leverage, no dependencies. Then V2-02 through V2-05 in order.

The end goal: when David opens a chat and says "rewrite Crazy In Tents through SCRVNR," the system retrieves his actual investigative writing as few-shot context, loads his iteratively-refined preference description, generates with those inputs, auto-corrects mechanicals, scores with the centrifuge, rewrites flagged sections, and ships — producing output that's measurably closer to his voice than anything the current system can produce.

### Anti-patterns the next instance should avoid
- Don't suggest manual steps when tools exist (§0.8 invariant 1)
- Don't use PowerShell — use cmd (SCRVNR runs on Windows, D:\ paths)
- Don't use bare `python` — always `D:\Programs\Python312\python.exe`
- Don't try to load the .jsonl corpus files into memory — they're ~100MB total, stream-process with ijson or line-by-line
- Don't touch existing voice.db tables — all schema changes are ADDITIVE ONLY
- Don't confuse David's voice with Claude's calibrated-to-David output. Chat messages = David. Essays = hybrid. Instructions files = Claude.

### Key technical details
- voice.db is SQLite at `D:\Projects\SCRVNR\learning\voice.db`
- Centrifuge: `from core.centrifuge import VoiceCentrifuge; c = VoiceCentrifuge(); r = c.score(text, register)`
- CLI: `D:\Programs\Python312\python.exe D:\Projects\SCRVNR\tools\centrifuge_cli.py score {file} --register {REG}`
- Quality gate: `D:\Programs\Python312\python.exe D:\Projects\SCRVNR\tools\quality_gate.py {file} --env {env}`
- Corpus files on disk (gitignored): `research\voice_fingerprint\final_corpus.jsonl`, `features_final.jsonl`
- Embedding infrastructure: nomic-embed-text via Ollama (already running for brain.db)
- Dependencies installed: wordfreq, ijson, nltk, matplotlib, seaborn, scipy, regex

### The SCRVNR Loader (for non-dev sessions that just want to USE SCRVNR)
`D:\Projects\SCRVNR\SCRVNR_LOADER.md` — paste at top of any chat to enable centrifuge scoring. Mode A (David's voice) or Mode B (anti-slop for any brand).

---

## SPRINT EXECUTION NOTES

Each sprint should follow AUTONOMIC format:
- GIT IDENTITY: dk.dkes@hotmail.com / David Kirsch
- GIT PROTOCOL: write to .git\COMMIT_MSG_TEMP, commit with -F flag
- Shell: cmd (not PowerShell)
- Python: D:\Programs\Python312\python.exe
- All new code at D:\Projects\SCRVNR\ (registered in KERNL PM as id: scrvnr)
- Corpus files are gitignored — only commit scripts, summaries, and reports
- Run centrifuge integration test after any schema or module changes
