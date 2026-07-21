"""Apply David's two corrections to disk copy + log correction pairs."""
import io, sys
sys.path.insert(0, r"D:\Projects\SCRVNR")
from core.correction_capture import CorrectionCapture

p = r"D:\Projects\SCRVNR\such-a-thing-v3.md"
t = io.open(p, encoding="utf-8").read()

# Correction 1: flourish -> David's construction
old1 = "That word - *product*. Not a flourish."
new1 = "And that word; *product*. Not decoration."
assert old1 in t, "flourish line not found"
t = t.replace(old1, new1)

# Correction 2: GDP line insertion
old2 = "and measures the bailing in gallons per hour while the hole does what holes do."
new2 = "and measures the bailing in gallons per hour while the hole does what holes do. At national scale, gallons per hour is called GDP."
assert old2 in t, "bucket line not found"
t = t.replace(old2, new2)

io.open(p, "w", encoding="utf-8").write(t)
print("Disk copy updated.")

cc = CorrectionCapture()

r1 = cc.capture(
    original="That word - product. Not a flourish. Multiplication: factors, each one load-bearing, where a single zero bankrupts everything it touches.",
    corrected="And that word; product. Not decoration. Multiplication: factors, each one load-bearing, where a single zero bankrupts everything it touches.",
    register="ARGUMENTATIVE",
    source="session",
)
print(f"Pair 1 (flourish vocabulary): {r1}")

r2 = cc.capture(
    original="The conventional model hands out better buckets - job training here, a clinic visit there, a food bank on Thursdays - and measures the bailing in gallons per hour while the hole does what holes do.",
    corrected="The conventional model hands out better buckets - job training here, a clinic visit there, a food bank on Thursdays - and measures the bailing in gallons per hour while the hole does what holes do. At national scale, gallons per hour is called GDP.",
    register="ARGUMENTATIVE",
    source="session",
)
print(f"Pair 2 (GDP insertion): {r2}")
