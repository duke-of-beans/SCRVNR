"""
SCRVNR Voice Fingerprint — Phase 1: Corpus Assembly
Extracts David's authored text from all source corpora.

Sources:
  - Claude chat exports (b0 + b1, ~1.84GB) — sender == "human"
  - GPT chat exports (17 JSON files, ~187MB) — author.role == "user"
  - SMS export (XML, 3191 messages) — type == "2" (sent by David)
  - AIS Profile Master docs (~40 files)
  - AIS Master Data docs (~15 files)
  - Career Voice & Writing docs (~20 files)
  - Throwbak records (~150+ YAML files)

Output:
  - raw_corpus.jsonl  (one JSON object per message/document)
  - corpus_manifest.json  (summary statistics)
"""

import ijson
import json
import os
import sys
import glob
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict
import traceback

OUTPUT_DIR = Path(r"D:\Projects\SCRVNR\research\voice_fingerprint")
CORPUS_FILE = OUTPUT_DIR / "raw_corpus.jsonl"
MANIFEST_FILE = OUTPUT_DIR / "corpus_manifest.json"

# Source paths
CLAUDE_EXPORTS = [
    Path(r"D:\Meta\claude_export\b0\conversations.json"),
    Path(r"D:\Meta\claude_export\b1\conversations.json"),
]
GPT_EXPORT_DIR = Path(r"D:\Personal\GPT Data")
SMS_FILE = Path(r"D:\OneDrive\Downloads\sms-20260508124842.xml")
AIS_PROFILE_DIR = Path(r"D:\Application Intelligence System\Profile_Master")
AIS_MASTER_DIR = Path(r"D:\Application Intelligence System\Master_Data")
CAREER_VOICE_DIR = Path(r"D:\Career\Voice-and-Writing")
THROWBAK_DIR = Path(r"D:\Projects\Throwbak\record")
ESSAY_DIR = Path(r"D:\Projects\davidkirsch-me\writing")

# Counters
stats = defaultdict(lambda: {"messages": 0, "words": 0, "errors": 0})
total_messages = 0
total_words = 0

def word_count(text):
    """Simple whitespace word count."""
    if not text:
        return 0
    return len(text.split())


def write_record(fh, record):
    """Write a single corpus record to JSONL output."""
    global total_messages, total_words
    text = record.get("text", "")
    if not text or not text.strip():
        return
    wc = word_count(text)
    record["word_count"] = wc
    fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    total_messages += 1
    total_words += wc
    src = record["source"]
    stats[src]["messages"] += 1
    stats[src]["words"] += wc


# ── CLAUDE EXPORT PARSER (streaming via ijson) ──────────────────────

def extract_claude(fh):
    """Stream-parse Claude conversation exports, extract human messages."""
    for export_path in CLAUDE_EXPORTS:
        if not export_path.exists():
            print(f"  [SKIP] {export_path} not found")
            continue
        label = export_path.parent.name  # b0 or b1
        print(f"  Parsing Claude export {label} ({export_path.stat().st_size / 1e9:.2f} GB)...")
        conv_count = 0
        msg_count = 0
        try:
            with open(export_path, "r", encoding="utf-8") as f:
                # ijson streams through the top-level array
                # Each item is a conversation object
                for conv in ijson.items(f, "item"):
                    conv_count += 1
                    conv_title = conv.get("name", "")
                    conv_id = conv.get("uuid", "")
                    for msg in conv.get("chat_messages", []):
                        if msg.get("sender") != "human":
                            continue
                        text = msg.get("text", "")
                        if not text:
                            # Try content array
                            for c in msg.get("content", []):
                                if c.get("type") == "text" and c.get("text"):
                                    text = c["text"]
                                    break
                        if not text:
                            continue
                        created = msg.get("created_at", "")
                        write_record(fh, {
                            "source": "claude_chat",
                            "source_file": f"claude_{label}",
                            "text": text,
                            "timestamp": created,
                            "conversation_title": conv_title,
                            "conversation_id": conv_id,
                        })
                        msg_count += 1
                    if conv_count % 100 == 0:
                        print(f"    ... {conv_count} conversations, {msg_count} human messages so far")
        except Exception as e:
            print(f"  [ERROR] Claude {label}: {e}")
            stats["claude_chat"]["errors"] += 1
            traceback.print_exc()
        print(f"  Done: {label} — {conv_count} conversations, {msg_count} human messages")


# ── GPT EXPORT PARSER (tree-walk mapping structure) ─────────────────

def extract_gpt(fh):
    """Parse GPT conversation exports, walk mapping tree for user messages."""
    gpt_files = sorted(GPT_EXPORT_DIR.glob("conversations-*.json"))
    if not gpt_files:
        print("  [SKIP] No GPT export files found")
        return
    print(f"  Found {len(gpt_files)} GPT export files")

    for gpt_file in gpt_files:
        fname = gpt_file.name
        print(f"  Parsing {fname} ({gpt_file.stat().st_size / 1e6:.1f} MB)...")
        conv_count = 0
        msg_count = 0
        try:
            with open(gpt_file, "r", encoding="utf-8") as f:
                conversations = json.load(f)
            for conv in conversations:
                conv_count += 1
                conv_title = conv.get("title", "")
                conv_id = conv.get("conversation_id", conv.get("id", ""))
                mapping = conv.get("mapping", {})
                if not mapping:
                    continue
                for node_id, node in mapping.items():
                    message = node.get("message")
                    if not message:
                        continue
                    author = message.get("author", {})
                    if author.get("role") != "user":
                        continue
                    content = message.get("content", {})
                    parts = content.get("parts", [])
                    # Join text parts, skip non-string (image refs etc)
                    text_parts = [p for p in parts if isinstance(p, str)]
                    text = "\n".join(text_parts).strip()
                    if not text:
                        continue
                    create_time = message.get("create_time")
                    ts = ""
                    if create_time:
                        try:
                            ts = datetime.fromtimestamp(create_time, tz=timezone.utc).isoformat()
                        except (ValueError, OSError):
                            ts = str(create_time)
                    write_record(fh, {
                        "source": "gpt_chat",
                        "source_file": fname,
                        "text": text,
                        "timestamp": ts,
                        "conversation_title": conv_title,
                        "conversation_id": conv_id,
                    })
                    msg_count += 1
            if conv_count % 50 == 0 or True:
                print(f"    {fname}: {conv_count} conversations, {msg_count} user messages")
        except Exception as e:
            print(f"  [ERROR] GPT {fname}: {e}")
            stats["gpt_chat"]["errors"] += 1
            traceback.print_exc()


# ── SMS PARSER (XML) ────────────────────────────────────────────────

def extract_sms(fh):
    """Parse SMS Backup & Restore XML. type=2 = sent by David."""
    if not SMS_FILE.exists():
        print("  [SKIP] SMS file not found")
        return
    print(f"  Parsing SMS export ({SMS_FILE.stat().st_size / 1e6:.1f} MB)...")
    sent_count = 0
    received_count = 0
    try:
        tree = ET.parse(str(SMS_FILE))
        root = tree.getroot()
        for sms in root.findall("sms"):
            sms_type = sms.get("type", "")
            if sms_type == "1":
                received_count += 1
                continue  # received, not David's voice
            if sms_type != "2":
                continue  # skip MMS, drafts, etc.
            body = sms.get("body", "").strip()
            if not body:
                continue
            contact = sms.get("contact_name", "Unknown")
            readable_date = sms.get("readable_date", "")
            date_ms = sms.get("date", "")
            ts = ""
            if date_ms:
                try:
                    ts = datetime.fromtimestamp(int(date_ms) / 1000, tz=timezone.utc).isoformat()
                except (ValueError, OSError):
                    ts = readable_date
            write_record(fh, {
                "source": "sms",
                "source_file": "sms_export",
                "text": body,
                "timestamp": ts,
                "conversation_title": f"SMS with {contact}",
                "conversation_id": sms.get("address", ""),
            })
            sent_count += 1
        print(f"  Done: {sent_count} sent, {received_count} received (skipped)")
    except Exception as e:
        print(f"  [ERROR] SMS: {e}")
        stats["sms"]["errors"] += 1
        traceback.print_exc()

    # MMS entries (RCS/multimedia — where most of David's texts actually live)
    mms_sent = 0
    mms_received = 0
    try:
        for mms in root.findall("mms"):
            msg_box = mms.get("msg_box", "")
            if msg_box == "1":
                mms_received += 1
                continue  # received
            if msg_box != "2":
                continue  # not sent by David
            # Extract text from parts
            parts = mms.findall("parts/part")
            text_parts = []
            for part in parts:
                if part.get("ct") == "text/plain":
                    t = part.get("text", "").strip()
                    if t:
                        text_parts.append(t)
            body = "\n".join(text_parts).strip()
            if not body:
                continue
            contact = mms.get("contact_name", "Unknown")
            readable_date = mms.get("readable_date", "")
            date_ms = mms.get("date", "")
            ts = ""
            if date_ms:
                try:
                    ts = datetime.fromtimestamp(int(date_ms) / 1000, tz=timezone.utc).isoformat()
                except (ValueError, OSError):
                    ts = readable_date
            write_record(fh, {
                "source": "sms",
                "source_file": "mms_export",
                "text": body,
                "timestamp": ts,
                "conversation_title": f"Text with {contact}",
                "conversation_id": mms.get("address", ""),
            })
            mms_sent += 1
        print(f"  MMS: {mms_sent} sent, {mms_received} received (skipped)")
    except Exception as e:
        print(f"  [ERROR] MMS: {e}")
        stats["sms"]["errors"] += 1
        traceback.print_exc()


# ── DOCUMENT PARSER (AIS, Career, Throwbak) ─────────────────────────

def read_text_file(filepath):
    """Read a text-based file, return contents."""
    ext = filepath.suffix.lower()
    try:
        if ext in (".md", ".txt", ".yaml", ".yml"):
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        elif ext == ".docx":
            # Basic docx text extraction without python-docx dependency
            # Use zipfile to extract document.xml
            import zipfile
            import re
            with zipfile.ZipFile(str(filepath)) as z:
                with z.open("word/document.xml") as doc:
                    xml_content = doc.read().decode("utf-8")
                    # Strip XML tags to get plain text
                    text = re.sub(r"<[^>]+>", " ", xml_content)
                    text = re.sub(r"\s+", " ", text).strip()
                    return text
    except Exception as e:
        print(f"    [WARN] Could not read {filepath.name}: {e}")
    return ""


def extract_documents(fh, directory, source_name, weight=1.0):
    """Extract text from all documents in a directory tree."""
    if not directory.exists():
        print(f"  [SKIP] {directory} not found")
        return
    extensions = {".md", ".txt", ".yaml", ".yml", ".docx"}
    files = []
    for ext in extensions:
        files.extend(directory.rglob(f"*{ext}"))
    files = sorted(set(files))
    print(f"  Found {len(files)} files in {directory.name}")
    for filepath in files:
        text = read_text_file(filepath)
        if not text or len(text.strip()) < 20:
            continue
        # Use file modification time as timestamp
        try:
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime, tz=timezone.utc).isoformat()
        except Exception:
            mtime = ""
        write_record(fh, {
            "source": source_name,
            "source_file": str(filepath.relative_to(directory)),
            "text": text,
            "timestamp": mtime,
            "conversation_title": filepath.stem,
            "conversation_id": "",
            "weight": weight,
        })
    print(f"  Done: {source_name} — {stats[source_name]['messages']} documents")


# ── ESSAY PARSER (hybrid weight) ────────────────────────────────────

# Include: "Crazy In Tents", "What Lies Beneath", "Through the Overton Glass",
#          "By Any Means", "A Beautiful Mosaic"
# Exclude: "The Natural Order of Intelligence", "Shadows on the Wall"
EXCLUDED_ESSAYS = {"the natural order of intelligence", "shadows on the wall"}

def read_html_text(filepath):
    """Extract plain text from an HTML file, stripping tags."""
    import re
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
        # Remove script/style blocks
        html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        # Strip tags
        text = re.sub(r"<[^>]+>", " ", html)
        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text
    except Exception as e:
        print(f"    [WARN] Could not read HTML {filepath.name}: {e}")
        return ""


def extract_essays(fh):
    """Extract essays with hybrid weight (0.3 for prose, 1.0 for structural choices)."""
    if not ESSAY_DIR.exists():
        print(f"  [SKIP] Essay directory not found: {ESSAY_DIR}")
        return
    files = sorted(ESSAY_DIR.rglob("*.md")) + sorted(ESSAY_DIR.rglob("*.txt")) + sorted(ESSAY_DIR.rglob("*.html"))
    print(f"  Found {len(files)} essay files")
    for filepath in files:
        # Skip image files
        if filepath.stem.startswith("img-"):
            continue
        # Check exclusion list
        stem_lower = filepath.stem.lower().replace("-", " ").replace("_", " ")
        if any(exc in stem_lower for exc in EXCLUDED_ESSAYS):
            print(f"    [EXCLUDE] {filepath.name} (too heavily Claude-authored)")
            continue
        if filepath.suffix.lower() == ".html":
            text = read_html_text(filepath)
        else:
            text = read_text_file(filepath)
        if not text or len(text.strip()) < 50:
            continue
        try:
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime, tz=timezone.utc).isoformat()
        except Exception:
            mtime = ""
        write_record(fh, {
            "source": "essays",
            "source_file": filepath.name,
            "text": text,
            "timestamp": mtime,
            "conversation_title": filepath.stem,
            "conversation_id": "",
            "weight": 0.3,  # Hybrid: Claude prose + David architecture
        })
    print(f"  Done: essays — {stats['essays']['messages']} files")


# ── MAIN ────────────────────────────────────────────────────────────

def main():
    print("=" * 70)
    print("SCRVNR Voice Fingerprint — Phase 1: Corpus Assembly")
    print(f"Started: {datetime.now().isoformat()}")
    print("=" * 70)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with open(CORPUS_FILE, "w", encoding="utf-8") as fh:
        print("\n[1/6] Claude Chat Exports")
        extract_claude(fh)

        print("\n[2/6] GPT Chat Exports")
        extract_gpt(fh)

        print("\n[3/6] SMS Export")
        extract_sms(fh)

        print("\n[4/6] AIS + Career Documents")
        extract_documents(fh, AIS_PROFILE_DIR, "ais_profile_master")
        extract_documents(fh, AIS_MASTER_DIR, "ais_master_data")
        extract_documents(fh, CAREER_VOICE_DIR, "career_voice")

        print("\n[5/6] Throwbak Records")
        extract_documents(fh, THROWBAK_DIR, "throwbak")

        print("\n[6/6] Essays (hybrid weight)")
        extract_essays(fh)

    # Build manifest
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "total_messages": total_messages,
        "total_words": total_words,
        "corpus_file": str(CORPUS_FILE),
        "by_source": {},
    }
    for src, s in sorted(stats.items()):
        manifest["by_source"][src] = {
            "messages": s["messages"],
            "words": s["words"],
            "errors": s["errors"],
        }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("CORPUS ASSEMBLY COMPLETE")
    print(f"Total messages: {total_messages:,}")
    print(f"Total words:    {total_words:,}")
    print(f"Output:         {CORPUS_FILE}")
    print(f"Manifest:       {MANIFEST_FILE}")
    print("-" * 70)
    for src, s in sorted(stats.items()):
        print(f"  {src:25s}  {s['messages']:>8,} msgs  {s['words']:>10,} words  {s['errors']} errors")
    print("=" * 70)
    print(f"Finished: {datetime.now().isoformat()}")


if __name__ == "__main__":
    main()
