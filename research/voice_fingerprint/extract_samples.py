#!/usr/bin/env python3
"""
VFP-02: Per-Register Sample Extraction
Extracts 10 random samples per register (>100 messages) for eyeball validation.
"""

import json
import random
import sys
from pathlib import Path
from collections import defaultdict

CORPUS_DIR = Path(r"D:\Projects\SCRVNR\research\voice_fingerprint")
INPUT_FILE = CORPUS_DIR / "tagged_corpus.jsonl"
OUTPUT_MD = CORPUS_DIR / "register_samples.md"

random.seed(42)  # Reproducible samples


def main():
    # Collect messages by register
    by_register = defaultdict(list)

    print("Reading tagged corpus...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            reg = msg.get("register", "UNTAGGED")
            text = msg.get("text", "").strip()
            if text:
                by_register[reg].append(text)

    # Sort registers by count descending
    sorted_regs = sorted(by_register.keys(),
                         key=lambda r: len(by_register[r]), reverse=True)

    md = ["# Register Samples — Eyeball Validation", ""]
    md.append(f"10 random samples per register (registers with > 100 messages).")
    md.append(f"Seed: 42 for reproducibility.\n")

    qualifying = 0
    for reg in sorted_regs:
        msgs = by_register[reg]
        count = len(msgs)
        if count < 100:
            print(f"  {reg}: {count} messages — skipping (< 100)")
            continue

        qualifying += 1
        samples = random.sample(msgs, min(10, count))
        md.append(f"## {reg} ({count:,} messages)\n")
        for i, text in enumerate(samples, 1):
            # Truncate to 200 chars, clean up for markdown
            display = text[:200].replace("\n", " ").replace("\r", "")
            if len(text) > 200:
                display += "..."
            # Escape pipes for markdown tables
            display = display.replace("|", "\\|")
            md.append(f'{i}. "{display}"')
        md.append("")

    md_text = "\n".join(md) + "\n"
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"\nQualifying registers: {qualifying}")
    print(f"Written to: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
