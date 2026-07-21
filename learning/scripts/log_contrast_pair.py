"""Log David's contrast correction pair. Crash-proof line logging."""
import sys, traceback
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\capture_log.txt"

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== start ===")
try:
    from core.correction_capture import CorrectionCapture
    log("import ok")
    cc = CorrectionCapture()
    log("init ok")
    pair = cc.capture(
        "This is not an exceptional case. It is the pattern.",
        "This isn't an exceptional case. It's the pattern.",
        register="ARGUMENTATIVE",
        source="session",
        score_both=True,
    )
    log("capture ok: " + repr(pair))
except Exception:
    log("EXCEPTION:\n" + traceback.format_exc())
log("=== end ===")
