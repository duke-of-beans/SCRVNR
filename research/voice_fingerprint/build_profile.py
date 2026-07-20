"""VFP-04 Task 5: Voice profile generation — the synthesis step.

Streams features.jsonl + features_final.jsonl zipped (line-aligned) to build
per-register and global profiles with contamination weighting, plus a Claude
baseline ESTIMATE from HIGH-contamination messages' original features.
Streams final_corpus.jsonl once for word-level analysis (idiosyncratic words,
typo fingerprint). Also dumps profile_viz_data.json for visualize_profile.py.
"""
import json
import re
import statistics
import time
from collections import Counter, defaultdict
from functools import lru_cache

from scipy.stats import skew as sskew, kurtosis as skurtosis
from wordfreq import zipf_frequency, top_n_list

DIR = r"D:\Projects\SCRVNR\research\voice_fingerprint"
F_ORIG = DIR + r"\features.jsonl"
F_FINAL = DIR + r"\features_final.jsonl"
CORPUS = DIR + r"\final_corpus.jsonl"
OUT_JSON = DIR + r"\voice_profile.json"
OUT_MD = DIR + r"\voice_profile.md"
OUT_VIZ = DIR + r"\profile_viz_data.json"

MIN_REGISTER_N = 20
RARITY_BINS = [(1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 99)]
SENTLEN_BINS = [(1, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 999)]

RE_ARTIFACT = re.compile(r"[\\/:#@\d_>{}\[\]()=+*&%$|~`^]|\.\w")
STOP_SUFFIXES = ("'s", "s'")

# Known technical terms/brands — legitimate vocabulary, not typos
TECH_TERMS = {
    "cjs", "mjs", "jsx", "tsx", "esm", "yaml", "json", "docx", "pptx", "xlsx",
    "redis", "cors", "npm", "npx", "thca", "cbd", "krown", "kanna", "cowork",
    "openai", "anthropic", "webpack", "vite", "babel", "prisma", "errno",
    "utils", "ghm", "skus", "reactjs", "nextjs", "nodejs", "oaksterdam",
    "uncaught", "refactor", "architected", "walbro", "bsfc", "kernl", "scrvnr",
    "quaife", "recurse", "limen", "msos", "coas", "tcv", "whp", "fpp", "blg",
}

# Raw code tokens / package-manager vocabulary — excluded from the
# idiosyncratic-words list per sprint spec (keep domain vocabulary)
CODE_TERMS = {
    "src", "const", "tsx", "jsx", "cjs", "mjs", "json", "yaml", "dist", "env",
    "classname", "favicon", "errno", "appdata", "exe", "localhost", "webpack",
    "webpack-internal", "next-devtools", "npx", "npm", "utils", "readme",
    "constructor", "async", "dep", "config", "auth", "vite", "babel", "prisma",
    "esm", "docx", "pptx", "xlsx", "svg", "typeerror", "parse", "settimeout",
    "middleware", "opacity", "req", "res", "filepath", "devtools", "onclick",
    "boolean", "gdf", "arp", "hmr", "rgba", "figma",
}

# Ultra-common typos that score Zipf >= 2.0 (typos frequent enough on the
# internet to register in wordfreq) — force-included in the fingerprint
KNOWN_TYPO_MAP = {
    "hte": "the", "teh": "the", "adn": "and", "taht": "that", "waht": "what",
    "jsut": "just", "wiht": "with", "thier": "their", "recieve": "receive",
}


@lru_cache(maxsize=200000)
def zipf(word):
    return zipf_frequency(word, "en")


def hist_counts(values, bins):
    counts = [0] * len(bins)
    for v in values:
        for i, (lo, hi) in enumerate(bins):
            if lo <= v < hi:
                counts[i] += 1
                break
    return counts


def bimodality_coefficient(values):
    """BC = (g1^2 + 1) / (g2 + 3(n-1)^2 / ((n-2)(n-3))); > 0.555 suggests bimodal."""
    n = len(values)
    if n < 4:
        return None
    g1 = float(sskew(values, bias=False))
    g2 = float(skurtosis(values, bias=False))  # excess kurtosis
    denom = g2 + 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))
    if denom == 0:
        return None
    return round((g1 ** 2 + 1) / denom, 4)


def edit_distance(a, b, maxd=2):
    """Basic Levenshtein with early bail-out beyond maxd."""
    if abs(len(a) - len(b)) > maxd:
        return maxd + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        row_min = i
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
            row_min = min(row_min, cur[-1])
        if row_min > maxd:
            return maxd + 1
        prev = cur
    return prev[-1]


def wmean(pairs):
    """Weighted mean over (value, weight) pairs; None-safe."""
    num = den = 0.0
    for v, w in pairs:
        if v is None:
            continue
        num += v * w
        den += w
    return round(num / den, 4) if den else None


RATE_FIELDS = [
    "contraction_rate", "caps_emphasis_rate", "profanity_rate",
    "question_density", "number_density", "mean_zipf", "median_zipf",
    "pct_rare", "pct_very_rare", "mean_sentence_len",
]
COUNT_FIELDS = ["double_period_count", "hyphen_count", "em_dash_count",
                "exclamation_count", "ellipsis_count"]
BOOL_FIELDS = ["has_file_path", "has_url", "has_dollar_amount"]


def pass1_features():
    """Zip features.jsonl + features_final.jsonl; accumulate per-register stats."""
    reg = defaultdict(lambda: {
        "n": 0, "n_words": 0, "w_words": 0.0,
        "zipf_vals": [], "zipf_w": [], "sentlen_vals": [], "msglen_vals": [],
        "rates": defaultdict(list),        # field -> [(val, weight)]
        "counts": defaultdict(float),      # field -> weighted count sum
        "bools": defaultdict(float),       # field -> weighted true count
        "wsum": 0.0,
        "rare_words": Counter(),           # per-register rarest_word candidates
    })
    pre_em = {"em": 0, "words": 0}
    post_em = {"em": 0.0, "words": 0.0}
    claude = defaultdict(list)             # baseline from HIGH originals
    n_high = 0

    with open(F_ORIG, "r", encoding="utf-8") as fo, \
         open(F_FINAL, "r", encoding="utf-8") as ff:
        for lo, lf in zip(fo, ff):
            orig = json.loads(lo)
            rec = json.loads(lf)
            r = rec.get("register", "UNTAGGED")
            w = rec.get("weight", 1.0)
            wc = rec.get("word_count") or 0
            a = reg[r]
            a["n"] += 1
            a["n_words"] += wc
            a["w_words"] += wc * w
            a["wsum"] += w

            if rec.get("mean_zipf") is not None:
                a["zipf_vals"].append(rec["mean_zipf"])
                a["zipf_w"].append(w)
            if rec.get("mean_sentence_len"):
                a["sentlen_vals"].append(rec["mean_sentence_len"])
            if wc:
                a["msglen_vals"].append(wc)
            for f in RATE_FIELDS:
                a["rates"][f].append((rec.get(f), w))
            for f in COUNT_FIELDS:
                a["counts"][f] += (rec.get(f) or 0) * w
            for f in BOOL_FIELDS:
                a["bools"][f] += w if rec.get(f) else 0.0
            rw = rec.get("rarest_word")
            if rw and rec.get("min_zipf") is not None and rec["min_zipf"] < 3.0:
                a["rare_words"][rw] += 1

            # Pre/post em-dash comparison (original vs weighted final)
            ow = orig.get("word_count") or 0
            pre_em["em"] += orig.get("em_dash_count") or 0
            pre_em["words"] += ow
            post_em["em"] += (rec.get("em_dash_count") or 0) * w
            post_em["words"] += wc * w

            # Claude baseline ESTIMATE: original features of HIGH messages
            if rec.get("contamination_level") == "high":
                n_high += 1
                for f in ["mean_zipf", "pct_rare", "contraction_rate",
                          "caps_emphasis_rate", "mean_sentence_len",
                          "question_density"]:
                    if orig.get(f) is not None:
                        claude[f].append(orig[f])
                if ow:
                    claude["em_dash_rate"].append((orig.get("em_dash_count") or 0) / ow * 1000)
                    claude["hyphen_rate"].append((orig.get("hyphen_count") or 0) / ow * 1000)
    return reg, pre_em, post_em, claude, n_high


RE_TOKEN = re.compile(r"[a-zA-Z''\-]+")
RE_STRIP = re.compile(r"^[^a-zA-Z]+|[^a-zA-Z]+$")


def pass2_words():
    """Stream final_corpus.jsonl; count rare words (zipf < 3) across messages.

    HIGH-contamination messages contribute clean_text (David's isolated prose)
    instead of the contaminated original.
    """
    word_msgs = Counter()
    word_occs = Counter()
    total_msgs = 0
    with open(CORPUS, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            msg = json.loads(line)
            total_msgs += 1
            text = msg.get("clean_text") if msg.get("contamination_level") == "high" \
                else msg.get("text", "")
            if not text:
                continue
            seen = set()
            for tok in RE_TOKEN.findall(text.lower()):
                wd = RE_STRIP.sub("", tok)
                if len(wd) < 3:
                    continue
                z = zipf(wd)
                if 0 < z < 3.0:
                    word_occs[wd] += 1
                    seen.add(wd)
            for wd in seen:
                word_msgs[wd] += 1
    return word_msgs, word_occs, total_msgs


def is_artifact(word):
    return bool(RE_ARTIFACT.search(word)) or word.startswith("c:") or len(word) > 25


def find_typos(word_msgs):
    """Typo = zipf < 2.0, 10+ messages, edit distance 1-2 from a common word."""
    common = [w for w in top_n_list("en", 12000) if zipf(w) > 4.0 and w.isalpha()]
    by_len = defaultdict(list)
    for w in common:
        by_len[len(w)].append(w)

    typos = {}
    for wd, mc in word_msgs.items():
        if mc < 10 or is_artifact(wd) or not wd.isalpha():
            continue
        if zipf(wd) >= 2.0 or wd in TECH_TERMS or wd in CODE_TERMS:
            continue
        best = None
        # Genuine misspellings match a common word AT LEAST as long as the
        # typo (hte->the, graet->great); matches to shorter words (docx->doc,
        # utils->til) are tech vocabulary, not typos.
        for ln in range(len(wd), len(wd) + 3):
            for cand in by_len.get(ln, []):
                d = edit_distance(wd, cand)
                if d <= 2 and (best is None or d < best[1]):
                    best = (cand, d)
                    if d == 1:
                        break
            if best and best[1] == 1:
                break
        if best:
            typos[wd] = {"looks_like": best[0], "edit_distance": best[1],
                         "messages": mc}

    # Force-include ultra-common typos that clear the Zipf 2.0 gate
    for wd, target in KNOWN_TYPO_MAP.items():
        if wd not in typos and word_msgs.get(wd, 0) >= 10:
            typos[wd] = {"looks_like": target,
                         "edit_distance": edit_distance(wd, target),
                         "messages": word_msgs[wd]}
    return typos


def build_register_profile(name, a, typo_set):
    zv = a["zipf_vals"]
    sv = a["sentlen_vals"]
    mv = a["msglen_vals"]
    ww = a["w_words"] or 1.0
    bc = bimodality_coefficient(sv) if len(sv) >= 4 else None
    top_rare = [w for w, _ in a["rare_words"].most_common(200)
                if not is_artifact(w) and w not in typo_set][:20]
    r = lambda f: wmean(a["rates"][f])
    per1k = lambda f: round(a["counts"][f] / ww * 1000, 4)
    pct = lambda f: round(a["bools"][f] / a["wsum"] * 100, 2) if a["wsum"] else None
    return {
        "register": name,
        "n_messages": a["n"],
        "n_words": a["n_words"],
        "vocabulary": {
            "mean_zipf": r("mean_zipf"),
            "median_zipf": round(statistics.median(zv), 3) if zv else None,
            "std_zipf": round(statistics.pstdev(zv), 3) if len(zv) > 1 else None,
            "pct_rare": r("pct_rare"),
            "pct_very_rare": r("pct_very_rare"),
            "rarity_histogram": hist_counts(zv, RARITY_BINS),
            "kite_skew": round(float(sskew(zv)), 4) if len(zv) > 2 else None,
            "top_20_rare_words": top_rare,
        },
        "rhythm": {
            "mean_sentence_len": r("mean_sentence_len"),
            "median_sentence_len": round(statistics.median(sv), 2) if sv else None,
            "std_sentence_len": round(statistics.pstdev(sv), 2) if len(sv) > 1 else None,
            "bimodality_coefficient": bc,
            "is_bimodal": bool(bc is not None and bc > 0.555),
            "sentence_len_histogram": hist_counts(sv, SENTLEN_BINS),
            "mean_message_len": round(statistics.mean(mv), 2) if mv else None,
            "median_message_len": round(statistics.median(mv), 1) if mv else None,
        },

        "style": {
            "contraction_rate": r("contraction_rate"),
            "caps_emphasis_rate": r("caps_emphasis_rate"),
            "profanity_rate": r("profanity_rate"),
            "question_density": r("question_density"),
            "double_period_rate": per1k("double_period_count"),
            "hyphen_rate": per1k("hyphen_count"),
            "em_dash_rate": per1k("em_dash_count"),
            "exclamation_rate": per1k("exclamation_count"),
            "ellipsis_rate": per1k("ellipsis_count"),
        },
        "specificity": {
            "pct_with_file_paths": pct("has_file_path"),
            "pct_with_urls": pct("has_url"),
            "pct_with_dollar_amounts": pct("has_dollar_amount"),
            "number_density": r("number_density"),
        },
    }


def main():
    start = time.time()
    print("Pass 1: streaming feature files...")
    reg, pre_em, post_em, claude, n_high = pass1_features()
    print(f"  {sum(a['n'] for a in reg.values()):,} records ({time.time()-start:.1f}s)")

    print("Pass 2: streaming corpus for word-level analysis...")
    word_msgs, word_occs, total_msgs = pass2_words()
    print(f"  {len(word_msgs):,} distinct rare words ({time.time()-start:.1f}s)")

    print("Typo fingerprint detection...")
    typos = find_typos(word_msgs)
    typo_set = set(typos)
    print(f"  {len(typos)} consistent typos found ({time.time()-start:.1f}s)")

    profiles = {}
    for name, a in sorted(reg.items(), key=lambda kv: -kv[1]["n"]):
        if a["n"] > MIN_REGISTER_N:
            profiles[name] = build_register_profile(name, a, typo_set)

    # 5B — Global aggregates
    all_zipf = [v for a in reg.values() for v in a["zipf_vals"]]
    total_msg = sum(a["n"] for a in reg.values())
    total_words = sum(a["n_words"] for a in reg.values())
    idio = [
        {"word": w, "zipf": round(zipf(w), 2), "occurrences": word_occs[w],
         "messages": word_msgs[w]}
        for w, _ in word_occs.most_common(2000)
        if word_msgs[w] >= 10 and not is_artifact(w) and w not in typo_set
        and w not in CODE_TERMS
    ][:50]
    typo_list = sorted(
        [{"word": w, **info, "occurrences": word_occs[w], "zipf": round(zipf(w), 2)}
         for w, info in typos.items()],
        key=lambda t: -t["messages"])
    contraction_grad = sorted(
        [(n, p["style"]["contraction_rate"]) for n, p in profiles.items()],
        key=lambda kv: -(kv[1] or 0))
    profanity_grad = sorted(
        [(n, p["style"]["profanity_rate"]) for n, p in profiles.items()],
        key=lambda kv: -(kv[1] or 0))

    pre_rate = round(pre_em["em"] / pre_em["words"] * 1000, 4)
    post_rate = round(post_em["em"] / post_em["words"] * 1000, 4)

    # 5C — Claude baseline ESTIMATE from HIGH-contamination originals
    cb = {k: round(statistics.mean(v), 4) for k, v in claude.items() if v}
    david_global = {
        "mean_zipf": round(statistics.mean(all_zipf), 4),
        "pct_rare": wmean([(v, w) for a in reg.values()
                           for v, w in a["rates"]["pct_rare"]]),
        "contraction_rate": wmean([(v, w) for a in reg.values()
                                   for v, w in a["rates"]["contraction_rate"]]),
        "mean_sentence_len": wmean([(v, w) for a in reg.values()
                                    for v, w in a["rates"]["mean_sentence_len"]]),
        "em_dash_rate": post_rate,
    }
    delta = {k: round(david_global[k] - cb[k], 4) for k in
             ["mean_zipf", "pct_rare", "contraction_rate", "mean_sentence_len",
              "em_dash_rate"] if k in cb and david_global.get(k) is not None}

    profile = {
        "generated": time.strftime("%Y-%m-%d %H:%M"),
        "sprint": "VFP-04",
        "corpus": {
            "total_messages": total_msg,
            "total_words": total_words,
            "registers_profiled": len(profiles),
            "em_dash_rate_pre_decontamination_per_1k_words": pre_rate,
            "em_dash_rate_post_decontamination_per_1k_words": post_rate,
        },
        "registers": profiles,
        "global": {
            "mean_zipf": david_global["mean_zipf"],
            "rarity_histogram": hist_counts(all_zipf, RARITY_BINS),
            "kite_skew": round(float(sskew(all_zipf)), 4),
            "idiosyncratic_words_top50": idio,
            "consistent_typos": typo_list,
            "contraction_gradient": contraction_grad,
            "profanity_gradient": profanity_grad,
        },
        "claude_baseline_comparison": {
            "NOTE": ("ESTIMATE, not a measurement. No clean Claude-only corpus "
                     "exists; the baseline is derived from the original features "
                     f"of the {n_high} HIGH-contamination messages, which mix "
                     "Claude prose with David's. Treat deltas as directional."),
            "claude_baseline_estimate": cb,
            "david_global": david_global,
            "delta_david_minus_claude": delta,
        },
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    print(f"Wrote {OUT_JSON}")

    viz = {
        "zipf_by_register": {n: reg[n]["zipf_vals"] for n in profiles},
        "sentlen_by_register": {n: reg[n]["sentlen_vals"] for n in profiles},
        "typos_top20": typo_list[:20],
        "contraction_gradient": contraction_grad,
        "profanity_gradient": profanity_grad,
        "register_counts": {n: p["n_messages"] for n, p in profiles.items()},
        "register_words": {n: p["n_words"] for n, p in profiles.items()},
        "radar_fields": {n: {
            "mean_zipf": p["vocabulary"]["mean_zipf"],
            "contraction_rate": p["style"]["contraction_rate"],
            "caps_emphasis_rate": p["style"]["caps_emphasis_rate"],
            "profanity_rate": p["style"]["profanity_rate"],
            "question_density": p["style"]["question_density"],
            "mean_sentence_len": p["rhythm"]["mean_sentence_len"],
        } for n, p in profiles.items()},
    }
    with open(OUT_VIZ, "w", encoding="utf-8") as f:
        json.dump(viz, f, ensure_ascii=False)
    print(f"Wrote {OUT_VIZ}")

    write_md(profile)
    print(f"Wrote {OUT_MD}")
    print(f"\n=== Profile Generation Complete ({time.time()-start:.1f}s) ===")
    print(f"Registers profiled: {list(profiles)}")
    print(f"Em-dash rate: {pre_rate} -> {post_rate} per 1k words")
    print(f"Typos: {len(typo_list)} | Idiosyncratic words: {len(idio)}")


def write_md(p):
    g = p["global"]
    cb = p["claude_baseline_comparison"]
    lines = []
    w = lines.append
    w("# David's Quantitative Voice Profile (VFP-04)")
    w("")
    w(f"Generated {p['generated']} from {p['corpus']['total_messages']:,} messages / "
      f"{p['corpus']['total_words']:,} words. {p['corpus']['registers_profiled']} registers profiled.")
    w("")
    w("## Headline Findings")
    w("")
    w(f"- **Global mean Zipf: {g['mean_zipf']}** with kite skew {g['kite_skew']} "
      "(negative skew = long tail into rare vocabulary, fat top at common words - "
      "the human 'kite shape').")
    w(f"- **Em-dash rate: {p['corpus']['em_dash_rate_pre_decontamination_per_1k_words']} -> "
      f"{p['corpus']['em_dash_rate_post_decontamination_per_1k_words']} per 1,000 words** "
      "after decontamination (weighted). David's native punctuation is the hyphen.")
    w(f"- **{len(g['consistent_typos'])} consistent typos** form a typographic fingerprint - "
      "misspellings that recur across 10+ messages are identity markers, not noise.")
    w(f"- **{len(g['idiosyncratic_words_top50'])} idiosyncratic words** (rare in English, "
      "routine for David).")
    w("")
    w("## Per-Register Profiles")
    w("")
    w("| Register | N | Words | Mean Zipf | Kite Skew | Contract | Caps | Profanity | Q Density | Bimodal |")
    w("|----------|---|-------|-----------|-----------|----------|------|-----------|-----------|---------|")
    for name, r in p["registers"].items():
        v, s, rh = r["vocabulary"], r["style"], r["rhythm"]
        w(f"| {name} | {r['n_messages']:,} | {r['n_words']:,} | {v['mean_zipf']} | "
          f"{v['kite_skew']} | {s['contraction_rate']} | {s['caps_emphasis_rate']} | "
          f"{s['profanity_rate']} | {s['question_density']} | "
          f"{'YES' if rh['is_bimodal'] else 'no'} ({rh['bimodality_coefficient']}) |")
    w("")

    w("## Style Rates by Register (per message / per 1k words)")
    w("")
    w("| Register | Double-period | Hyphen | Em-dash | Exclamation | Ellipsis |")
    w("|----------|--------------|--------|---------|-------------|----------|")
    for name, r in p["registers"].items():
        s = r["style"]
        w(f"| {name} | {s['double_period_rate']} | {s['hyphen_rate']} | "
          f"{s['em_dash_rate']} | {s['exclamation_rate']} | {s['ellipsis_rate']} |")
    w("")
    w("## Contraction Gradient (formality spectrum)")
    w("")
    for name, rate in g["contraction_gradient"]:
        w(f"1. **{name}**: {rate}")
    w("")
    w("## Profanity Gradient")
    w("")
    for name, rate in g["profanity_gradient"]:
        w(f"1. **{name}**: {rate}")
    w("")
    w("## Typographic Fingerprint (top 20 consistent typos)")
    w("")
    w("| Typo | Looks like | Edit dist | Messages | Occurrences |")
    w("|------|-----------|-----------|----------|-------------|")
    for t in g["consistent_typos"][:20]:
        w(f"| {t['word']} | {t['looks_like']} | {t['edit_distance']} | "
          f"{t['messages']} | {t['occurrences']} |")
    w("")
    w("## Idiosyncratic Vocabulary (top 50)")
    w("")
    w(", ".join(f"**{t['word']}** ({t['messages']} msgs)"
                for t in g["idiosyncratic_words_top50"]))
    w("")

    w("## Claude Baseline Comparison (ESTIMATE)")
    w("")
    w(f"> {cb['NOTE']}")
    w("")
    w("| Feature | Claude (est.) | David (global) | Delta (David - Claude) |")
    w("|---------|---------------|----------------|------------------------|")
    for k in cb["delta_david_minus_claude"]:
        w(f"| {k} | {cb['claude_baseline_estimate'].get(k)} | "
          f"{cb['david_global'].get(k)} | {cb['delta_david_minus_claude'][k]} |")
    w("")
    w("The delta IS the centrifuge target: generation-time constraints should push "
      "output away from the Claude baseline toward David's measured values, "
      "per-register.")
    w("")
    w("---")
    w("Self-contained summary - the full structured data lives in voice_profile.json. "
      "Charts in charts/. Generated by build_profile.py (VFP-04 Task 5).")
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
