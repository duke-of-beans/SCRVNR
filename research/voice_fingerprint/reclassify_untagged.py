"""VFP-03 Task 0: Reclassify UNTAGGED messages using Phase 2 findings."""
import json
import re
import sys
import time

INPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\tagged_corpus.jsonl"
OUTPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\tagged_corpus_v2.jsonl"

# Title-based reclassification rules (case-insensitive substring match)
# Order matters — first match wins
TITLE_RULES = [
    # TECH — broadest, goes first for tech-specific patterns
    (["handoff", "execute", "file execution", "mission control", "dashboard",
      "mission", "forum", "blueprint", "node", "memory resource",
      "model switching", "processing", "pipeline", "debug", "deployment",
      "cors", "config", "validation", "ui ", "security", "injection",
      "aegis", "tessryx", "gad", "satellite", "cluster", "contentstudio",
      "evomap", "sprint", "sluice", "loading", "environment",
      "thalamic", "pdf generation", "visual bug", "fixing", "map pin",
      "bonus model", "task visibility", "process manager", "project environment",
      "next task", "ready for next", "document review"], "TECH"),
    # ACADEMIC
    (["syntheon", "medical device", "innovation", "consciousness", "bridge",
      "cognitive", "persona", "orgone", "accumulator", "fda regulation"], "ACADEMIC"),
    # PROFESSIONAL
    (["tea role", "candidate", "sales", "fiverr", "seller", "domain",
      "affiliate", "monetiz", "email template", "profile with qr",
      "justin", "repositioning", "business session", "company ownership",
      "licensing", "ein", "fbn", "e-commerce", "website for",
      "cleaning", "hustle", "onboarding", "consultant", "addendum",
      "contract", "restructuring", "hemp product", "thca",
      "aztek waste", "side hustle"], "PROFESSIONAL"),
    # MECHANICAL
    (["cap rotor", "installation", "rotor", "wheel styl", "dakota",
      "audio-only", "receiver", "sony"], "MECHANICAL"),
    # INVESTIGATE
    (["research brief", "research kickoff", "cannabis", "legalization",
      "crime stoppers", "decentralized crime"], "INVESTIGATE"),
    # PERSONAL
    (["limen", "jenna", "companionship", "creative workflow"], "PERSONAL"),
    # CREATIVE_DIRECTION
    (["homepage", "japan page", "design audit", "page design",
      "meme", "subtitle", "design sprint"], "CREATIVE_DIRECTION"),
]

# Argumentative detection signals
COUNTERPOINT_RE = re.compile(
    r"that'?s not|the problem with|no\s*[—\-]\s|incorrect|wrong because|"
    r"the distinction is|the issue is", re.IGNORECASE
)
EVIDENCE_RE = re.compile(
    r"according to|the data shows?|the documentation|\d+%|\$\d+", re.IGNORECASE
)
CAPS_EMPHASIS_RE = re.compile(r"(?<!\b[A-Z])\b[A-Z]{2,}\b(?!\s[A-Z])")
RHETORICAL_Q_RE = re.compile(
    r"(why would|how is that|since when|if that'?s true)[^?]*\?", re.IGNORECASE
)
REFUTATION_RE = re.compile(
    r"your point about|the claim that", re.IGNORECASE
)

# Common acronyms to exclude from caps emphasis detection
COMMON_ACRONYMS = {"API","URL","HTML","CSS","JSON","SQL","MCP","OK","ID","UI","UX"}

def match_title(title):
    """Return register if title matches any rule, else None."""
    if not title:
        return None
    t = title.lower()
    for substrings, register in TITLE_RULES:
        for s in substrings:
            if s in t:
                return register
    return None

def is_argumentative(text):
    """Return True if text has 3+ argumentative signals."""
    if not text:
        return False
    signals = 0
    if COUNTERPOINT_RE.search(text):
        signals += 1
    if EVIDENCE_RE.search(text):
        signals += 1
    caps_words = CAPS_EMPHASIS_RE.findall(text)
    real_caps = [w for w in caps_words if w not in COMMON_ACRONYMS and len(w) >= 2]
    if real_caps:
        signals += 1
    if RHETORICAL_Q_RE.search(text):
        signals += 1
    if REFUTATION_RE.search(text):
        signals += 1
    return signals >= 3

def main():
    start = time.time()
    total = 0
    reclassified = 0
    reclass_map = {}  # target_register -> count
    still_untagged = 0

    with open(INPUT, "r", encoding="utf-8") as fin, \
         open(OUTPUT, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            total += 1

            if msg.get("register") == "UNTAGGED":
                new_reg = match_title(msg.get("conversation_title", ""))
                if new_reg:
                    msg["register"] = new_reg
                    reclassified += 1
                    reclass_map[new_reg] = reclass_map.get(new_reg, 0) + 1
                elif is_argumentative(msg.get("text", "")):
                    msg["register"] = "ARGUMENTATIVE"
                    reclassified += 1
                    reclass_map["ARGUMENTATIVE"] = reclass_map.get("ARGUMENTATIVE", 0) + 1
                else:
                    still_untagged += 1

            fout.write(json.dumps(msg, ensure_ascii=False) + "\n")

    elapsed = time.time() - start
    untagged_pct = (still_untagged / total) * 100 if total else 0

    print(f"\n=== UNTAGGED Reclassification Results ===")
    print(f"Total messages: {total:,}")
    print(f"Reclassified: {reclassified:,}")
    print(f"Still UNTAGGED: {still_untagged:,} ({untagged_pct:.1f}%)")
    print(f"\nReclassified to:")
    for reg, count in sorted(reclass_map.items(), key=lambda x: -x[1]):
        print(f"  {reg}: {count:,}")
    print(f"\nProcessing time: {elapsed:.1f}s")

if __name__ == "__main__":
    main()
