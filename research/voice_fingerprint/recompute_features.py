"""VFP-04 Task 4: Recompute features for messages modified in Tasks 2-3.

Streams final_corpus.jsonl and features.jsonl in parallel (line-aligned since
Phase 3). For rescued messages: update register metadata. For HIGH-contamination
messages with clean_text: recompute ALL features on clean_text using the exact
VFP-03 extraction logic (imported from extract_features.py). All other records
pass through unchanged. Contamination weight metadata is propagated to every
record so build_profile.py can stream features_final.jsonl alone.
"""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_features import extract_features

CORPUS = r"D:\Projects\SCRVNR\research\voice_fingerprint\final_corpus.jsonl"
FEATURES = r"D:\Projects\SCRVNR\research\voice_fingerprint\features.jsonl"
OUTPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\features_final.jsonl"


def main():
    start = time.time()
    total = 0
    recomputed = 0
    register_updated = 0
    passthrough = 0

    with open(CORPUS, "r", encoding="utf-8") as fc, \
         open(FEATURES, "r", encoding="utf-8") as ff, \
         open(OUTPUT, "w", encoding="utf-8") as fout:
        for corpus_line, feat_line in zip(fc, ff):
            corpus_line = corpus_line.strip()
            feat_line = feat_line.strip()
            if not corpus_line or not feat_line:
                continue
            msg = json.loads(corpus_line)
            rec = json.loads(feat_line)
            total += 1

            # Alignment sanity check — files must be line-parallel
            if msg.get("conversation_id") != rec.get("conversation_id") or \
               msg.get("timestamp") != rec.get("timestamp"):
                print(f"ABORT: line {total} misaligned "
                      f"({msg.get('conversation_id')} vs {rec.get('conversation_id')})")
                sys.exit(2)

            changed = False
            # Task 3 change: register reclassification
            if msg.get("rescued"):
                rec["register"] = msg["register"]
                rec["register_original"] = msg.get("register_original")
                rec["rescued"] = True
                register_updated += 1
                changed = True

            # Task 2 change: HIGH contamination with recovered clean_text —
            # recompute all features on David's isolated prose
            if msg.get("contamination_level") == "high" and msg.get("clean_text"):
                feats = extract_features(msg["clean_text"])
                rec.update(feats)
                rec["features_recomputed"] = True
                recomputed += 1
                changed = True

            if not changed:
                passthrough += 1

            # Propagate contamination weighting to every record
            rec["contamination_level"] = msg.get("contamination_level", "none")
            rec["weight"] = msg.get("weight", 1.0)

            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
            if total % 10000 == 0:
                print(f"  [{total:,}] {time.time() - start:.1f}s")

    print(f"\n=== Feature Recomputation Complete ({time.time() - start:.1f}s) ===")
    print(f"Total records:              {total:,}")
    print(f"Features recomputed:        {recomputed:,}")
    print(f"Register updates (rescued): {register_updated:,}")
    print(f"Unchanged passthrough:      {passthrough:,}")


if __name__ == "__main__":
    main()
