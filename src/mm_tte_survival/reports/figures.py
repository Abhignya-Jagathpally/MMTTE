"""Figure generation for reports."""
from __future__ import annotations

from pathlib import Path
import numpy as np


def write_reclassification_km(outdir: Path, quad_df, time_col, event_col):
    """KM of the four clinical × molecular-residual risk quadrants."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from lifelines import KaplanMeierFitter
    except Exception:
        return
    t, e = quad_df[time_col].values, quad_df[event_col].values
    fig, ax = plt.subplots(figsize=(6.5, 5))
    for g in ["clinical_low__molecular_low", "clinical_low__molecular_high",
              "clinical_high__molecular_low", "clinical_high__molecular_high"]:
        m = (quad_df["grp"] == g).values
        if m.sum() >= 5:
            KaplanMeierFitter().fit(t[m], e[m], label=f"{g} (n={int(m.sum())})").plot_survival_function(ax=ax, ci_show=False)
    ax.set_title("OS by clinical × molecular-residual risk")
    ax.set_xlabel("months"); ax.set_ylabel("survival probability")
    (outdir / "figures").mkdir(exist_ok=True)
    fig.tight_layout(); fig.savefig(outdir / "figures" / "mmrf_reclassification_km.png", dpi=130)
    plt.close(fig)
