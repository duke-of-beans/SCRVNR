"""Standalone capture: weaponized ending pair."""
import sys, traceback
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\r8_capture_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== start ===")
try:
    from core.correction_capture import CorrectionCapture
    log("import ok")
    cc = CorrectionCapture()
    log("init ok")
    p = cc.capture(
        "The guillotine wasn't the revolution. It was the receipt. That's not a threat. It's the history section.",
        "The guillotine wasn't the revolution. It was the receipt. And if things keep going the way they're going, the history section isn't a threat. It's a promise.",
        register="ARGUMENTATIVE", source="session", score_both=True)
    log("capture ok: " + repr(p))
except Exception:
    log("EXCEPTION:\n" + traceback.format_exc())
log("=== end ===")
