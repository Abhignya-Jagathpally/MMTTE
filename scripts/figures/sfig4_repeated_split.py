#!/usr/bin/env python
"""Supplement Figure S4 — repeated-split stability (distributions, not point bars).

A. box+strip of OS C-index across 50 stratified splits per feature set
B. paired ΔC distribution vs clinical with the zero line emphasised
Emphasises: stable positive direction but ΔC CI crosses 0 (NOT confirmatory).
Recomputes per-split values directly (the leaderboard CSV only stores summaries).
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _style import color_for, COLORS, save, plt
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from mm_tte_survival.metrics import fast_c_index as cidx
from mm_tte_survival.data.cohort import build_matched_cohort
from mm_tte_survival.data.splits import stratified_event_split
from mm_tte_survival.evaluation.evaluate import _fit_cox

CFG = {"paths": {"clinical": str(ROOT / "data/real/clinical_survival.csv"),
                 "cytogenetics": str(ROOT / "data/real/cytogenetics.csv"),
                 "omics": str(ROOT / "data/real/omics.csv")},
       "schema": {"id_col": "patient_id", "time_col": "time_months", "event_col": "event",
                  "clinical_cols": ["age", "sex_M", "iss_2", "iss_3", "line_of_therapy", "albumin", "b2m"],
                  "cytogenetic_cols": ["amp1q", "del1p", "del13q", "del17p", "t_4_14", "t_11_14", "t_14_16", "hyperdiploid"]}}
N_SPLITS, SEED, HORIZON = 50, 42, 24.0


def main():
    df, g = build_matched_cohort(CFG)
    tc, ec = "time_months", "event"
    sets = {"clinical": g["clinical"], "clinical+cyto": g["clinical"] + g["cyto"],
            "clinical+omics": g["clinical"] + g["omics"],
            "clinical+cyto+omics": g["clinical"] + g["cyto"] + g["omics"]}
    per = {k: [] for k in sets}
    d_om, d_full = [], []
    for s in range(N_SPLITS):
        tm = stratified_event_split(df, ec, SEED + s)
        te = ~tm
        t = pd.to_numeric(df[tc]).values[te.values]; e = df[ec].astype(int).values[te.values]
        r = {}
        for name, cols in sets.items():
            risk, _ = _fit_cox(df, cols, tm, tc, ec, HORIZON)
            r[name] = cidx(t, e, risk); per[name].append(r[name])
        d_om.append(r["clinical+omics"] - r["clinical"])
        d_full.append(r["clinical+cyto+omics"] - r["clinical"])

    order = sorted(sets, key=lambda k: np.mean(per[k]))
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))

    ax = axes[0]
    data = [per[k] for k in order]
    bp = ax.boxplot(data, vert=False, patch_artist=True, widths=0.6, showfliers=False)
    for patch, k in zip(bp["boxes"], order):
        patch.set_facecolor(color_for(k)); patch.set_alpha(0.6)
    for i, k in enumerate(order, 1):
        ax.scatter(per[k], np.random.default_rng(0).normal(i, 0.05, len(per[k])), s=6, color="black", alpha=0.4)
    ax.set_yticklabels(order, fontsize=9); ax.set_xlabel("OS C-index across 50 splits")
    ax.set_title("A. Per-split C-index distribution")

    ax = axes[1]
    parts = ax.violinplot([d_om, d_full], vert=False, showmeans=True, showextrema=True)
    for pc in parts["bodies"]:
        pc.set_facecolor(COLORS["omics"]); pc.set_alpha(0.5)
    ax.axvline(0, color=COLORS["blocked"], ls="--", lw=1.2, label="no improvement")
    ax.set_yticks([1, 2]); ax.set_yticklabels(["+omics vs clinical", "+cyto+omics vs clinical"], fontsize=9)
    ax.set_xlabel("paired ΔC-index")
    f_om, f_full = np.mean(np.array(d_om) > 0), np.mean(np.array(d_full) > 0)
    ax.set_title("B. Paired ΔC distribution")
    ax.text(0.5, -0.22, f"improved in {f_om*100:.0f}% / {f_full*100:.0f}% of splits — "
            "stable positive direction, but ΔC CI crosses 0 (NOT confirmatory).",
            transform=ax.transAxes, ha="center", fontsize=8, color=COLORS["caution"])
    ax.legend(fontsize=8, loc="upper right")
    fig.suptitle("S4. Repeated stratified-split stability (open-GDC OS)", fontsize=11)
    fig.tight_layout(rect=[0, 0.03, 1, 0.96])
    save(fig, "sfig4_repeated_split")


if __name__ == "__main__":
    main()
