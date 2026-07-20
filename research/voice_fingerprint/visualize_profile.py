"""VFP-04 Task 6: Publication-quality voice profile visualizations.

7 charts, dark theme, 300 DPI, 12x8in, saved to charts/.
Reads profile_viz_data.json + voice_profile.json (no recomputation).
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

DIR = r"D:\Projects\SCRVNR\research\voice_fingerprint"
CHARTS = os.path.join(DIR, "charts")
os.makedirs(CHARTS, exist_ok=True)

# Dark theme consistent with portfolio aesthetic
BG = "#0f1115"
PANEL = "#161a21"
FG = "#e6e6e6"
GRID = "#2a2f3a"
ACCENT = "#5ac8fa"
PALETTE = ["#5ac8fa", "#ff9f43", "#2ecc71", "#e74c3c", "#a29bfe",
           "#f1c40f", "#e84393", "#1abc9c", "#fd79a8", "#74b9ff", "#dfe6e9"]

plt.rcParams.update({
    "figure.facecolor": BG, "axes.facecolor": PANEL, "savefig.facecolor": BG,
    "text.color": FG, "axes.labelcolor": FG, "xtick.color": FG,
    "ytick.color": FG, "axes.edgecolor": GRID, "grid.color": GRID,
    "font.family": "sans-serif", "axes.titlesize": 16, "axes.titleweight": "bold",
    "figure.figsize": (12, 8), "savefig.dpi": 300,
})

with open(os.path.join(DIR, "profile_viz_data.json"), encoding="utf-8") as f:
    VIZ = json.load(f)
with open(os.path.join(DIR, "voice_profile.json"), encoding="utf-8") as f:
    PROFILE = json.load(f)


def save(fig, name):
    fig.tight_layout()
    path = os.path.join(CHARTS, name)
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print(f"  saved {name}")


def chart1_kite():
    """Violin plot: mean_zipf distribution per register."""
    regs = sorted(VIZ["zipf_by_register"], key=lambda r: -len(VIZ["zipf_by_register"][r]))
    data = [VIZ["zipf_by_register"][r] for r in regs]
    fig, ax = plt.subplots()
    parts = ax.violinplot(data, showmedians=True, widths=0.85)
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(PALETTE[i % len(PALETTE)])
        pc.set_alpha(0.75)
    for k in ("cmins", "cmaxes", "cbars", "cmedians"):
        parts[k].set_edgecolor(FG)
        parts[k].set_linewidth(0.8)
    david = PROFILE["global"]["mean_zipf"]
    claude = PROFILE["claude_baseline_comparison"]["claude_baseline_estimate"]["mean_zipf"]
    ax.axhline(david, color="#2ecc71", ls="--", lw=1.5,
               label=f"David global mean ({david:.2f})")
    ax.axhline(claude, color="#e74c3c", ls="--", lw=1.5,
               label=f"Claude baseline est. ({claude:.2f})")
    ax.set_xticks(range(1, len(regs) + 1))
    ax.set_xticklabels(regs, rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Per-message mean Zipf score")
    ax.set_title("David's Vocabulary Rarity Distribution by Register")
    ax.text(0.01, 0.02,
            "StoryScope percentiles (human 0.71 / AI 0.49) are not directly "
            "convertible to Zipf;\nClaude baseline estimated from HIGH-contamination messages.",
            transform=ax.transAxes, fontsize=8, color="#9aa3b2")
    ax.legend(loc="upper right", facecolor=PANEL, edgecolor=GRID)
    ax.grid(axis="y", alpha=0.4)
    save(fig, "kite_shape_by_register.png")


def chart2_bimodality():
    """Overlaid histogram + KDE of sentence lengths: TECH and CREATIVE_DIRECTION."""
    fig, ax = plt.subplots()
    for reg, color in [("TECH", ACCENT), ("CREATIVE_DIRECTION", "#ff9f43")]:
        vals = [v for v in VIZ["sentlen_by_register"][reg] if v <= 60]
        bc = PROFILE["registers"][reg]["rhythm"]["bimodality_coefficient"]
        sns.histplot(vals, bins=48, kde=True, stat="density", color=color,
                     alpha=0.45, ax=ax, label=f"{reg} (BC={bc})",
                     edgecolor="none")
    ax.set_xlabel("Mean sentence length (words per message)")
    ax.set_ylabel("Density")
    ax.set_title("Bimodal Sentence Length in Technical and Creative Registers")
    ax.legend(facecolor=PANEL, edgecolor=GRID)
    ax.grid(alpha=0.4)
    save(fig, "sentence_bimodality.png")


def chart3_radar():
    """Radar chart: 6 normalized feature axes, top 5 registers by volume."""
    regs = ["TECH", "CASUAL", "PROFESSIONAL", "MECHANICAL", "INVESTIGATE"]
    fields = ["mean_zipf", "contraction_rate", "caps_emphasis_rate",
              "profanity_rate", "question_density", "mean_sentence_len"]
    # Normalize each field 0-1 across ALL registers
    all_vals = {f: [VIZ["radar_fields"][r][f] for r in VIZ["radar_fields"]]
                for f in fields}
    lo = {f: min(all_vals[f]) for f in fields}
    hi = {f: max(all_vals[f]) for f in fields}
    angles = np.linspace(0, 2 * np.pi, len(fields), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
    ax.set_facecolor(PANEL)
    for i, reg in enumerate(regs):
        vals = [(VIZ["radar_fields"][reg][f] - lo[f]) / ((hi[f] - lo[f]) or 1)
                for f in fields]
        vals += vals[:1]
        ax.plot(angles, vals, color=PALETTE[i], lw=2, label=reg)
        ax.fill(angles, vals, color=PALETTE[i], alpha=0.12)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(fields, fontsize=9)
    ax.set_yticklabels([])
    ax.set_title("Register Feature Radar — Distinct Shapes in Feature Space", pad=24)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1),
              facecolor=PANEL, edgecolor=GRID)
    save(fig, "register_radar.png")


def chart4_typos():
    """Bar chart: top 20 consistent typos by occurrence count."""
    typos = sorted(VIZ["typos_top20"], key=lambda t: -t["occurrences"])[:20]
    words = [t["word"] for t in typos][::-1]
    occs = [t["occurrences"] for t in typos][::-1]
    looks = [t["looks_like"] for t in typos][::-1]
    fig, ax = plt.subplots()
    bars = ax.barh(words, occs, color=ACCENT, alpha=0.85)
    for bar, lk in zip(bars, looks):
        ax.text(bar.get_width() + max(occs) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"→ {lk}", va="center", fontsize=8, color="#9aa3b2")
    ax.set_xlabel("Total occurrences in corpus")
    ax.set_title("David's Typographic Fingerprint — Most Consistent Non-Standard Spellings")
    ax.grid(axis="x", alpha=0.4)
    save(fig, "typo_fingerprint.png")


def _gradient_bar(pairs, ylabel, title, fname, highlight=None):
    names = [p[0] for p in pairs]
    vals = [p[1] or 0 for p in pairs]
    colors = ["#e74c3c" if n == highlight else ACCENT for n in names]
    fig, ax = plt.subplots()
    ax.bar(names, vals, color=colors, alpha=0.9)
    for i, v in enumerate(vals):
        ax.text(i, v, f"{v:.2f}", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticklabels(names, rotation=30, ha="right", fontsize=9)
    ax.grid(axis="y", alpha=0.4)
    save(fig, fname)


def chart5_profanity():
    _gradient_bar(VIZ["profanity_gradient"],
                  "Profanity per 1,000 words (weighted mean)",
                  "Profanity Rate by Register (per 1,000 words)",
                  "profanity_gradient.png", highlight="FRUSTRATED")


def chart6_contractions():
    _gradient_bar(VIZ["contraction_gradient"],
                  "Contractions per 100 words (weighted mean)",
                  "Contraction Rate by Register — Formality Gradient",
                  "contraction_spectrum.png")


def chart7_composition():
    """Two donuts: messages by register vs words by register."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 8))
    for ax, data, label in [
        (ax1, VIZ["register_counts"], "Messages by Register"),
        (ax2, VIZ["register_words"], "Words by Register"),
    ]:
        items = sorted(data.items(), key=lambda kv: -kv[1])
        names = [k for k, _ in items]
        vals = [v for _, v in items]
        total = sum(vals)
        wedges, _, autotexts = ax.pie(
            vals, colors=PALETTE[:len(vals)], startangle=90,
            wedgeprops={"width": 0.42, "edgecolor": BG},
            autopct=lambda p: f"{p:.0f}%" if p >= 3 else "",
            pctdistance=0.79, textprops={"fontsize": 8, "color": BG})
        for at in autotexts:
            at.set_fontweight("bold")
        ax.set_title(f"{label}\n({total:,} total)", fontsize=13)
        ax.legend(wedges, names, loc="lower center", ncol=3, fontsize=7,
                  bbox_to_anchor=(0.5, -0.18), facecolor=PANEL, edgecolor=GRID)
    fig.suptitle("Corpus Composition — Message Frequency vs Word Volume",
                 fontsize=16, fontweight="bold")
    save(fig, "corpus_composition.png")


if __name__ == "__main__":
    print("Generating charts...")
    chart1_kite()
    chart2_bimodality()
    chart3_radar()
    chart4_typos()
    chart5_profanity()
    chart6_contractions()
    chart7_composition()
    print("All 7 charts complete.")
