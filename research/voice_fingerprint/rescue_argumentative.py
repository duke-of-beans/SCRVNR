"""VFP-04 Task 3: ARGUMENTATIVE register rescue.

Phase 2 content-level detection was too strict (3+ hard signals, captured only
6 messages). This applies a WEIGHTED scoring pass over the decontaminated
corpus and reclassifies qualifying UNTAGGED/CASUAL/PROFESSIONAL messages
(plus LinkedIn-flavored CREATIVE_DIRECTION messages) as ARGUMENTATIVE.
"""
import json
import re
import time
from collections import Counter

INPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\decontaminated_corpus.jsonl"
OUTPUT = r"D:\Projects\SCRVNR\research\voice_fingerprint\final_corpus.jsonl"

THRESHOLD = 3.0
ELIGIBLE = {"UNTAGGED", "CASUAL", "PROFESSIONAL"}

COUNTERPOINT_PHRASES = [
    "that's not", "the problem with", "no — ", "no - ", "the distinction is",
    "the issue is", "the difference between", "actually", "not quite", "wrong",
]
DISAGREE_PHRASES = ["i disagree", "i'd push back", "i don't think", "counterpoint"]
LINKEDIN_KEYWORDS = ["post", "comment", "thread", "replied", "argument"]

# Same acronym exclusions as VFP-03 extract_features
ACRONYMS = {
    "I","API","URL","HTML","CSS","JSON","SQL","MCP","KERNL","SCRVNR","VIGIL",
    "TESSRYX","AEGIS","ASURIQ","COVOS","GPT","LLM","NER","FTS","RLS","RPC",
    "YAML","PDF","SMS","MMS","OK","ID","UI","UX","CLI","SDK","NPM","GIT",
    "SSH","TCP","HTTP","REST","CRUD","AWS","GCP","ETA","CEO","COO","LLC",
    "DBA","EIN","IRS","SEC","FEC","DOJ","FBI","CIA","NSA","FOIA","PAC",
    "AIPAC","NATO","IMF","UN","EU","USA","CA","BSOD","SSD","HDD","RAM",
    "CPU","GPU","USB","HDMI","OG","TDC","PCV","ATF","FWD",
}

RE_CAPS_WORD = re.compile(r"\b([A-Z]{2,})\b")
RE_NUMBER = re.compile(r"\b\d+(?:\.\d+)?%?\b")
RE_NAMED_REF = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b")
RE_RHETORICAL_Q = re.compile(r"\b(why|how|since when|if)\b[^?.!\n]*\?", re.IGNORECASE)


def score_message(text, register, word_count):
    """Weighted ARGUMENTATIVE score per VFP-04 spec. Each signal scores once."""
    lower = text.lower()
    score = 0.0
    signals = []

    if any(p in lower for p in COUNTERPOINT_PHRASES):
        score += 2.0
        signals.append("counterpoint")
    caps = [c for c in RE_CAPS_WORD.findall(text) if c not in ACRONYMS]
    if caps:
        score += 1.0
        signals.append("caps_emphasis")
    if RE_NUMBER.search(text) or RE_NAMED_REF.search(text):
        score += 1.0
        signals.append("evidence")
    if RE_RHETORICAL_Q.search(text):
        score += 1.0
        signals.append("rhetorical_q")
    if word_count > 100 and register != "TECH":
        score += 0.5
        signals.append("long_form")
    if any(p in lower for p in DISAGREE_PHRASES):
        score += 3.0
        signals.append("explicit_disagree")
    return score, signals


def main():
    start = time.time()
    total = 0
    rescued = 0
    rescued_from = Counter()
    register_totals = Counter()
    signal_counts = Counter()

    with open(INPUT, "r", encoding="utf-8") as fin, \
         open(OUTPUT, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            total += 1
            text = msg.get("text", "")
            register = msg.get("register", "UNTAGGED")
            word_count = msg.get("word_count") or len(text.split())

            eligible = register in ELIGIBLE
            if not eligible and register == "CREATIVE_DIRECTION":
                lower = text.lower()
                eligible = any(k in lower for k in LINKEDIN_KEYWORDS)

            if eligible:
                score, signals = score_message(text, register, word_count)
                if score >= THRESHOLD:
                    msg["register_original"] = register
                    msg["register"] = "ARGUMENTATIVE"
                    msg["argumentative_score"] = score
                    msg["argumentative_signals"] = signals
                    msg["rescued"] = True
                    rescued += 1
                    rescued_from[register] += 1
                    for s in signals:
                        signal_counts[s] += 1

            register_totals[msg["register"]] += 1
            fout.write(json.dumps(msg, ensure_ascii=False) + "\n")

    print(f"=== ARGUMENTATIVE Rescue Complete ({time.time() - start:.1f}s) ===")
    print(f"Total messages: {total:,}")
    print(f"New ARGUMENTATIVE captured: {rescued:,}")
    print(f"Rescued from: {dict(rescued_from)}")
    print(f"Signal frequency: {dict(signal_counts)}")
    print("\nRegister totals after rescue:")
    for reg, cnt in register_totals.most_common():
        print(f"  {reg}: {cnt:,}")


if __name__ == "__main__":
    main()
