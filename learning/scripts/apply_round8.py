"""Weaponize the ending: history section converts to promise. Capture pair."""
import sys, traceback
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\round8_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== round8 start ===")
PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

old = "The guillotine wasn't the revolution. It was the receipt.\n\nThat's not a threat. It's the history section."
new = "The guillotine wasn't the revolution. It was the receipt.\n\nAnd if things keep going the way they're going, the history section isn't a threat. It's a promise."

n = t.count(old)
log(f"ending: {n} match(es)")
if n == 1:
    t = t.replace(old, new)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(t)
    log("file written.")
else:
    log("!! expected 1 - NOT WRITTEN")

try:
    from core.correction_capture import CorrectionCapture
    cc = CorrectionCapture()
    p = cc.capture(
        "The guillotine wasn't the revolution. It was the receipt. That's not a threat. It's the history section.",
        "The guillotine wasn't the revolution. It was the receipt. And if things keep going the way they're going, the history section isn't a threat. It's a promise.",
        register="ARGUMENTATIVE", source="session", score_both=True)
    log("pair (weaponized ending): " + repr(p))
except Exception:
    log("CAPTURE EXCEPTION:\n" + traceback.format_exc())

i = t.find("The guillotine wasn't")
log("\n--- final ---\n" + t[i:i+260])
log("=== round8 end ===")
