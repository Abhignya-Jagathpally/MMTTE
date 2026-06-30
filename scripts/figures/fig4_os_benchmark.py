#!/usr/bin/env python
"""Main Figure 4 — open-GDC OS benchmark (compact, journal-style).

A. same-cohort OS C-index ranking (mmSYGNAL = off-endpoint, orange)
B. claim badge: OS only / no relapse-PFS claim / no clinical use
Reproducible from sota_comparison.csv.
"""
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import color_for, COLORS, save, plt
import matplotlib.gridspec as gridspec

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "outputs" / "experiment0_open_gdc_os" / "sota_comparison.csv"


def main():
    df = pd.read_csv(CSV).sort_values("test_cindex", ascending=True)
    labels, vals = df["model"].tolist(), df["test_cindex"].tolist()
    colors = [color_for(m) for m in labels]

    fig = plt.figure(figsize=(7.2, 4.0))
    gs = gridspec.GridSpec(1, 1, left=0.30, right=0.97, top=0.88, bottom=0.13)
    ax = fig.add_subplot(gs[0])
    ax.barh(range(len(labels)), vals, color=colors, edgecolor="black", linewidth=0.4, height=0.74)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8.5)
    ax.set_xlim(0.55, 0.80)
    ax.set_xlabel("Held-out OS C-index  (N$_{test}$=182, 38 events)", fontsize=9)
    ax.tick_params(axis="x", labelsize=8)
    for i, v in enumerate(vals):
        ax.text(v - 0.006, i, f"{v:.3f}", va="center", ha="right", fontsize=8,
                color="white", fontweight="bold")
    ax.set_title("Same-cohort OS discrimination (Experiment 0)", fontsize=11, pad=8)
    ax.spines[["top", "right"]].set_visible(False)

    # claim badge (top-right inside axes)
    badge = ("Claim gate: OS only\n"
             "✓ technical validation\n"
             "✗ relapse/PFS claim\n"
             "✗ clinical use")
    ax.text(0.985, 0.04, badge, transform=ax.transAxes, ha="right", va="bottom",
            fontsize=7.6, family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", fc="#fff3e0", ec=COLORS["caution"], lw=1.0))
    save(fig, "fig4_os_benchmark")
    print("Caption: Same-cohort open-GDC OS discrimination. clinical+omics is strongest; "
          "mmSYGNAL (orange) is a relapse/PFS model shown as an OFF-ENDPOINT transfer "
          "comparator, not a same-task ranking. No relapse/PFS or clinical-use claim.")


if __name__ == "__main__":
    main()
