"""Three-way decomposition: original v3 vs v4 vs v5 (Rhythm Doctrine run). Matched sections."""
import sys, re, io, atexit
sys.path.insert(0, r"D:\Projects\SCRVNR")

_buf = io.StringIO()
class _Tee:
    def write(self, s):
        _buf.write(s)
        try:
            sys.__stdout__.write(s)
        except Exception:
            pass
    def flush(self):
        try:
            sys.__stdout__.flush()
        except Exception:
            pass
sys.stdout = _Tee()

def _dump():
    with open(r"D:\Projects\SCRVNR\learning\scripts\threeway_out.txt", "w", encoding="utf-8") as f:
        f.write(_buf.getvalue())
atexit.register(_dump)

from core.pipeline import VoicePipeline

pipe = VoicePipeline()
c = pipe.centrifuge

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
    m = re.search(r'^### VI\.', t, flags=re.MULTILINE)
    head = t[:m.start()] if m else t
    m9 = re.search(r'^### IX\.', t, flags=re.MULTILINE)
    tail = t[m9.start():] if m9 else ''
    return head + "\n" + tail

orig = matched_span(load(r"D:\Projects\SCRVNR\by-any-means-original-june13.md"))
orig = re.sub(r'\*\[Remainder of Section V[^\]]*\]\*', '', orig)
orig = re.sub(r'\*\[ORIGINAL DRAFT[^\]]*\]\*', '', orig)
v4 = matched_span(load(r"D:\Projects\SCRVNR\by-any-means-v4.md"))
v5 = matched_span(load(r"D:\Projects\SCRVNR\by-any-means-v5.md"))

REG = 'ARGUMENTATIVE'
target = c._targets.get(REG, {})
profile = c._profiles.get(REG, {})

print("TARGETS: zipf=%.3f pct_rare=%.2f sent_mean=%.2f sent_std=%.2f contraction=%.4f caps_profile=%.2f" % (
    target.get('target_mean_zipf', 0), target.get('target_pct_rare', 0),
    target.get('target_sentence_len_mean', 0), target.get('target_sentence_len_std', 0),
    target.get('target_contraction_rate', 0), profile.get('caps_emphasis_rate', 0)))

# FULL-TEXT pass too (whole essays, not just matched span) for v4 vs v5
sets = [
    ("ORIGINAL v3 (matched span)", strip_md(orig)),
    ("V4 (matched span)", strip_md(v4)),
    ("V5 (matched span)", strip_md(v5)),
    ("V4 (full)", strip_md(load(r"D:\Projects\SCRVNR\by-any-means-v4.md"))),
    ("V5 (full)", strip_md(load(r"D:\Projects\SCRVNR\by-any-means-v5.md"))),
]

for label, raw in sets:
    r = pipe.process(raw, register=REG)
    fixed = r['text']
    wc = len(fixed.split())
    rhythm = c._compute_rhythm(fixed)
    style = c._compute_style(fixed, wc)
    lengths = sorted(rhythm.get('lengths', []))
    p10 = lengths[int(len(lengths)*0.1)] if lengths else 0
    p90 = lengths[int(len(lengths)*0.9)] if lengths else 0
    mx = max(lengths) if lengths else 0
    print()
    print("--- %s ---" % label)
    print("overall=%.3f  rarity=%.3f rhythm=%.3f style=%.3f  (band %s)" % (
        r['overall_score'], r['score']['rarity_score'], r['score']['rhythm_score'],
        r['score']['style_score'], r['band']))
    print("sent: n=%d mean=%.2f std=%.2f p10=%d p90=%d max=%d" % (
        rhythm['count'], rhythm['mean_len'], rhythm['std_len'], p10, p90, mx))
    print("contraction_rate=%.3f/100w  em=%d  caps_rate=%.2f" % (
        style['contraction_rate'], style['em_dash_count'], style['caps_rate']))
    print("fixes: %s" % [(f['type'], f.get('count','')) for f in r['fixes']])
