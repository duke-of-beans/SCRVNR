"""Apply David's three corrections: referent precision, opener contrast, isolation scarcity. Capture pairs."""
import sys, traceback
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\round3_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== round3 start ===")
PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

edits = [
    # E1 referent precision: name over ambiguous pronoun in multi-actor scene
    ("The guards refused her a doctor until dawn.",
     "The guards refused Cosu a doctor until dawn."),
    # E2 opener contrast (David's flag): casual opener before hard dense paragraph
    ("Here is what the show cuts.",
     "Here's what the show cuts."),
    # E3 opener contrast (same construction, section IV): proactive application
    ("That's the history. Here is why the pattern holds now.",
     "That's the history. Here's why the pattern holds now."),
    # E4 isolation scarcity: fold workday punch into the Haymarket paragraph
    ("The eight-hour workday took 105 years.\n\nHaymarket, where",
     "The eight-hour workday took 105 years. Haymarket, where"),
    # E5 isolation scarcity: fold "It always does." back inline
    ("locked to prevent theft. [8] The legislation followed the bodies.\n\nIt always does.",
     "locked to prevent theft. [8] The legislation followed the bodies. It always does."),
]

ok = True
for i, (old, new) in enumerate(edits, 1):
    n = t.count(old)
    log(f"E{i}: {n} match(es)")
    if n != 1:
        log(f"E{i}: !! expected 1 - SKIPPED")
        ok = False
        continue
    t = t.replace(old, new)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(t)
log("file written." if ok else "file written WITH SKIPS - CHECK.")

# Capture the two direct David corrections as pairs
try:
    from core.correction_capture import CorrectionCapture
    cc = CorrectionCapture()
    p1 = cc.capture(
        "Alice Cosu watched Lewis crumple, believed she was watching a woman die, and suffered a heart attack. The guards refused her a doctor until dawn.",
        "Alice Cosu watched Lewis crumple, believed she was watching a woman die, and suffered a heart attack. The guards refused Cosu a doctor until dawn.",
        register="ARGUMENTATIVE", source="session", score_both=True)
    log("pair1 (referent precision): " + repr(p1))
    p2 = cc.capture(
        "Here is what the show cuts.",
        "Here's what the show cuts.",
        register="ARGUMENTATIVE", source="session", score_both=True)
    log("pair2 (opener contrast): " + repr(p2))
except Exception:
    log("CAPTURE EXCEPTION:\n" + traceback.format_exc())

# verify section II shape
i = t.find("A confession.")
log("\n--- section II around confession ---\n" + t[i-200:i+900])
log("=== round3 end ===")
