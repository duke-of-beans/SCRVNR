"""Fix subtitle: replace essay subtitle, remove misplaced section subheading."""
import sys

LOG = r"D:\Projects\SCRVNR\learning\scripts\round10_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== round10 start ===")
PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

edits = [
    # E1: replace essay subtitle
    ("## On subjective opportunity and objective cost",
     "## On hollow wills and sharp receipts"),
    # E2: remove misplaced section subheading from VIII
    ("### VIII.\n#### On hollow wills and sharp receipts\n\nThe New Deal",
     "### VIII.\n\nThe New Deal"),
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
log("file written." if ok else "file written WITH SKIPS")

# verify
i = t.find("# By Any Means")
log("\n--- header ---\n" + t[i:i+120])
j = t.find("### VIII.")
log("\n--- VIII ---\n" + t[j:j+120])
log("=== round10 end ===")
