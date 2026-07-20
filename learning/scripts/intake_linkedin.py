"""
LinkedIn Intake — SCRVNR v2.0 Corpus Expansion

Processes LinkedIn message export and identity asset into SCRVNR corpus format.

Sources:
  1. messages.csv — LinkedIn DM history (filter to David-authored only)
  2. Private_identity_asset.csv — LinkedIn profile/identity data

Outputs:
  - learning/samples/linkedin_corpus.jsonl — David's messages in corpus format
  - Updates intake_log in voice.db

Run:
    D:\\Programs\\Python312\\python.exe D:\\Projects\\SCRVNR\\learning\\scripts\\intake_linkedin.py
"""

import csv
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from research.voice_fingerprint.secret_scrubber import scrub

MESSAGES_CSV = PROJECT_ROOT / "learning" / "samples" / "messages.csv"
IDENTITY_CSV = PROJECT_ROOT / "learning" / "samples" / "Private_identity_asset.csv"
OUTPUT_JSONL = PROJECT_ROOT / "research" / "voice_fingerprint" / "linkedin_corpus.jsonl"
DB_PATH = PROJECT_ROOT / "learning" / "voice.db"

DAVID_NAMES = {"David Kirsch", "David", "david kirsch"}
WORD_PATTERN = re.compile(r"[a-zA-Z']+")
MIN_WORDS = 5  # minimum words for a message to be useful


def generate_msg_id(text: str, source: str, idx: int) -> str:
    """Generate deterministic msg_id."""
    combined = f"{source}:{idx}:{text[:100]}"
    return f"li_{hashlib.md5(combined.encode()).hexdigest()[:10]}"


def classify_register(text: str, word_count: int) -> str:
    """Classify LinkedIn message into a register."""
    lower = text.lower()

    # Short casual messages
    if word_count < 15:
        return "CASUAL"

    # Professional/networking indicators
    networking_signals = ["opportunity", "role", "position", "hiring", "team",
                          "company", "experience", "portfolio", "project",
                          "connect", "reaching out", "introduction", "resume",
                          "interview", "collaborate"]
    net_count = sum(1 for s in networking_signals if s in lower)
    if net_count >= 2:
        return "PROFESSIONAL"

    # Technical discussion
    tech_signals = ["api", "deploy", "code", "build", "server", "database",
                     "github", "vercel", "supabase", "typescript", "python",
                     "endpoint", "pipeline", "architecture"]
    tech_count = sum(1 for s in tech_signals if s in lower)
    if tech_count >= 2:
        return "TECH"

    # Default for LinkedIn
    return "PROFESSIONAL"


def process_messages():
    """Process messages.csv — extract David's messages."""
    if not MESSAGES_CSV.exists():
        print(f"  NOT FOUND: {MESSAGES_CSV}")
        return []

    messages = []
    total_rows = 0
    david_rows = 0
    skipped_short = 0
    skipped_empty = 0

    with open(str(MESSAGES_CSV), 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            total_rows += 1
            sender = row.get('FROM', '').strip()

            if sender not in DAVID_NAMES:
                continue

            david_rows += 1
            content = row.get('CONTENT', '').strip()

            if not content:
                skipped_empty += 1
                continue

            # Scrub secrets
            content = scrub(content)

            words = WORD_PATTERN.findall(content)
            word_count = len(words)

            if word_count < MIN_WORDS:
                skipped_short += 1
                continue

            register = classify_register(content, word_count)
            msg_id = generate_msg_id(content, 'linkedin_dm', idx)
            date = row.get('DATE', '')

            messages.append({
                'msg_id': msg_id,
                'text': content,
                'source': 'linkedin_dm',
                'register': register,
                'word_count': word_count,
                'date': date,
                'to': row.get('TO', ''),
            })

    print(f"  Messages CSV: {total_rows} total rows, {david_rows} from David")
    print(f"  Kept: {len(messages)}, skipped: {skipped_short} short + {skipped_empty} empty")
    return messages


def process_identity():
    """Process Private_identity_asset.csv — extract text content."""
    if not IDENTITY_CSV.exists():
        print(f"  NOT FOUND: {IDENTITY_CSV}")
        return []

    messages = []

    with open(str(IDENTITY_CSV), 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            # The raw text column contains David's professional writing
            raw_text = row.get('Private Identity Asset Raw Text', '').strip()
            if not raw_text:
                continue

            # Scrub secrets
            raw_text = scrub(raw_text)

            # Split into paragraphs for individual messages
            paragraphs = [p.strip() for p in raw_text.split('\n\n') if p.strip()]

            for pi, para in enumerate(paragraphs):
                words = WORD_PATTERN.findall(para)
                word_count = len(words)

                if word_count < MIN_WORDS:
                    continue

                msg_id = generate_msg_id(para, 'linkedin_identity', idx * 100 + pi)

                messages.append({
                    'msg_id': msg_id,
                    'text': para,
                    'source': 'linkedin_identity',
                    'register': 'PROFESSIONAL',
                    'word_count': word_count,
                    'date': '',
                    'to': '',
                })

    print(f"  Identity CSV: {len(messages)} paragraphs extracted")
    return messages


def write_corpus(messages):
    """Write to JSONL and update intake_log."""
    # Write JSONL
    with open(str(OUTPUT_JSONL), 'w', encoding='utf-8') as f:
        for msg in messages:
            f.write(json.dumps(msg, ensure_ascii=False) + '\n')
    print(f"\n  Wrote {len(messages)} messages to {OUTPUT_JSONL.name}")

    # Update intake_log in voice.db
    if not DB_PATH.exists():
        print(f"  WARNING: voice.db not found, skipping intake_log update")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    inserted = 0
    for msg in messages:
        try:
            cur.execute("""
            INSERT OR IGNORE INTO intake_log (msg_id, source, register, word_count, weight)
            VALUES (?, ?, ?, ?, ?)
            """, (msg['msg_id'], msg['source'], msg['register'], msg['word_count'], 1.0))
            if cur.rowcount > 0:
                inserted += 1
        except sqlite3.OperationalError:
            break

    conn.commit()
    conn.close()
    print(f"  Logged {inserted} new messages to intake_log")


def main():
    print("SCRVNR LinkedIn Intake")
    print("=" * 50)

    print("\n[1] Processing messages.csv...")
    dm_messages = process_messages()

    print("\n[2] Processing Private_identity_asset.csv...")
    identity_messages = process_identity()

    all_messages = dm_messages + identity_messages

    if not all_messages:
        print("\nNo messages to process.")
        return

    # Register distribution
    registers = {}
    for msg in all_messages:
        reg = msg['register']
        registers[reg] = registers.get(reg, 0) + 1

    print(f"\n[3] Register distribution:")
    for reg, count in sorted(registers.items(), key=lambda x: -x[1]):
        print(f"  {reg}: {count}")

    total_words = sum(m['word_count'] for m in all_messages)
    print(f"\n  Total: {len(all_messages)} messages, {total_words:,} words")

    print("\n[4] Writing corpus...")
    write_corpus(all_messages)

    print("\nDone.")


if __name__ == "__main__":
    main()
