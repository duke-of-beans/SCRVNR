#!/usr/bin/env python3
"""
VFP-02: Register Distribution Analysis
Reads tagged_corpus.jsonl and produces cross-tabulation,
volume stats, temporal coverage, UNTAGGED analysis, and candidate new registers.
"""

import json
import sys
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime
import statistics

CORPUS_DIR = Path(r"D:\Projects\SCRVNR\research\voice_fingerprint")
INPUT_FILE = CORPUS_DIR / "tagged_corpus.jsonl"
OUTPUT_JSON = CORPUS_DIR / "register_distribution.json"
OUTPUT_MD = CORPUS_DIR / "register_distribution.md"


def parse_timestamp(ts_str):
    """Parse ISO timestamp, return datetime or None."""
    if not ts_str:
        return None
    try:
        # Handle various ISO formats
        ts_str = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(ts_str)
    except (ValueError, TypeError):
        return None


def main():
    # Accumulators
    reg_source = defaultdict(Counter)      # register → {source: count}
    reg_msgs = Counter()                   # register → message count
    reg_words = Counter()                  # register → word count
    reg_lengths = defaultdict(list)        # register → [word_counts]
    reg_earliest = {}                      # register → earliest timestamp
    reg_latest = {}                        # register → latest timestamp
    untagged_titles = Counter()            # conversation_title → count (for UNTAGGED)
    total = 0

    print("Reading tagged corpus...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            total += 1

            reg = msg.get("register", "UNTAGGED")
            src = msg.get("source", "unknown")
            wc = msg.get("word_count", 0)
            ts = parse_timestamp(msg.get("timestamp"))

            reg_source[reg][src] += 1
            reg_msgs[reg] += 1
            reg_words[reg] += wc
            reg_lengths[reg].append(wc)

            if ts:
                if reg not in reg_earliest or ts < reg_earliest[reg]:
                    reg_earliest[reg] = ts
                if reg not in reg_latest or ts > reg_latest[reg]:
                    reg_latest[reg] = ts

            if reg == "UNTAGGED":
                title = msg.get("conversation_title", "") or "(no title)"
                if title.strip():
                    untagged_titles[title] += 1

    print(f"Total messages: {total:,}")

    # All sources present in the data
    all_sources = sorted(set(
        src for counts in reg_source.values() for src in counts
    ))
    all_registers = sorted(reg_msgs.keys(), key=lambda r: reg_msgs[r], reverse=True)
    total_words = sum(reg_words.values())

    # ─── BUILD OUTPUT STRUCTURES ──────────────────────────────────────
    distribution = {
        "total_messages": total,
        "total_words": total_words,
        "registers": {},
        "cross_tabulation": {},
        "untagged_analysis": {},
        "candidate_new_registers": []
    }

    for reg in all_registers:
        lengths = reg_lengths[reg]
        mc = reg_msgs[reg]
        wc = reg_words[reg]
        mean_len = statistics.mean(lengths) if lengths else 0
        median_len = statistics.median(lengths) if lengths else 0
        earliest = reg_earliest.get(reg)
        latest = reg_latest.get(reg)

        distribution["registers"][reg] = {
            "message_count": mc,
            "message_pct": round(mc / total * 100, 2),
            "word_count": wc,
            "word_pct": round(wc / total_words * 100, 2) if total_words else 0,
            "mean_message_length": round(mean_len, 1),
            "median_message_length": round(median_len, 1),
            "earliest": earliest.isoformat() if earliest else None,
            "latest": latest.isoformat() if latest else None,
        }

        # Cross-tabulation row
        distribution["cross_tabulation"][reg] = {
            src: reg_source[reg].get(src, 0) for src in all_sources
        }

    # UNTAGGED analysis: top 20 titles
    top_untagged = untagged_titles.most_common(20)
    distribution["untagged_analysis"]["top_titles"] = [
        {"title": t, "count": c} for t, c in top_untagged
    ]

    # Candidate new registers: titles appearing 50+ times in UNTAGGED
    candidates = [(t, c) for t, c in untagged_titles.items()
                  if c >= 50 and t not in ("(no title)", "", "Untitled")]
    distribution["candidate_new_registers"] = [
        {"title": t, "count": c} for t, c in sorted(candidates, key=lambda x: -x[1])
    ]

    # ─── WRITE JSON ──────────────────────────────────────────────────
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(distribution, f, indent=2, ensure_ascii=False, default=str)
    print(f"JSON written: {OUTPUT_JSON}")

    # ─── BUILD MARKDOWN ──────────────────────────────────────────────
    md = []
    md.append("# Register Distribution Analysis")
    md.append(f"\nTotal messages: **{total:,}** | Total words: **{total_words:,}**\n")

    # Volume stats table
    md.append("## Volume Stats by Register\n")
    md.append(f"| Register | Messages | Msg % | Words | Word % | Mean Len | Median Len | Earliest | Latest |")
    md.append(f"|----------|----------|-------|-------|--------|----------|------------|----------|--------|")
    for reg in all_registers:
        d = distribution["registers"][reg]
        earliest_str = d["earliest"][:10] if d["earliest"] else "—"
        latest_str = d["latest"][:10] if d["latest"] else "—"
        md.append(f"| {reg} | {d['message_count']:,} | {d['message_pct']}% | {d['word_count']:,} | {d['word_pct']}% | {d['mean_message_length']} | {d['median_message_length']} | {earliest_str} | {latest_str} |")


    # Cross-tabulation table
    md.append("\n## Register × Source Cross-Tabulation\n")
    header = "| Register | " + " | ".join(all_sources) + " | Total |"
    sep = "|----------|" + "|".join(["-------" for _ in all_sources]) + "|-------|"
    md.append(header)
    md.append(sep)
    for reg in all_registers:
        cells = [str(reg_source[reg].get(src, 0)) for src in all_sources]
        total_reg = reg_msgs[reg]
        md.append(f"| {reg} | " + " | ".join(cells) + f" | {total_reg:,} |")

    # UNTAGGED analysis
    md.append("\n## UNTAGGED Analysis — Top 20 Conversation Titles\n")
    md.append("| # | Title | Count |")
    md.append("|---|-------|-------|")
    for i, (title, count) in enumerate(top_untagged, 1):
        safe_title = title.replace("|", "\\|")[:80]
        md.append(f"| {i} | {safe_title} | {count} |")

    # Candidate new registers
    if candidates:
        md.append("\n## Candidate New Registers\n")
        md.append("Conversation titles appearing 50+ times in UNTAGGED:\n")
        for t, c in sorted(candidates, key=lambda x: -x[1]):
            md.append(f"- **{t}** ({c} occurrences)")
    else:
        md.append("\n## Candidate New Registers\n")
        md.append("No single conversation title appears 50+ times in UNTAGGED.")


    # Write markdown
    md_text = "\n".join(md) + "\n"
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(md_text)
    print(f"Markdown written: {OUTPUT_MD}")

    # Print to stdout
    print()
    print(md_text)


if __name__ == "__main__":
    main()
