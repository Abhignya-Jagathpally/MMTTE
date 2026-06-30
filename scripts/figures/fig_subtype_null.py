#!/usr/bin/env python
"""Figure 3 (headline, negative result) — the subtype-aware NULL.

Stage D: small-subtype calibration improvement (independent − HSS IBS) under REAL
labels vs negative controls. If real ≈ permuted/random, the benefit is shared-trunk
regularization, NOT cytogenetic biology. This is now a headline figure: a clean,
pre-registered negative result.

PLOT-ONLY. Reads outputs/stageD_open_gdc_os/stageD_detail.csv (per-fold) for CIs and
stageD_negative_controls.csv (means). Endpoint = OS technical validation; subtypes
are sequencing-inferred (NOT FISH).
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import COLORS, save, plt

ROOT = Path(__file__).resolve().parents[2]
SD = ROOT / "outputs" / "stageD_open_gdc_os"
COND_ORDER = ["real", "permuted", "random", "lambda0", "lambda_huge"]
COND_LABEL = {"real": "REAL labels", "permuted": "permuted", "random": "random",
              "lambda0": "λ=0 (no distill)", "lambda_huge": "λ→∞"}
COND_COLOR = {"real": COLORS["confirmed"], "permuted": COLORS["blocked"],
              "random": COLORS["caution"], "lambda0": COLORS["model"], "lambda_huge": "#9467bd"}


def _small_subtypes(detail):
    prev = detail.groupby("subtype")["mean_test_n"].mean() if "mean_test_n" in detail else None
    # least-prevalent two CNV subtypes (match experiments_stageD._decide)
    counts = detail.groupby("subtype")["test_n"].mean() if "test_n" in detail else prev
    return list(counts.sort_values().index[:2])


def main():
    detail = pd.read_csv(SD / "stageD_detail.csv")
    detail = detail[detail.get("status", "ok") == "ok"].copy()
    detail["improvement"] = detail["ibs_independent"] - detail["ibs_hss"]
    small = _small_subtypes(detail)
    sub = detail[detail.subtype.isin(small)]

    # per-condition mean ± 95% CI across (subtype,fold) of small subtypes
    stats = {}
    for c in COND_ORDER:
        v = sub[sub.condition == c]["improvement"].dropna().values
        if len(v) == 0:
            continue
        m, se = v.mean(), v.std(ddof=1) / np.sqrt(len(v)) if len(v) > 1 else (v.mean(), 0)
        stats[c] = (m, 1.96 * se, len(v))

    fig, ax = plt.subplots(figsize=(7.0, 3.3))
    ax.axhline(0, color="#333333", lw=1.0)
    xs = range(len(stats))
    for x, c in zip(xs, [c for c in COND_ORDER if c in stats]):
        m, ci, n = stats[c]
        ax.errorbar(x, m, yerr=ci, fmt="o", color=COND_COLOR[c], ms=8, capsize=4, lw=2)
        ax.text(x, m + ci + 0.004, f"{m:+.3f}", ha="center", fontsize=8, color=COND_COLOR[c])
    ax.set_xticks(list(xs))
    ax.set_xticklabels([COND_LABEL[c] for c in COND_ORDER if c in stats], fontsize=8.5)
    ax.set_ylabel("small-subtype IBS improvement\n(independent − HSS; +ve = HSS better)", fontsize=9)
    real_m = stats["real"][0]
    ctrl_max = max(stats["permuted"][0], stats["random"][0])
    ax.set_title(f"Subtype-aware NULL: REAL ({real_m:+.3f}) ≤ scrambled controls "
                 f"(max {ctrl_max:+.3f})\n→ benefit is regularization, not cytogenetic biology (pre-registered STOP)",
                 fontsize=9.5)
    ax.annotate("scrambled labels help\nas much or MORE", xy=(1, stats["permuted"][0]),
                xytext=(1.4, stats["permuted"][0] + 0.02), fontsize=7.5, color=COLORS["blocked"],
                arrowprops=dict(arrowstyle="->", color=COLORS["blocked"], lw=1))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.text(0.01, -0.03, f"Small subtypes: {', '.join(small)} (sequencing-inferred, NOT FISH). "
             "OS technical validation only.", fontsize=6.8, color="#555555")
    save(fig, "fig3_subtype_null")


if __name__ == "__main__":
    main()
