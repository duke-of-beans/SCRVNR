"""Round 5: duress cui bono, betrayal inversion, the guillotine ending. Capture pairs."""
import sys, traceback
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\round5_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== round5 start ===")
PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

E3_OLD = "The question is not whether you should vote. The question is whether you believe the ticket is the whole building - and what three hundred years of evidence say about that belief."
E3_NEW = E3_OLD + "\n\nBecause here's what the evidence says, plainly, one last time. These stories don't end with laws getting passed. Every case in this essay is filed under reform, and every one of them was a revolution - not the powdered-wig kind, smaller, domestic, but mechanically identical: consent withdrawn, cost imposed, terms reset. Nothing the same before versus after.\n\nAnd the record keeps one more line item about how the biggest resets concluded. The architects of the old arrangement were tried in public, and more than a few met a blade there. [29] In public. On purpose. Not as spectacle - as notice, so that everyone watching, on every side of it, understood: the public would not stand for this again.\n\nThat's not a threat. It's the history section.\n\nThe guillotine wasn't the revolution. It was the receipt."

edits = [
    # E1 section V: the duress has authors and beneficiaries
    ("The question is what it builds alongside one, and which of the two lasts longer.",
     "The question is what it builds alongside one, and which of the two lasts longer. And ask who caused the duress - and who collected on it. One side, the other, or both."),
    # E2 section VIII opener: betrayal reassigned to the curriculum
    ("Here's the part they really don't want in the curriculum: none of this is a betrayal of the American tradition. It *is* the American tradition.",
     "This is just America. A betrayal of the curriculum, but tradition."),
    # E3 section IX: the guillotine ending
    (E3_OLD, E3_NEW),
    # E4 sources: add [29]
    ("[28] Declaration of Independence (1776).",
     "[28] Declaration of Independence (1776).\n[29] Trial and execution of Louis XVI (January 1793), National Convention records; Revolutionary Tribunal proceedings, 1793-1794."),
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

try:
    from core.correction_capture import CorrectionCapture
    cc = CorrectionCapture()
    p1 = cc.capture(
        "The question is what it builds alongside one, and which of the two lasts longer.",
        "The question is what it builds alongside one, and which of the two lasts longer. And ask who caused the duress - and who collected on it. One side, the other, or both.",
        register="ARGUMENTATIVE", source="session", score_both=True)
    log("pair1 (duress cui bono): " + repr(p1))
    p2 = cc.capture(
        "Here's the part they really don't want in the curriculum: none of this is a betrayal of the American tradition. It is the American tradition.",
        "This is just America. A betrayal of the curriculum, but tradition.",
        register="ARGUMENTATIVE", source="session", score_both=True)
    log("pair2 (betrayal inversion): " + repr(p2))
except Exception:
    log("CAPTURE EXCEPTION:\n" + traceback.format_exc())

i = t.find("The guillotine wasn't")
log("\n--- ending ---\n" + t[i-800:i+120])
log("=== round5 end ===")
