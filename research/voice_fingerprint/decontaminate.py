"""VFP-04 Task 2: Em-dash decontamination of the voice corpus.

David uses hyphens (" - "), never em-dashes. Em-dashes mark Claude/GPT prose
that leaked into "human" messages (pasted AI output, copied AI-generated docs).
ADDITIVE decontamination: adds contamination fields, never deletes messages.
"""
import json
import re
import statistics
import sys
import time
from collections import Counter

from wordfreq import zipf_frequency
from nltk.corpus import stopwords

INPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\tagged_corpus_v2.jsonl"
OUTPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\decontaminated_corpus.jsonl"
REPORT = r"D:\Projects\SCRVNR\research\voice_fingerprint\decontamination_report.md"

EM_DASH = "—"
STOPWORDS = set(stopwords.words("english"))
RE_PUNCT_STRIP = re.compile(r"^[^a-zA-Z]+|[^a-zA-Z]+$")


def rarity_features(text):
    """Rarity features on clean text — same logic as VFP-03 extract_features."""
    words_lower = [w.lower() for w in text.split()]
    content_words = []
    for w in words_lower:
        cleaned = RE_PUNCT_STRIP.sub("", w)
        if cleaned and len(cleaned) >= 3 and cleaned not in STOPWORDS:
            content_words.append(cleaned)
    if len(words_lower) < 3 or not content_words:
        return None
    zipf_scores = [zipf_frequency(cw, "en") for cw in content_words]
    n = len(zipf_scores)
    return {
        "clean_word_count": len(words_lower),
        "clean_mean_zipf": round(statistics.mean(zipf_scores), 3),
        "clean_median_zipf": round(statistics.median(zipf_scores), 3),
        "clean_pct_rare": round(sum(1 for z in zipf_scores if 0 < z < 3.0) / n * 100, 2),
        "clean_pct_very_rare": round(sum(1 for z in zipf_scores if 0 < z < 2.0) / n * 100, 2),
        "clean_pct_unknown": round(sum(1 for z in zipf_scores if z == 0) / n * 100, 2),
    }


def extract_clean_text(text):
    """Keep lines WITHOUT em-dashes — those are likely David's actual words."""
    lines = text.split("\n")
    clean_lines = [ln for ln in lines if EM_DASH not in ln]
    return "\n".join(clean_lines).strip()


def classify(em_count, word_count):
    """Return (contamination_level, decontaminated, weight)."""
    if em_count == 0:
        return "none", False, 1.0
    density = em_count / max(word_count, 1)
    if density > 0.01:
        return "high", True, 0.3
    if density > 0.005:
        return "medium", True, 0.7
    return "low", False, 1.0


def main():
    start = time.time()
    total = 0
    total_em_dashes = 0
    level_counts = Counter()
    register_high = Counter()
    clean_extracted = 0
    clean_failed = 0

    with open(INPUT, "r", encoding="utf-8") as fin, \
         open(OUTPUT, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            total += 1
            text = msg.get("text", "")
            word_count = msg.get("word_count") or len(text.split())
            em_count = text.count(EM_DASH)
            total_em_dashes += em_count

            level, decon, weight = classify(em_count, word_count)
            level_counts[level] += 1
            msg["em_dash_count"] = em_count
            msg["contamination_level"] = level
            msg["decontaminated"] = decon
            msg["weight"] = weight

            if level == "high":
                register_high[msg.get("register", "UNTAGGED")] += 1
                clean_text = extract_clean_text(text)
                if clean_text:
                    msg["clean_text"] = clean_text
                    feats = rarity_features(clean_text)
                    if feats:
                        msg.update(feats)
                    clean_extracted += 1
                else:
                    clean_failed += 1

            fout.write(json.dumps(msg, ensure_ascii=False) + "\n")
            if total % 10000 == 0:
                print(f"  [{total:,}] {time.time() - start:.1f}s")

    flagged = level_counts["high"] + level_counts["medium"] + level_counts["low"]
    weighted_down = level_counts["high"] + level_counts["medium"]
    pct_flagged = flagged / total * 100
    pct_weighted = weighted_down / total * 100

    print(f"\n=== Decontamination Complete ({time.time() - start:.1f}s) ===")
    print(f"Total messages:     {total:,}")
    print(f"Total em-dashes:    {total_em_dashes:,}")
    print(f"HIGH:               {level_counts['high']:,}")
    print(f"MEDIUM:             {level_counts['medium']:,}")
    print(f"LOW:                {level_counts['low']:,}")
    print(f"Clean (none):       {level_counts['none']:,}")
    print(f"Flagged:            {flagged:,} ({pct_flagged:.2f}% of corpus)")
    print(f"Weight-reduced:     {weighted_down:,} ({pct_weighted:.2f}% of corpus)")
    print(f"clean_text OK:      {clean_extracted:,} | failed: {clean_failed:,}")
    print(f"Top HIGH registers: {register_high.most_common(5)}")

    with open(REPORT, "w", encoding="utf-8") as f:
        f.write("# Em-Dash Decontamination Report (VFP-04 Task 2)\n\n")
        f.write(f"Input: tagged_corpus_v2.jsonl ({total:,} messages)\n")
        f.write(f"Output: decontaminated_corpus.jsonl ({total:,} messages — additive, nothing deleted)\n\n")
        f.write("## Why\n\n")
        f.write("David uses hyphens (\" - \"), never em-dashes. The corpus contained ")
        f.write(f"{total_em_dashes:,} em-dashes — markers of Claude/GPT prose leaked into ")
        f.write("\"human\" messages via pasted AI output, copied AI-generated docs, and ")
        f.write("GPT-era conversations.\n\n")
        f.write("## Results\n\n")
        f.write("| Level | Rule (em-dash density) | Messages | % of Corpus | Weight |\n")
        f.write("|-------|------------------------|----------|-------------|--------|\n")
        f.write(f"| HIGH | > 1 per 100 words | {level_counts['high']:,} | {level_counts['high']/total*100:.2f}% | 0.3 |\n")
        f.write(f"| MEDIUM | > 0.5 per 100 words | {level_counts['medium']:,} | {level_counts['medium']/total*100:.2f}% | 0.7 |\n")
        f.write(f"| LOW | any em-dash below 0.5/100w | {level_counts['low']:,} | {level_counts['low']/total*100:.2f}% | 1.0 |\n")
        f.write(f"| none | zero em-dashes | {level_counts['none']:,} | {level_counts['none']/total*100:.2f}% | 1.0 |\n\n")
        f.write(f"**Flagged: {flagged:,} messages ({pct_flagged:.2f}% of corpus). ")
        f.write(f"Weight-reduced (HIGH+MEDIUM): {weighted_down:,} ({pct_weighted:.2f}%).**\n\n")
        f.write("## Clean-Text Extraction (HIGH messages)\n\n")
        f.write("For HIGH-contamination messages, lines containing em-dashes (likely quoted AI prose) ")
        f.write("were stripped; remaining lines stored as `clean_text` with recomputed rarity features ")
        f.write("(`clean_mean_zipf`, `clean_pct_rare`, etc.).\n\n")
        f.write(f"- clean_text extracted: {clean_extracted:,}\n")
        f.write(f"- no clean lines recoverable: {clean_failed:,}\n\n")
        f.write("## HIGH Contamination by Register\n\n")
        f.write("| Register | HIGH messages |\n|----------|---------------|\n")
        for reg, cnt in register_high.most_common():
            f.write(f"| {reg} | {cnt:,} |\n")
        f.write(f"\nGenerated by decontaminate.py — {time.strftime('%Y-%m-%d %H:%M')}\n")

    if pct_weighted > 20.0:
        print(f"\nABORT: decontamination weight-reduces {pct_weighted:.2f}% of corpus (> 20% threshold)")
        sys.exit(2)
    print(f"\nReport written: {REPORT}")


if __name__ == "__main__":
    main()
