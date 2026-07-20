"""VFP-03 Task 4: Global voice signature extraction."""
import json
import time
import math
from collections import defaultdict, Counter

INPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\features.jsonl"
CORPUS = r"D:\Projects\SCRVNR\research\voice_fingerprint\tagged_corpus_v2.jsonl"
OUT_JSON = r"D:\Projects\SCRVNR\research\voice_fingerprint\voice_signature.json"
OUT_MD = r"D:\Projects\SCRVNR\research\voice_fingerprint\voice_signature.md"

def main():
    start = time.time()

    # --- Pass 1: Collect rarest words per message, contraction/profanity by register ---
    all_mean_zipf = []
    word_zipf_accum = defaultdict(list)  # word -> list of zipf scores
    word_msg_count = defaultdict(int)    # word -> number of messages containing it
    word_corpus_count = Counter()        # word -> total occurrences

    reg_contraction = defaultdict(list)
    reg_profanity = defaultdict(list)
    em_dash_total = 0
    total_messages = 0

    print("Pass 1: Reading features.jsonl for rarity + style metrics...")
    with open(INPUT, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            rec = json.loads(line)
            total_messages += 1
            reg = rec.get("register", "UNKNOWN")

            mz = rec.get("mean_zipf")
            if mz is not None:
                all_mean_zipf.append(float(mz))

            cr = rec.get("contraction_rate")
            if cr is not None:
                reg_contraction[reg].append(float(cr))

            pr = rec.get("profanity_rate")
            if pr is not None:
                reg_profanity[reg].append(float(pr))

            em = rec.get("em_dash_count", 0)
            em_dash_total += em

    print(f"  {total_messages:,} messages loaded from features.jsonl")

    # --- Pass 2: Read corpus for word-level rarity analysis ---
    print("Pass 2: Reading corpus for word-level rarity...")
    from wordfreq import zipf_frequency
    from nltk.corpus import stopwords
    import re

    STOPWORDS = set(stopwords.words("english"))
    RE_PUNCT = re.compile(r"^[^a-zA-Z]+|[^a-zA-Z]+$")

    msg_idx = 0
    with open(CORPUS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            msg = json.loads(line)
            msg_idx += 1
            text = msg.get("text", "")
            if not text: continue

            words_in_msg = set()
            for w in text.split():
                cleaned = RE_PUNCT.sub("", w.lower())
                if not cleaned or len(cleaned) < 3 or cleaned in STOPWORDS:
                    continue
                word_corpus_count[cleaned] += 1
                if cleaned not in words_in_msg:
                    words_in_msg.add(cleaned)
                    word_msg_count[cleaned] += 1
                    z = zipf_frequency(cleaned, "en")
                    if z > 0:
                        word_zipf_accum[cleaned].append(z)

            if msg_idx % 10000 == 0:
                print(f"  [{msg_idx:,} messages]")

    print(f"  {msg_idx:,} messages scanned, {len(word_corpus_count):,} unique words")

    # --- Compute signature metrics ---
    print("\nComputing voice signature...")

    # 1. Global rarity percentile
    global_mean_zipf = sum(all_mean_zipf) / len(all_mean_zipf) if all_mean_zipf else 0

    # 2. Top 50 rarest words David uses (lowest nonzero zipf, 5+ messages)
    rare_candidates = []
    for word, zipf_list in word_zipf_accum.items():
        if word_msg_count[word] >= 5:
            mean_z = sum(zipf_list) / len(zipf_list)
            rare_candidates.append((word, mean_z, word_msg_count[word], word_corpus_count[word]))
    rare_candidates.sort(key=lambda x: x[1])
    top_50_rarest = rare_candidates[:50]

    # 3. Top 50 words rare in English but common for David (zipf < 3.5, high corpus freq)
    rarity_spikes = []
    for word, zipf_list in word_zipf_accum.items():
        mean_z = sum(zipf_list) / len(zipf_list)
        if mean_z < 3.5 and word_corpus_count[word] >= 10:
            rarity_spikes.append((word, mean_z, word_corpus_count[word], word_msg_count[word]))
    rarity_spikes.sort(key=lambda x: -x[2])  # sort by David's usage frequency
    top_50_spikes = rarity_spikes[:50]

    # 4. Em-dash audit
    em_dash_audit = {
        "total_em_dashes": em_dash_total,
        "messages_checked": total_messages,
        "per_1000_messages": round(em_dash_total / total_messages * 1000, 2) if total_messages else 0,
    }

    # 5. Contraction rate by register
    contraction_by_reg = {}
    for reg in sorted(reg_contraction.keys()):
        vals = reg_contraction[reg]
        contraction_by_reg[reg] = {
            "mean": round(sum(vals)/len(vals), 3),
            "n": len(vals),
        }

    # 6. Profanity distribution by register
    profanity_by_reg = {}
    for reg in sorted(reg_profanity.keys()):
        vals = reg_profanity[reg]
        profanity_by_reg[reg] = {
            "mean": round(sum(vals)/len(vals), 3),
            "n": len(vals),
        }

    # --- Build output ---
    signature = {
        "global_rarity": {
            "david_mean_zipf": round(global_mean_zipf, 4),
            "storyscope_human_mean_percentile": 0.71,
            "storyscope_ai_mean_percentile": 0.49,
            "note": "Zipf and percentile are different scales — relative position is informative, not directly comparable",
        },
        "top_50_rarest_words": [
            {"word": w, "mean_zipf": round(z, 3), "messages": m, "occurrences": o}
            for w, z, m, o in top_50_rarest
        ],
        "top_50_rarity_spikes": [
            {"word": w, "mean_zipf": round(z, 3), "occurrences": o, "messages": m}
            for w, z, o, m in top_50_spikes
        ],
        "em_dash_audit": em_dash_audit,
        "contraction_rate_by_register": contraction_by_reg,
        "profanity_by_register": profanity_by_reg,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(signature, f, indent=2, ensure_ascii=False)
    print(f"Wrote {OUT_JSON}")

    # --- Write markdown ---
    with open(OUT_MD, "w", encoding="utf-8") as md:
        md.write("# David's Voice Signature\n\n")
        md.write("## Global Rarity Profile\n\n")
        md.write(f"- **David's mean Zipf**: {global_mean_zipf:.4f}\n")
        md.write(f"- StoryScope human mean percentile: 0.71\n")
        md.write(f"- StoryScope AI mean percentile: 0.49\n")
        md.write(f"- Note: Different scales — relative position informative, not directly comparable\n\n")

        md.write("## Top 50 Rarest Words David Uses Regularly (5+ messages)\n\n")
        md.write("| # | Word | Mean Zipf | Messages | Occurrences |\n")
        md.write("|---|------|----------|----------|-------------|\n")
        for i, (w, z, m, o) in enumerate(top_50_rarest, 1):
            md.write(f"| {i} | {w} | {z:.3f} | {m} | {o} |\n")

        md.write("\n## Top 50 Rarity Spikes (rare in English, common for David)\n\n")
        md.write("| # | Word | Mean Zipf | Occurrences | Messages |\n")
        md.write("|---|------|----------|-------------|----------|\n")
        for i, (w, z, o, m) in enumerate(top_50_spikes, 1):
            md.write(f"| {i} | {w} | {z:.3f} | {o} | {m} |\n")

        md.write("\n## Em-Dash Audit\n\n")
        md.write(f"- Total em-dashes in corpus: **{em_dash_total}**\n")
        md.write(f"- Per 1,000 messages: {em_dash_audit['per_1000_messages']}\n")
        if em_dash_total > 50:
            md.write("- **WARNING**: Significant em-dash usage detected. Some messages may be Claude-contaminated.\n")
        else:
            md.write("- Clean: near-zero em-dash usage confirms pure-David corpus.\n")

        md.write("\n## Contraction Rate by Register\n\n")
        md.write("| Register | Mean Rate | N |\n")
        md.write("|----------|----------|---|\n")
        for reg, data in sorted(contraction_by_reg.items(), key=lambda x: -x[1]["mean"]):
            md.write(f"| {reg} | {data['mean']:.3f} | {data['n']:,} |\n")

        md.write("\n## Profanity Distribution by Register\n\n")
        md.write("| Register | Mean Rate (per 1000) | N |\n")
        md.write("|----------|---------------------|---|\n")
        for reg, data in sorted(profanity_by_reg.items(), key=lambda x: -x[1]["mean"]):
            md.write(f"| {reg} | {data['mean']:.3f} | {data['n']:,} |\n")

    print(f"Wrote {OUT_MD}")
    elapsed = time.time() - start
    print(f"\nDone in {elapsed:.1f}s")

    with open(OUT_MD, "r", encoding="utf-8") as f:
        print(f.read())

if __name__ == "__main__":
    main()
