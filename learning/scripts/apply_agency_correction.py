"""Apply David's agency correction (we -> the dry end / handed) to disk + log pairs."""
import io, sys
sys.path.insert(0, r"D:\Projects\SCRVNR")
from core.correction_capture import CorrectionCapture

p = r"D:\Projects\SCRVNR\such-a-thing-v3.md"
t = io.open(p, encoding="utf-8").read()

old1 = "We spent fifty years filing them under *compassion* so we'd never have to collect them."
new1 = "The dry end spent fifty years filing them under *compassion* - and teaching everyone else the word meant weakness - so no one would ever come to collect them."
assert old1 in t, "closer line not found"
t = t.replace(old1, new1)

old2 = "They were never in tension. We just had the wrong model."
new2 = "They were never in tension. We were handed the wrong model."
assert old2 in t, "model line not found"
t = t.replace(old2, new2)

io.open(p, "w", encoding="utf-8").write(t)
print("Disk copy updated.")

cc = CorrectionCapture()

r1 = cc.capture(
    original="The returns are at the bottom. They always were. We spent fifty years filing them under compassion so we'd never have to collect them.",
    corrected="The returns are at the bottom. They always were. The dry end spent fifty years filing them under compassion - and teaching everyone else the word meant weakness - so no one would ever come to collect them.",
    register="ARGUMENTATIVE",
    source="session",
)
print(f"Pair 1 (agency: we -> the dry end): {r1}")

r2 = cc.capture(
    original="They were never in tension. We just had the wrong model.",
    corrected="They were never in tension. We were handed the wrong model.",
    register="ARGUMENTATIVE",
    source="session",
)
print(f"Pair 2 (had -> handed): {r2}")
