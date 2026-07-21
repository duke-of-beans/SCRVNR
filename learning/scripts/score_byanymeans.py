"""By Any Means: score original (June 13) vs v4 (phased workflow). Mechanical check on v4."""
import sys, re
sys.path.insert(0, r"D:\Projects\SCRVNR")
from core.pipeline import VoicePipeline

pipe = VoicePipeline()

def clean_md(path, drop_recon_notes=False):
    with open(path, "r", encoding="utf-8") as f:
        t = f.read()
    if drop_recon_notes:
        t = re.sub(r'\*?\[(ORIGINAL DRAFT|Remainder of|Reconstructed)[^\]]*\]\*?', '', t)
        t = re.sub(r'### V?I{0,3}\. \*?\[Reconstructed[^\]]*\]\*?', '', t)
    # drop sources section
    idx = t.find('### Sources')
    if idx > 0:
        t = t[:idx]
    t = re.sub(r'^#.*$', '', t, flags=re.MULTILINE)
    t = re.sub(r'\[(\d+)\]', '', t)
    t = re.sub(r'\*\*?', '', t)
    t = re.sub(r'^---$', '', t, flags=re.MULTILINE)
    return t.strip()

v4_path = r"D:\Projects\SCRVNR\by-any-means-v4.md"
orig_path = r"D:\Projects\SCRVNR\by-any-means-original-june13.md"

# ---- Phase 6: mechanical check on v4 ----
with open(v4_path, "r", encoding="utf-8") as f:
    raw = f.read()
em = raw.count('\u2014')
en = raw.count('\u2013')
sq = raw.count('\u2018') + raw.count('\u2019') + raw.count('\u201c') + raw.count('\u201d')
print("=" * 60)
print("PHASE 6 MECHANICAL CHECK - v4")
print("=" * 60)
print(f"em-dashes: {em}  en-dashes: {en}  smart-quotes: {sq}")
print("PASS" if (em == 0 and sq == 0) else "FAIL - needs cleanup")

# ---- Phase 7: centrifuge ----
original = clean_md(orig_path, drop_recon_notes=True)
v4 = clean_md(v4_path)

print()
print("=" * 60)
print("CENTRIFUGE: Original (June 13) vs V4 (phased workflow)")
print("=" * 60)

for label, text in [("ORIGINAL v3 (June 13, recovered)", original), ("V4 (phased workflow)", v4)]:
    r = pipe.process(text, register='ARGUMENTATIVE')
    s = r['score']
    print(f"\n--- {label} ---")
    print(f"Words: {len(text.split())}")
    print(f"Score: {r['overall_score']:.3f} ({r['band']})")
    print(f"  rarity={s.get('rarity_score',0):.3f} rhythm={s.get('rhythm_score',0):.3f} style={s.get('style_score',0):.3f}")
    print(f"Fixes: {r['fix_count']}")
    for fx in r['fixes'][:3]:
        print(f"  [{fx['category']}] {fx['type']}: {fx.get('count','')}")
    if r['suggestions']:
        for sug in r['suggestions'][:3]:
            print(f"  suggest: {sug['type']}: {sug.get('words', sug.get('suggestion',''))}")
