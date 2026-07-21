"""Fair comparison: verbatim-matched sections only (open through V + closer IX)."""
import sys, re
sys.path.insert(0, r"D:\Projects\SCRVNR")
from core.pipeline import VoicePipeline

pipe = VoicePipeline()

def load(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def strip_md(t):
    idx = t.find('### Sources')
    if idx > 0:
        t = t[:idx]
    t = re.sub(r'^#.*$', '', t, flags=re.MULTILINE)
    t = re.sub(r'\[(\d+)\]', '', t)
    t = re.sub(r'\*\*?', '', t)
    t = re.sub(r'^---$', '', t, flags=re.MULTILINE)
    return t.strip()

def matched_span(t):
    """Keep opening through end of section V, plus section IX closer. Drop VI-VIII."""
    # cut at section VI
    m = re.search(r'^### VI\.', t, flags=re.MULTILINE)
    head = t[:m.start()] if m else t
    # grab IX
    m9 = re.search(r'^### IX\.', t, flags=re.MULTILINE)
    tail = t[m9.start():] if m9 else ''
    return head + "\n" + tail

orig = matched_span(load(r"D:\Projects\SCRVNR\by-any-means-original-june13.md"))
v4 = matched_span(load(r"D:\Projects\SCRVNR\by-any-means-v4.md"))

# drop the recon-note paragraph from original section V
orig = re.sub(r'\*\[Remainder of Section V[^\]]*\]\*', '', orig)
orig = re.sub(r'\*\[ORIGINAL DRAFT[^\]]*\]\*', '', orig)

print("=" * 60)
print("FAIR COMPARISON: matched sections (open-V + IX), ARGUMENTATIVE")
print("=" * 60)
for label, text in [("ORIGINAL v3 (verbatim only)", strip_md(orig)), ("V4 (same span)", strip_md(v4))]:
    r = pipe.process(text, register='ARGUMENTATIVE')
    s = r['score']
    print(f"\n--- {label} ---")
    print(f"Words: {len(text.split())}")
    print(f"Score: {r['overall_score']:.3f} ({r['band']})")
    print(f"  rarity={s.get('rarity_score',0):.3f} rhythm={s.get('rhythm_score',0):.3f} style={s.get('style_score',0):.3f}")
