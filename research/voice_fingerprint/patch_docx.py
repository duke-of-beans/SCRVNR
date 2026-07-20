"""Patch: append the 15 misnamed .docx files (actually plain text) to raw_corpus.jsonl"""
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

d = Path(r"D:\Application Intelligence System\Profile_Master")
out = Path(r"D:\Projects\SCRVNR\research\voice_fingerprint\raw_corpus.jsonl")
manifest = Path(r"D:\Projects\SCRVNR\research\voice_fingerprint\corpus_manifest.json")

docx_files = sorted(d.glob("*.docx"))
print(f"Found {len(docx_files)} .docx files to patch")

count = 0
total_words = 0

with open(out, "a", encoding="utf-8") as fh:
    for f in docx_files:
        try:
            text = open(f, "r", encoding="utf-8", errors="replace").read().strip()
        except Exception as e:
            print(f"  FAIL {f.name}: {e}")
            continue
        if len(text) < 20:
            print(f"  SKIP {f.name}: too short")
            continue
        wc = len(text.split())
        mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat()
        record = {
            "source": "ais_profile_master",
            "source_file": f.name,
            "text": text,
            "timestamp": mtime,
            "conversation_title": f.stem,
            "conversation_id": "",
            "word_count": wc,
        }
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        count += 1
        total_words += wc
        print(f"  OK {f.name}: {wc} words")

print(f"\nAppended {count} documents, {total_words:,} words")

# Update manifest
with open(manifest, "r", encoding="utf-8") as mf:
    m = json.load(mf)
m["total_messages"] += count
m["total_words"] += total_words
m["by_source"]["ais_profile_master"]["messages"] += count
m["by_source"]["ais_profile_master"]["words"] += total_words
m["patched_docx"] = {"files": count, "words": total_words}
with open(manifest, "w", encoding="utf-8") as mf:
    json.dump(m, mf, indent=2, ensure_ascii=False)
print(f"Manifest updated: {m['total_messages']} msgs, {m['total_words']:,} words")
