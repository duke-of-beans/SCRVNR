"""Score comparison: original vs v2 rewrite through centrifuge."""
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

with open(r"D:\Projects\davidkirsch-me\writing\such-a-thing-as-society.html", "r", encoding="utf-8") as f:
    original_html = f.read()
original_text = extract_body(original_html)

# Read v2 from the outputs folder
import glob, os
v2_paths = [
    os.path.expanduser(r"~\Downloads\such-a-thing-as-society-v2.md"),
    r"D:\Projects\SCRVNR\such-a-thing-v2-test.md",
]
v2_text = None
for p in v2_paths:
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            v2_text = f.read()
        print(f"V2 source: {p}")
        break

if v2_text is None:
    print("ERROR: V2 file not found. Scoring original only.")
    v2_text = original_text  # fallback

v2_text = re.sub(r'^#.*$', '', v2_text, flags=re.MULTILINE)
v2_text = re.sub(r'\[(\d+)\]', '', v2_text)
v2_text = re.sub(r'\*\*', '', v2_text).strip()

print("=" * 60)
print("SCRVNR v2.0 Centrifuge Comparison")
print("=" * 60)

print(f"\nOriginal word count: {len(original_text.split())}")
print(f"V2 word count: {len(v2_text.split())}")

print("\n--- ORIGINAL ---")
orig_result = pipe.process(original_text, register='ARGUMENTATIVE')
print(f"Score: {orig_result['overall_score']:.3f} ({orig_result['band']})")
print(f"Fixes available: {orig_result['fix_count']}")
for f in orig_result['fixes'][:5]:
    print(f"  [{f['category']}] {f['type']}: {f.get('count', '')}")
print(f"Suggestions: {len(orig_result['suggestions'])}")
for s in orig_result['suggestions']:
    print(f"  {s['type']}: {s.get('words', s.get('suggestion', ''))}")

print("\n--- V2 REWRITE ---")
v2_result = pipe.process(v2_text, register='ARGUMENTATIVE')
print(f"Score: {v2_result['overall_score']:.3f} ({v2_result['band']})")
print(f"Fixes available: {v2_result['fix_count']}")
for f in v2_result['fixes'][:5]:
    print(f"  [{f['category']}] {f['type']}: {f.get('count', '')}")
print(f"Suggestions: {len(v2_result['suggestions'])}")
for s in v2_result['suggestions']:
    print(f"  {s['type']}: {s.get('words', s.get('suggestion', ''))}")

delta = v2_result['overall_score'] - orig_result['overall_score']
print(f"\n--- DELTA ---")
print(f"Score: {delta:+.3f}")
print(f"Band: {orig_result['band']} -> {v2_result['band']}")

r1 = orig_result['score']
r2 = v2_result['score']
print(f"\nOriginal: rarity={r1.get('rarity_score',0):.3f} rhythm={r1.get('rhythm_score',0):.3f} style={r1.get('style_score',0):.3f}")
print(f"V2:       rarity={r2.get('rarity_score',0):.3f} rhythm={r2.get('rhythm_score',0):.3f} style={r2.get('style_score',0):.3f}")
