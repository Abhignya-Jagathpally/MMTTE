#!/usr/bin/env python
"""Supplement Figure S4 — repeated-split stability.

A. per-feature-set mean C-index +/- 95% CI across 50 stratified splits
B. paired ΔC distribution + fraction of splits improved
"""
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import color_for, COLORS, save, plt

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "outputs" / "experiment0_open_gdc_os"


def main():
    lb = pd.read_csv(D / "repeated_split_leaderboard.csv").sort_values("mean_cindex")
    dd = pd.read_csv(D / "repeated_split_delta_cindex.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    ax = axes[0]
    y = range(len(lb))
    err = [lb["mean_cindex"] - lb["ci_low"], lb["ci_high"] - lb["mean_cindex"]]
    ax.barh(y, lb["mean_cindex"], xerr=err, color=[color_for(m) for m in lb["feature_set"]],
            edgecolor="black", lw=0.4, capsize=3)
    ax.set_yticks(y); ax.set_yticklabels(lb["feature_set"], fontsize=9)
    ax.set_xlabel("mean OS C-index over 50 splits"); ax.set_xlim(0.55, 0.82)
    ax.set_title("A. Repeated stratified-split stability")
    for i, (_, r) in enumerate(lb.iterrows()):
        ax.text(r["ci_high"] + 0.005, i, f"{r['mean_cindex']:.3f}±{r['sd_cindex']:.3f}", va="center", fontsize=7.5)

    ax = axes[1]
    ax.bar(range(len(dd)), dd["mean_delta"], yerr=[dd["mean_delta"] - dd["ci_low"], dd["ci_high"] - dd["mean_delta"]],
           color=COLORS["omics"], edgecolor="black", lw=0.4, capsize=4)
    ax.axhline(0, color="gray", ls=":")
    ax.set_xticks(range(len(dd))); ax.set_xticklabels(dd["comparison"], rotation=15, ha="right", fontsize=8)
    ax.set_ylabel("mean ΔC-index (95% CI)")
    ax.set_title("B. Paired ΔC vs clinical")
    for i, (_, r) in enumerate(dd.iterrows()):
        ax.text(i, r["ci_high"] + 0.004, f"improved {r['frac_splits_improved']*100:.0f}% of splits", ha="center", fontsize=7.5)
    fig.suptitle("S4. Repeated-split stability (open-GDC OS)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, "sfig4_repeated_split")


if __name__ == "__main__":
    main()
