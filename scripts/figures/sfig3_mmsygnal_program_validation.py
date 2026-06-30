#!/usr/bin/env python
"""Supplement Figure S3 — mmSYGNAL program-activity validation.

A. distribution of {-1,0,1} program activity (ours vs upstream 3-patient example)
B. per-program mean activity
C. mmSYGNAL subtype-model selection counts
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import COLORS, save, plt

ROOT = Path(__file__).resolve().parents[2]
PROG = ROOT / "data" / "real" / "mmsygnal_program_activity_0_140.csv"
EXAMPLE = ROOT / "external" / "mmSYGNAL-risk-prediction-models" / "data" / "patient_program_activity.csv"
SCORES = ROOT / "outputs" / "benchmarks" / "mmSYGNAL" / "mmsygnal_scores.csv"


def main():
    prog = pd.read_csv(PROG)
    pcols = [str(i) for i in range(141)]
    v = prog[pcols].values.astype(float)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # A. {-1,0,1} distribution vs example
    ax = axes[0]
    ours = [np.mean(v == k) for k in (-1, 0, 1)]
    bars = ax.bar([x - 0.18 for x in range(3)], ours, width=0.36, label="ours (N=787)",
                  color=COLORS["omics"], edgecolor="black", lw=0.4)
    if EXAMPLE.exists():
        ex = pd.read_csv(EXAMPLE).values.astype(float)
        exd = [np.mean(ex == k) for k in (-1, 0, 1)]
        ax.bar([x + 0.18 for x in range(3)], exd, width=0.36, label="upstream example (N=3)",
               color=COLORS["caution"], edgecolor="black", lw=0.4)
    ax.set_xticks(range(3)); ax.set_xticklabels(["-1", "0", "+1"])
    ax.set_ylabel("fraction"); ax.set_xlabel("program activity value")
    ax.set_title(f"A. Activity distribution (mean ours={v.mean():.2f})"); ax.legend(fontsize=8)

    # B. per-program mean activity
    ax = axes[1]
    means = v.mean(axis=0)
    ax.bar(range(141), means, color=COLORS["model"])
    ax.set_xlabel("program 0..140"); ax.set_ylabel("mean activity")
    ax.set_title("B. Per-program mean activity")

    # C. subtype model selection counts
    ax = axes[2]
    if SCORES.exists():
        s = pd.read_csv(SCORES)
        n_sub = int((s["mmsygnal_selected_score"] != s["mmsygnal_agnostic_score"]).sum())
        n_agn = int(len(s) - n_sub)
        cls = s["mmsygnal_risk_class"].value_counts().reindex(["low", "high", "extreme"]).fillna(0)
        ax.bar(["agnostic", "subtype"], [n_agn, n_sub], color=[COLORS["clinical"], COLORS["cytogenetics"]],
               edgecolor="black", lw=0.4)
        ax.set_ylabel("patients"); ax.set_title("C. mmSYGNAL model selection")
        ax.text(0.5, 0.92, f"risk class: low {int(cls['low'])}, high {int(cls['high'])}, extreme {int(cls['extreme'])}",
                transform=ax.transAxes, ha="center", fontsize=8)
    fig.suptitle("S3. mmSYGNAL 141-program activity validation (official miner3, method-reproduced)", fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, "sfig3_mmsygnal_program_validation")


if __name__ == "__main__":
    main()
