"""Apply #32 inversion sweep results to v5: open restructure + Declaration inversion."""
import sys, traceback
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\sweep_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== sweep start ===")
PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

edits = [
    # E1: strip crime/anaphora from the open's first paragraph - guards descend, no reason given
    ("at the Occoquan Workhouse in Virginia. Their crime was picketing. They had stood at the White House gates holding signs that asked why a president waging a war to make the world safe for democracy would not extend democracy to half his own citizens. For that, they were arrested. For that, they were imprisoned. And on that night, on the superintendent's order, they were beaten.\n\nLucy Burns",
     "at the Occoquan Workhouse in Virginia.\n\nLucy Burns"),
    # E2: detonation - crime revealed AFTER the brutality; anaphora becomes a triplet; amendment isolated
    ("was slammed twice over the back of an iron bench. [1]\n\nThe superintendent was never prosecuted. The women went on hunger strikes. The state held them down and forced tubes into their throats. And within three years, the Nineteenth Amendment was ratified.",
     "was slammed twice over the back of an iron bench. [1] The superintendent was never prosecuted.\n\nTheir crime was picketing. They had stood at the White House gates holding signs that asked why a president waging a war to make the world safe for democracy would not extend democracy to half his own citizens. For that, they were arrested. For that, they were imprisoned. For that, they were beaten. And when they went on hunger strikes, the state held them down and forced tubes into their throats.\n\nWithin three years, the Nineteenth Amendment was ratified."),
    # E3: Declaration quote before its source - the instruction reads seditious until the classroom lands
    ('And beneath all of them, the founding document itself - the one framed in every classroom in the country - declaring that when a government becomes destructive of its ends, "it is their right, it is their duty, to throw off such Government." [28]',
     'And beneath all of them, an older instruction: when any government becomes destructive of its ends, "it is their right, it is their duty, to throw off such Government." [28] That one hangs framed in every classroom in the country.'),
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

if ok:
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(t)
    log("file written.")
else:
    with open(PATH, "w", encoding="utf-8") as f:
        f.write(t)
    log("file written with skips - CHECK.")

i = t.find("Occoquan Workhouse")
log("\n--- new open ---\n" + t[i-60:i+1200])
log("=== sweep end ===")
