"""Add subheading to section VIII in both copies."""
import sys
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\round9_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== round9 start ===")
PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

old = "### VIII.\n\nThe New Deal was a system buying survival."
new = "### VIII.\n#### On hollow wills and sharp receipts\n\nThe New Deal was a system buying survival."

n = t.count(old)
log(f"subheading: {n} match(es)")
if n == 1:
    t = t.replace(old, new)
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(t)
    log("file written.")
else:
    log("!! expected 1 - NOT WRITTEN")

# verify
i = t.find("### VIII.")
log("\n--- section VIII head ---\n" + t[i:i+200])
log("=== round9 end ===")
