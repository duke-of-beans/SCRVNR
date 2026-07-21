"""Apply David's contrast correction to v5, log the correction pair, verify."""
import sys, io, atexit
sys.path.insert(0, r"D:\Projects\SCRVNR")

_buf = io.StringIO()
class _Tee:
    def write(self, s):
        _buf.write(s)
        try:
            sys.__stdout__.write(s)
        except Exception:
            pass
    def flush(self):
        pass
sys.stdout = _Tee()

def _dump():
    with open(r"D:\Projects\SCRVNR\learning\scripts\contrast_fix_out.txt", "w", encoding="utf-8") as f:
        f.write(_buf.getvalue())
atexit.register(_dump)

PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

edits = [
    # David's explicit correction: casual beat after the hard thesis line
    ("This is not an exceptional case. It is the pattern.",
     "This isn't an exceptional case. It's the pattern."),
    # Parallel application of the principle: hard parts (MLK letter) hit before; close drops casual
    ("So take the counterargument at full strength. The question is not whether the system can produce a New Deal.",
     "So take the counterargument at full strength. The question isn't whether the system can produce a New Deal."),
]

for old, new in edits:
    n = t.count(old)
    print(f"replace ({n} match): {old[:60]}...")
    if n != 1:
        print("  !! expected exactly 1 match - ABORTING this edit")
        continue
    t = t.replace(old, new)

with open(PATH, "w", encoding="utf-8") as f:
    f.write(t)
print("file patched.")

# Log the David correction pair (his explicit correction only, not my parallel application)
from core.correction_capture import CorrectionCapture
cc = CorrectionCapture()
pair = cc.capture(
    "This is not an exceptional case. It is the pattern.",
    "This isn't an exceptional case. It's the pattern.",
    register="ARGUMENTATIVE",
    source="session",
    score_both=True,
)
print("correction pair logged:", pair.get("id") if isinstance(pair, dict) else pair)

# Verify the patched open reads correctly
i = t.find("methods that were not voting")
print("\n--- patched open close ---")
print(t[i:i+140])
