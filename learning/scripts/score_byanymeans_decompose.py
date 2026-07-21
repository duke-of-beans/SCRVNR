"""Decompose the centrifuge gap: original v3 vs v4, every sub-score, actual targets."""
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
    with open(r"D:\Projects\SCRVNR\learning\scripts\decompose_out.txt", "w", encoding="utf-8") as f:
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

REG = 'ARGUMENTATIVE'
target = c._targets.get(REG, {})
profile = c._profiles.get(REG, {})

print("=" * 64)
print(f"TARGETS ({REG}) from voice.db")
print("=" * 64)
for k, v in sorted(target.items()):
    print(f"  target.{k} = {v}")
print(f"  profile.caps_emphasis_rate = {profile.get('caps_emphasis_rate')}")
print(f"  profile.is_bimodal = {profile.get('is_bimodal')}")

for label, raw in [("ORIGINAL v3", strip_md(orig)), ("V4", strip_md(v4))]:
    r = pipe.process(raw, register=REG)
    fixed = r['text']
    words = c._tokenize_words(fixed)
    wc = len(fixed.split())
    rarity = c._compute_rarity(words)
    rhythm = c._compute_rhythm(fixed)
    style = c._compute_style(fixed, wc)

    t_zipf = target.get('target_mean_zipf', 4.3); tol_z = max(target.get('tolerance_zipf', 0.8) * 1.5, 0.5)
    z_sub = max(0.0, 1.0 - abs(rarity['mean_zipf'] - t_zipf) / tol_z)
    t_rare = target.get('target_pct_rare', 6.0); tol_r = max(target.get('tolerance_rare', 3.0), 2.0)
    r_sub = max(0.0, 1.0 - abs(rarity['pct_rare'] - t_rare) / tol_r)
    t_mean = target.get('target_sentence_len_mean', 15.0); tol_s = max(target.get('tolerance_sentence', 5.0), 1.0)
    m_sub = max(0.0, 1.0 - abs(rhythm['mean_len'] - t_mean) / tol_s)
    t_std = target.get('target_sentence_len_std', 10.0)
    s_sub = max(0.0, 1.0 - abs(rhythm['std_len'] - t_std) / max(t_std * 0.5, 3.0))
    t_cont = target.get('target_contraction_rate', 0.4); tol_c = max(target.get('tolerance_contraction', 0.15), 0.05)
    cont_sub = max(0.0, 1.0 - abs(style['contraction_rate'] - t_cont) / tol_c)
    em = style['em_dash_count']
    em_sub = 1.0 if em == 0 else (0.4 if em <= 2 else 0.0)
    pcaps = profile.get('caps_emphasis_rate', 10.0)
    if pcaps and pcaps > 5.0:
        caps_sub = min(1.0, style['caps_rate'] / max(pcaps * 0.3, 1.0))
    else:
        caps_sub = 0.8

    print()
    print("=" * 64)
    print(f"{label}  (post-fix, scored text)  words={wc}")
    print("=" * 64)
    print(f"overall={r['overall_score']:.3f}  rarity={r['score']['rarity_score']:.3f}  rhythm={r['score']['rhythm_score']:.3f}  style={r['score']['style_score']:.3f}")
    print(f"[RARITY 0.4] mean_zipf={rarity['mean_zipf']:.3f} vs {t_zipf} (tol {tol_z:.2f}) -> {z_sub:.3f} x0.6")
    print(f"             pct_rare={rarity['pct_rare']:.2f}% vs {t_rare}% (tol {tol_r}) -> {r_sub:.3f} x0.4")
    print(f"[RHYTHM 0.3] sent_mean={rhythm['mean_len']:.2f} vs {t_mean} (tol {tol_s}) -> {m_sub:.3f} x0.6")
    print(f"             sent_std={rhythm['std_len']:.2f} vs {t_std} -> {s_sub:.3f} x0.4   (n={rhythm['count']})")
    print(f"[STYLE 0.3]  contraction_rate={style['contraction_rate']:.3f}/100w vs {t_cont} (tol {tol_c}) -> {cont_sub:.3f} x0.3")
    print(f"             em_dashes={em} -> {em_sub:.1f} x0.4")
    print(f"             caps_rate={style['caps_rate']:.2f}/1000w vs profile {pcaps} (sat at {max(pcaps*0.3,1.0) if pcaps else 'n/a'}) -> {caps_sub:.3f} x0.3")
    print(f"fixes applied: {[(f['type'], f.get('count','')) for f in r['fixes']]}")
