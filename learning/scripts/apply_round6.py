"""Flip the final two beats: blade first, shrug last. Capture pair."""
import sys, traceback
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\round6_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== round6 start ===")
PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

old = "That's not a threat. It's the history section.\n\nThe guillotine wasn't the revolution. It was the receipt."
new = "The guillotine wasn't the revolution. It was the receipt.\n\nThat's not a threat. It's the history section."

n = t.count(old)
log(f"flip: {n} match(es)")
if n == 1:
    t = t.replace(old, new)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(t)
    log("file written.")
else:
    log("!! expected 1 match - NOT WRITTEN")

try:
    from core.correction_capture import CorrectionCapture
    cc = CorrectionCapture()
    p = cc.capture(
        "That's not a threat. It's the history section. The guillotine wasn't the revolution. It was the receipt.",
        "The guillotine wasn't the revolution. It was the receipt. That's not a threat. It's the history section.",
        register="ARGUMENTATIVE", source="session", score_both=True)
    log("pair (beat flip): " + repr(p))
except Exception:
    log("CAPTURE EXCEPTION:\n" + traceback.format_exc())

i = t.find("The guillotine wasn't")
log("\n--- final beats ---\n" + t[i-100:i+220])
log("=== round6 end ===")
