"""Score v3 against original and v2 through the full pipeline."""
import sys, re
sys.path.insert(0, r"D:\Projects\SCRVNR")
from core.pipeline import VoicePipeline

pipe = VoicePipeline()

def extract_body(html):
    text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    start = text.find('Photo:')
    if start > 0:
        text = text[start + 20:]
    end = text.find('Sources')
    if end > 0:
        text = text[:end]
    return text.strip()

def clean_md(path):
    with open(path, "r", encoding="utf-8") as f:
        t = f.read()
    t = re.sub(r'^#.*$', '', t, flags=re.MULTILINE)
    t = re.sub(r'\[(\d+)\]', '', t)
    t = re.sub(r'\*\*?', '', t)
    return t.strip()

with open(r"D:\Projects\davidkirsch-me\writing\such-a-thing-as-society.html", "r", encoding="utf-8") as f:
    original = extract_body(f.read())

v3 = clean_md(r"D:\Projects\SCRVNR\such-a-thing-v3.md")

print("=" * 60)
print("CENTRIFUGE: Original vs V3 (phased workflow)")
print("=" * 60)

for label, text in [("ORIGINAL (published)", original), ("V3 (phased workflow)", v3)]:
    r = pipe.process(text, register='ARGUMENTATIVE')
    s = r['score']
    print(f"\n--- {label} ---")
    print(f"Words: {len(text.split())}")
    print(f"Score: {r['overall_score']:.3f} ({r['band']})")
    print(f"  rarity={s.get('rarity_score',0):.3f} rhythm={s.get('rhythm_score',0):.3f} style={s.get('style_score',0):.3f}")
    print(f"Fixes: {r['fix_count']}")
    for f in r['fixes'][:3]:
        print(f"  [{f['category']}] {f['type']}: {f.get('count','')}")
    if r['suggestions']:
        for sug in r['suggestions']:
            print(f"  suggest: {sug['type']}: {sug.get('words', sug.get('suggestion',''))}")
