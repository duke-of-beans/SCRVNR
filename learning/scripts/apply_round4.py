"""Apply salt + tangibility corrections: giant scissors, BORG jug. Capture pairs."""
import sys, traceback
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\round4_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== round4 start ===")
PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

edits = [
    # E1 tangibility: notarization (abstract) -> ribbon-cutting giant scissors (tangible, absurdist, credit-theft venom)
    ("The ballot formalized what bodies in the street had already forced. The movement created the conditions.\n\nThe vote was the notarization.",
     "The ballot formalized what bodies in the street had already forced. The movement built the bridge.\n\nThe vote showed up with the giant scissors."),
    # E2 the salt: dark-elite reference x lowbrow absurdist object
    ("Both parties drink from the same well.",
     "Both parties drink from the same BORG jug at Bohemian Grove."),
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
        "The ballot formalized what bodies in the street had already forced. The movement created the conditions. The vote was the notarization.",
        "The ballot formalized what bodies in the street had already forced. The movement built the bridge. The vote showed up with the giant scissors.",
        register="ARGUMENTATIVE", source="session", score_both=True)
    log("pair1 (tangibility/scissors): " + repr(p1))
    p2 = cc.capture(
        "Both parties drink from the same well.",
        "Both parties drink from the same BORG jug at Bohemian Grove.",
        register="ARGUMENTATIVE", source="session", score_both=True)
    log("pair2 (the salt/BORG): " + repr(p2))
except Exception:
    log("CAPTURE EXCEPTION:\n" + traceback.format_exc())

i = t.find("giant scissors")
log("\n--- scissors context ---\n" + t[i-300:i+200])
j = t.find("BORG jug")
log("\n--- BORG context ---\n" + t[j-120:j+250])
log("=== round4 end ===")
