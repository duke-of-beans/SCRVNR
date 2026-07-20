"""
Add stable, deterministic msg_id to corpus and features files.
ID scheme: msg_{sha256(source + timestamp + first_50_chars_of_text)[:12]}

This creates:
  - final_corpus_v2.jsonl (corpus with msg_id)
  - features_v2.jsonl (features with msg_id)
  - Cross-validates that every features msg_id exists in corpus
"""

import json
import hashlib
from pathlib import Path


def compute_msg_id(source: str, timestamp: str, text: str) -> str:
    """Deterministic message ID from source + timestamp + first 50 chars."""
    key = f"{source}{timestamp}{text[:50]}"
    h = hashlib.sha256(key.encode('utf-8', errors='replace')).hexdigest()[:12]
    return f"msg_{h}"


def main():
    base = Path(__file__).parent
    corpus_in = base / "final_corpus.jsonl"
    features_in = base / "features_final.jsonl"
    corpus_out = base / "final_corpus_v2.jsonl"
    features_out = base / "features_v2.jsonl"

    # Step 1: Read corpus, compute msg_id, write v2
    print("Step 1: Adding msg_id to final_corpus.jsonl...")
    corpus_ids = []
    id_set = set()
    duplicates = 0

    with open(corpus_in, 'r', encoding='utf-8') as fin, \
         open(corpus_out, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            source = msg.get('source', '')
            timestamp = msg.get('timestamp', '')
            text = msg.get('text', '')
            mid = compute_msg_id(source, timestamp, text)

            if mid in id_set:
                duplicates += 1
            id_set.add(mid)

            msg['msg_id'] = mid
            corpus_ids.append(mid)
            fout.write(json.dumps(msg, ensure_ascii=False) + '\n')

    print(f"  Corpus: {len(corpus_ids)} messages, {duplicates} duplicate IDs")

    # Step 2: Read features, add matching msg_id by line position, write v2
    print("Step 2: Adding msg_id to features_final.jsonl...")
    feature_count = 0
    feature_ids = set()

    with open(features_in, 'r', encoding='utf-8') as fin, \
         open(features_out, 'w', encoding='utf-8') as fout:
        for i, line in enumerate(fin):
            line = line.strip()
            if not line:
                continue
            feat = json.loads(line)
            if i < len(corpus_ids):
                mid = corpus_ids[i]
            else:
                # Fallback: compute from feature data
                source = feat.get('source', '')
                timestamp = feat.get('timestamp', '')
                text = feat.get('text', '')
                mid = compute_msg_id(source, timestamp, text)
            feat['msg_id'] = mid
            feature_ids.add(mid)
            feature_count += 1
            fout.write(json.dumps(feat, ensure_ascii=False) + '\n')

    print(f"  Features: {feature_count} entries")

    # Step 3: Cross-check
    print("Step 3: Cross-validation...")
    corpus_id_set = set(corpus_ids)
    missing = feature_ids - corpus_id_set
    if missing:
        print(f"  FAIL: {len(missing)} feature msg_ids not in corpus")
    else:
        print("  PASS: All feature msg_ids exist in corpus")

    # Summary
    print(f"\nSummary:")
    print(f"  Total IDs generated: {len(corpus_ids)}")
    print(f"  Duplicates found: {duplicates}")
    print(f"  Verification: {'PASS' if not missing else 'FAIL'}")


if __name__ == "__main__":
    main()
