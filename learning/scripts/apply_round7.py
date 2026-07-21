"""Insert the Resets section as new VIII, renumber VIII->IX, IX->X, add sources [30]-[33]."""
import sys, traceback
sys.path.insert(0, r"D:\Projects\SCRVNR")

LOG = r"D:\Projects\SCRVNR\learning\scripts\round7_log.txt"
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

log("=== round7 start ===")
PATH = r"D:\Projects\SCRVNR\by-any-means-v5.md"
with open(PATH, "r", encoding="utf-8") as f:
    t = f.read()

NEW_SECTION = """### VIII.

The New Deal was a system buying survival. Not every system pays.

France set the founding price. A monarchy that priced out every petition, every parlement, every bread riot, until 1789 arrived all at once - and four years later the king who could not be corrected was corrected. In public. Permanently. [29] That's the archetype, and it has never stopped running.

Romania, 1989. Nicolae Ceausescu ruled for twenty-four years, shot into a crowd in Timisoara, and gave one last speech from a balcony to a square that started booing. Three days later he was lifting off the roof of the Central Committee building in a helicopter as the crowd came through the doors. He was caught within hours, tried by a military tribunal in about an hour, and executed by firing squad against a wall with his wife - on Christmas Day, on television. [30] Twenty-four years, then an hour.

Now the modern run. Sri Lanka, July 2022: an economy looted into fuel lines and blackouts, months of protest, and then a crowd simply walked into the presidential palace - and swam in the pool. Cooked in the kitchen. Used the gym. Gotabaya Rajapaksa fled on a military jet and resigned by email, from Singapore. [31] Bangladesh, August 2024: students protesting job quotas were met with a crackdown that killed some 1,400 people, and weeks later Sheikh Hasina - fifteen years in power - had forty-five minutes to reach a helicopter before the crowd reached her residence. They lounged on her bed for the cameras. Fifteen months on, a tribunal convicted her of crimes against humanity and sentenced her to death anyway. In absentia. The trial did not require her attendance. [32] Nepal, September 2025: a government banned twenty-six social media platforms while its ministers' children posted designer luggage, and Gen Z came into the streets. Security forces killed nineteen protesters on day one. On day two the parliament was burning, the Supreme Court was burning, ministers' houses were burning, and the prime minister was gone - forty-eight hours, start to finish. Seventy-two dead. The protesters picked the interim replacement in a poll on Discord. [33]

Three governments. Three summers.

None of this is ancient and none of it is foreign in kind. The mechanism is the one this essay has been describing the whole time, run at full amplitude: consent withdrawn all at once instead of on schedule, cost imposed beyond any concession's reach, terms reset. The people in those palaces all had elections, courts, petitions - the whole permitted apparatus - and they priced every channel out until the only channel left was the door.

The reset isn't a theory. It has reruns."""

edits = [
    # E1: insert new VIII before tradition section, renaming tradition to IX
    ("---\n\n### VIII.\n\nThis is just America. A betrayal of the curriculum, but tradition.",
     "---\n\n" + NEW_SECTION + "\n\n---\n\n### IX.\n\nThis is just America. A betrayal of the curriculum, but tradition."),
    # E2: rename ticket/guillotine section IX -> X
    ("---\n\n### IX.\n\nThe ballot box exists.",
     "---\n\n### X.\n\nThe ballot box exists."),
    # E3: sources 30-33
    ("[29] Trial and execution of Louis XVI (January 1793), National Convention records; Revolutionary Tribunal proceedings, 1793-1794.",
     "[29] Trial and execution of Louis XVI (January 1793), National Convention records; Revolutionary Tribunal proceedings, 1793-1794.\n[30] Trial and execution of Nicolae and Elena Ceausescu (December 25, 1989); Romanian military tribunal record; broadcast footage.\n[31] Resignation of Gotabaya Rajapaksa (July 2022), Parliament of Sri Lanka; contemporaneous Reuters/AP reporting on the July 9 occupation of the presidential palace.\n[32] UN OHCHR findings on the July-August 2024 killings in Bangladesh (~1,400 dead); International Crimes Tribunal-1, Chief Prosecutor v. Sheikh Hasina & Others, verdict of November 17, 2025.\n[33] Nepal Ministry of Health casualty figures (September 2025); contemporaneous Reuters/AFP/Al Jazeera reporting on the September 8-9 protests and the resignation of K.P. Sharma Oli."),
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
log("file written." if ok else "file written WITH SKIPS - CHECK.")

# mechanical check on the whole patched essay
em = t.count("\u2014") + t.count("\u2013")
sq = sum(t.count(c) for c in "\u2018\u2019\u201c\u201d")
log(f"mechanical: em/en={em} curly={sq}")
log(f"words: {len(t.split())}")
log("=== round7 end ===")
