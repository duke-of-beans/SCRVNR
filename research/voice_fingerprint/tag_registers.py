#!/usr/bin/env python3
"""
VFP-02: Register Tagging Engine for SCRVNR Voice Fingerprint
Tags each message in the 42,363-message corpus with a register label.
Stream-processes raw_corpus.jsonl → tagged_corpus.jsonl.
"""

import json
import re
import sys
import os
from pathlib import Path
from collections import Counter

CORPUS_DIR = Path(r"D:\Projects\SCRVNR\research\voice_fingerprint")
INPUT_FILE = CORPUS_DIR / "raw_corpus.jsonl"
OUTPUT_FILE = CORPUS_DIR / "tagged_corpus.jsonl"

# ─── REGISTER TAXONOMY ───────────────────────────────────────────────
REGISTERS = [
    "TECH", "INVESTIGATE", "PERSONAL", "CASUAL", "PROFESSIONAL",
    "ARGUMENTATIVE", "CREATIVE_DIRECTION", "MECHANICAL", "FRUSTRATED",
    "ACADEMIC", "UNTAGGED"
]

# ─── TITLE KEYWORD → REGISTER MAPPING ────────────────────────────────
# Each tuple: (compiled_regex_pattern, register)
# Order matters: first match wins. More specific patterns first.
TITLE_KEYWORDS = [
    # MECHANICAL — Volvo/hardware
    (re.compile(r'\b(?:volvo|engine|cam|timing|b5254|transmission|mechanical|turbo|boost|intercooler|exhaust|radiator|coolant|brake|suspension|clutch|flywheel|injector|intake|manifold|gasket|crankshaft|camshaft|piston|cylinder|wiring|harness|relay|fuse|ECU|OBD|diagnostic|torque|horsepower)\b', re.I), "MECHANICAL"),

    # INVESTIGATE — research/investigative
    (re.compile(r'\b(?:tranche|graph|entity|vigil|fascia|9[/-]?11|epstein|investigation|corpus|meridian|fine\s*print|national\s*razor|FOIA|whistleblow|coverup|cover.up|intelligence|surveillance|crisis\s*cap|ledger|dossier|classified|declassified|redacted|PACER|court\s*filing)\b', re.I), "INVESTIGATE"),

    # ACADEMIC — research/theory
    (re.compile(r'\b(?:arxiv|paper|hirm|multiplicative|theorem|proof|academic|axiom|lemma|corollary|dissertation|hypothesis|consciousness|ontolog|epistem|phenomeno|cognitive\s*organism|autopoie|emergent|storyscape|storyscope)\b', re.I), "ACADEMIC"),

    # CREATIVE_DIRECTION — writing/voice/essays
    (re.compile(r'\b(?:essay|writing|draft|voice|scrvnr|linkedin\s*post|article|crazy\s*in\s*tents|what\s*lies\s*beneath|mosaic|beautiful\s*mosaic|overton|natural\s*order|shadows\s*on\s*the\s*wall|tone|rewrite|editorial|prose|narrative|rigged\s*by\s*design|chapter|book)\b', re.I), "CREATIVE_DIRECTION"),

    # TECH — software/infrastructure
    (re.compile(r'\b(?:asuriq|consensus|railway|vercel|deploy|build|sprint|backlog|mcp|kernl|typescript|next\.?js|supabase|git|commit|api|docker|node|npm|pnpm|react|tailwind|prisma|database|postgres|redis|webhook|endpoint|middleware|server|frontend|backend|component|refactor|debug|bug|error|stack\s*trace|migration|schema|route|auth|token|JWT|OAuth|CI|CD|pipeline|lambda|serverless|terraform|AWS|cloudflare|DNS|SSL|nginx|upstream|downstream|repository|branch|merge|pull\s*request|PR|issue|ticket|linter|eslint|prettier|webpack|vite|bundl|transpil|compil|runtime|dependency|package|module|import|export|function|class|interface|type|enum|generic|async|await|promise|callback|hook|state|prop|render|DOM|HTML|CSS|JS|Python|Rust|Go|SQL|YAML|JSON|XML|regex|grep|bash|shell|terminal|CLI|IDE|vscode|cursor|greglite|gregore|consonance|forme|shim|trace|covos|boom.and.bust|oktyv|throwbak)\b', re.I), "TECH"),

    # PROFESSIONAL — career/business
    (re.compile(r'\b(?:resume|cover\s*letter|job|application|upwork|easter\s*agency|client|proposal|outreach|interview|salary|negotiate|portfolio|linkedin|recruiter|hiring|freelanc|contract|invoice|billing|revenue|pricing|pitch|deck|startup|venture|investor|funding|business\s*plan|marketing|brand|strategy|consulting|engagement|deliverable|stakeholder|KPI|OKR|roadmap|milestone|retainer)\b', re.I), "PROFESSIONAL"),

    # PERSONAL — relationships/emotions
    (re.compile(r'\b(?:lindsay|kissa|rachel|angela|dating|relationship|breakup|break.up|kids|personal|feelings|emotion|therapy|therapist|love|divorce|custody|co.?parent|family|mom|dad|ashley|brother|sister|grief|lonely|anxious|depress|heartbreak|vulnerable|trust|intimacy|attachment)\b', re.I), "PERSONAL"),

    # CASUAL — low-stakes
    (re.compile(r'\b(?:recipe|cook|food|ricotta|turkey|apple|ingredients|dinner|lunch|breakfast|snack|orestes|perfect\s*circle|music|song|album|playlist|spotify|guitar|band|concert|movie|show|netflix|streaming|game|gaming|weather|vacation|trip|hike|workout|gym|exercise|beer|wine|coffee)\b', re.I), "CASUAL"),
]

# ─── CONTENT HEURISTICS ──────────────────────────────────────────────
PROFANITY_PATTERN = re.compile(r'\b(?:fuck|shit|damn|hell|ass|bullshit|wtf|goddam|bitch|crap|piss)\b', re.I)
FRUSTRATED_PATTERN = re.compile(r'(?:\?\?|wtf|the\s+fuck|what\s+the\s+hell|are\s+you\s+kidding)', re.I)
FILE_PATH_PATTERN = re.compile(r'[A-Z]:\\|\/[a-z]+\/[a-z]+|\.(?:py|js|ts|tsx|jsx|json|yaml|yml|md|css|html)\b', re.I)
CODE_PATTERN = re.compile(r'(?:function\s|const\s|let\s|var\s|import\s|export\s|class\s|def\s|return\s|console\.|print\(|npm\s|git\s|docker\s|pip\s)', re.I)
MONEY_PATTERN = re.compile(r'(?:\$\d|revenue|pricing|invoice|billing|retainer|hourly\s*rate)', re.I)
TECH_TERM_PATTERN = re.compile(r'\b(?:API|CLI|SDK|URL|DNS|SSL|JWT|OAuth|SQL|HTML|CSS|npm|git|docker|deploy|server|database|endpoint|middleware|component|function|module|import|build|compile|runtime|debug|error|stack|trace|config|env|repo|branch|merge|commit)\b', re.I)


# ─── SMS CONTACT → REGISTER MAPPING ──────────────────────────────────
# Extract contact name from conversation_title "SMS with {Name}"
SMS_PERSONAL_CONTACTS = re.compile(
    r'\b(?:mikey|gavin|kissa|lindsay|angela|rachel|mom|dad|ashley|cathy|'
    r'brother|sister|bro|sis)\b', re.I
)

def extract_sms_contact(msg):
    """Extract contact name from SMS conversation_title."""
    title = msg.get("conversation_title", "") or ""
    m = re.match(r'^SMS with (.+)$', title, re.I)
    return m.group(1).strip() if m else ""


# ─── THROWBAK SUBDIRECTORY → REGISTER ────────────────────────────────
THROWBAK_SUBDIR_MAP = {
    "intellectual": "ACADEMIC",
    "threads": "PERSONAL",
    "people": "PERSONAL",
    "persons": "PERSONAL",
    "events": "PERSONAL",
    "creative": "CREATIVE_DIRECTION",
    "decisions": "PERSONAL",
    "work_chapters": "PROFESSIONAL",
    "eras": "PERSONAL",
}


# ─── TAGGING FUNCTIONS ───────────────────────────────────────────────

def tag_by_title(title):
    """Match conversation title keywords against register patterns."""
    if not title or title.lower() in ("untitled", "new chat", ""):
        return None
    for pattern, register in TITLE_KEYWORDS:
        if pattern.search(title):
            return register
    return None


def tag_by_content(text, word_count):
    """Content-based heuristics when title doesn't match."""
    if not text:
        return "UNTAGGED"

    # FRUSTRATED: profanity + question marks + short messages
    has_profanity = bool(PROFANITY_PATTERN.search(text))
    has_frustrated = bool(FRUSTRATED_PATTERN.search(text))
    if has_frustrated:
        return "FRUSTRATED"
    if has_profanity and "?" in text and word_count < 30:
        return "FRUSTRATED"

    # Very short non-technical → CASUAL
    if word_count < 8 and not TECH_TERM_PATTERN.search(text):
        return "CASUAL"

    # File paths or code references → TECH
    if FILE_PATH_PATTERN.search(text) or CODE_PATTERN.search(text):
        return "TECH"

    # Money/business terms → PROFESSIONAL
    if MONEY_PATTERN.search(text):
        return "PROFESSIONAL"

    return "UNTAGGED"


def tag_claude_or_gpt(msg):
    """Tag Claude/GPT chat messages: title first, then content heuristics."""
    title = msg.get("conversation_title", "") or ""
    text = msg.get("text", "") or ""
    wc = msg.get("word_count", 0)

    # Try title-based tagging
    register = tag_by_title(title)
    if register:
        return register

    # Fall through to content heuristics
    return tag_by_content(text, wc)


def tag_sms(msg):
    """Tag SMS messages by contact name, default CASUAL."""
    contact = extract_sms_contact(msg)
    if contact:
        if SMS_PERSONAL_CONTACTS.search(contact):
            return "PERSONAL"
        # Check if it looks like a phone number (unknown contact)
        if re.match(r'^\+?\d[\d\s\-]+$', contact):
            return "CASUAL"
        # Named contact not in personal list — still likely personal for SMS
        return "PERSONAL"
    # No contact info at all
    return "CASUAL"


def tag_throwbak(msg):
    """Tag throwbak records by subdirectory in source_file."""
    source_file = msg.get("source_file", "") or ""
    # source_file format: "subdir\\filename" or "subdir/filename"
    parts = re.split(r'[\\\/]', source_file)
    if len(parts) >= 2:
        subdir = parts[0].lower()
        register = THROWBAK_SUBDIR_MAP.get(subdir)
        if register:
            return register
    # Default throwbak to PERSONAL
    return "PERSONAL"


def tag_career_voice(msg):
    """Tag career_voice: Writing-Protocol* → CREATIVE_DIRECTION, else PROFESSIONAL."""
    source_file = msg.get("source_file", "") or ""
    if source_file.lower().startswith("writing-protocol"):
        return "CREATIVE_DIRECTION"
    return "PROFESSIONAL"


def tag_essays(msg):
    """Tag essays: all CREATIVE_DIRECTION (hybrid weight already set in corpus)."""
    return "CREATIVE_DIRECTION"


def tag_ais_profile_master(msg):
    """Tag AIS Profile Master docs: PROFESSIONAL."""
    return "PROFESSIONAL"


def tag_ais_master_data(msg):
    """Tag AIS Master Data docs: PROFESSIONAL."""
    return "PROFESSIONAL"


# ─── SOURCE DISPATCH ─────────────────────────────────────────────────
SOURCE_TAGGERS = {
    "claude_chat": tag_claude_or_gpt,
    "gpt_chat": tag_claude_or_gpt,
    "sms": tag_sms,
    "throwbak": tag_throwbak,
    "career_voice": tag_career_voice,
    "essays": tag_essays,
    "ais_profile_master": tag_ais_profile_master,
    "ais_master_data": tag_ais_master_data,
}


def tag_message(msg):
    """Dispatch to source-appropriate tagger."""
    source = msg.get("source", "")
    tagger = SOURCE_TAGGERS.get(source)
    if tagger:
        return tagger(msg)
    # Unknown source — try title, then content
    return tag_by_content(msg.get("text", ""), msg.get("word_count", 0))


# ─── MAIN: STREAM-PROCESS CORPUS ────────────────────────────────────

def main():
    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        sys.exit(1)

    register_counts = Counter()
    register_words = Counter()
    source_counts = Counter()
    total = 0
    errors = 0

    print(f"Reading: {INPUT_FILE}")
    print(f"Writing: {OUTPUT_FILE}")
    print()

    with open(INPUT_FILE, "r", encoding="utf-8") as fin, \
         open(OUTPUT_FILE, "w", encoding="utf-8") as fout:

        for line_num, line in enumerate(fin, 1):
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError as e:
                errors += 1
                print(f"  JSON error line {line_num}: {e}")
                # Write line as-is with UNTAGGED
                try:
                    msg = {"text": line, "source": "parse_error"}
                    msg["register"] = "UNTAGGED"
                    fout.write(json.dumps(msg, ensure_ascii=False) + "\n")
                except Exception:
                    pass
                continue

            # Tag the message
            register = tag_message(msg)
            msg["register"] = register

            # Write tagged message — preserve ALL original fields
            fout.write(json.dumps(msg, ensure_ascii=False) + "\n")

            # Track stats
            total += 1
            wc = msg.get("word_count", 0)
            register_counts[register] += 1
            register_words[register] += wc
            source_counts[msg.get("source", "unknown")] += 1

            # Progress every 5,000 messages
            if total % 5000 == 0:
                print(f"  Processed {total:,} messages...")

    # ─── FINAL REPORT ────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"TAGGING COMPLETE")
    print(f"{'='*60}")
    print(f"Total messages tagged: {total:,}")
    print(f"Parse errors: {errors}")
    print()

    total_words = sum(register_words.values())

    print(f"{'Register':<22} {'Messages':>10} {'%':>7} {'Words':>12} {'%':>7}")
    print(f"{'-'*22} {'-'*10} {'-'*7} {'-'*12} {'-'*7}")
    for reg in sorted(register_counts.keys(), key=lambda r: register_counts[r], reverse=True):
        mc = register_counts[reg]
        mp = mc / total * 100 if total else 0
        wc = register_words[reg]
        wp = wc / total_words * 100 if total_words else 0
        print(f"{reg:<22} {mc:>10,} {mp:>6.1f}% {wc:>12,} {wp:>6.1f}%")

    print()
    untagged = register_counts.get("UNTAGGED", 0)
    untagged_pct = untagged / total * 100 if total else 0
    print(f"UNTAGGED rate: {untagged:,} / {total:,} = {untagged_pct:.1f}%")
    if untagged_pct > 30:
        print("⚠  WARNING: UNTAGGED rate exceeds 30% — heuristics need expansion")

    # Check for single-register dominance
    for reg, count in register_counts.items():
        pct = count / total * 100 if total else 0
        if pct > 50:
            print(f"⚠  WARNING: {reg} contains {pct:.1f}% of all messages — likely over-matching")

    # Count registers with > 50 messages
    qualifying = sum(1 for c in register_counts.values() if c > 50)
    print(f"\nRegisters with > 50 messages: {qualifying} / {len(register_counts)}")
    print(f"Source breakdown: {dict(source_counts)}")

    print(f"\nOutput written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
