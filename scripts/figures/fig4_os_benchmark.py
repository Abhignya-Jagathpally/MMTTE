#!/usr/bin/env python
"""Main Figure 4 — open-GDC OS benchmark (same-cohort model ranking).

Reproducible horizontal bar chart from sota_comparison.csv. Off-endpoint
comparators (mmSYGNAL) are coloured orange and annotated, so the figure cannot be
read as a same-task ranking.
"""
from pathlib import Path
import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import color_for, COLORS, save, plt

ROOT = Path(__file__).resolve().parents[2]
CSV = ROOT / "outputs" / "experiment0_open_gdc_os" / "sota_comparison.csv"


def main():
    df = pd.read_csv(CSV).sort_values("test_cindex", ascending=True)
    labels = df["model"].tolist()
    vals = df["test_cindex"].tolist()
    colors = [color_for(m) for m in labels]
    fig, ax = plt.subplots(figsize=(8, 4.6))
    bars = ax.barh(range(len(labels)), vals, color=colors, edgecolor="black", linewidth=0.4)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Held-out OS C-index (N_test=182, 38 events)")
    ax.set_xlim(0.5, 0.82)
    ax.axvline(0.5, color="gray", ls=":", lw=0.8)
    for i, v in enumerate(vals):
        ax.text(v + 0.004, i, f"{v:.3f}", va="center", fontsize=8)
    ax.set_title("Experiment 0 — open-GDC OS, same-cohort matched comparison")
    # legend / off-endpoint note
    ax.text(0.5, -1.4, "Orange = mmSYGNAL (relapse/PFS model, OFF-ENDPOINT on OS — "
            "transfer check only, not a same-task ranking).",
            transform=ax.get_yaxis_transform(), fontsize=7.5, color=COLORS["caution"])
    save(fig, "fig4_os_benchmark")


if __name__ == "__main__":
    main()
