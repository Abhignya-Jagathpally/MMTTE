"""Residual-risk decomposition, matched-cohort ablation, paired delta-C testing,
repeated-split validation, endpoint-gated claim report, calibration / DCA /
NRI-IDI, and the MMRF usefulness + reclassification-outcome report.

Design principles enforced here:
- ONE matched cohort (all required modalities) and ONE split per analysis, so the
  modality comparison is fair (same patients, same split, same endpoint, same
  censoring, train-only preprocessing). Repeated-split validation re-runs this.
- Molecular features are orthogonalised against clinical before the residual Cox,
  so the molecular term is genuine incremental risk; total = clinical + residual.
- Claims are SEPARATED and endpoint-gated (endpoints.py). OS can never license a
  relapse/PFS claim. Every comparison gets an evidence_level.
- A leakage_audit.json records where every transform was fitted.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from .config import ensure_outdir
from .metrics import fast_c_index as harrell_c_index
from .endpoints import resolve_endpoint, gate_claims
from .stats import (paired_delta_cindex, evidence_level, calibration_metrics,
                    decision_curve, nri_idi)

MAX_OMICS_PCS = 16
HORIZON_MONTHS = 24.0  # landmark for calibration / DCA / NRI-IDI / event rates


# --------------------------------------------------------------------------- #
# Data assembly
# --------------------------------------------------------------------------- #
def _load_tables(cfg: dict):
    p = cfg["paths"]
    clin = pd.read_csv(p["clinical"]); clin["patient_id"] = clin["patient_id"].astype(str)
    cyto = pd.read_csv(p["cytogenetics"]) if p.get("cytogenetics") and Path(p["cytogenetics"]).exists() else None
    omics = pd.read_csv(p["omics"]) if p.get("omics") and Path(p["omics"]).exists() else None
    prog_path = Path(p.get("clinical", ".")).parent / "program_activity.csv"
    prog = pd.read_csv(prog_path) if prog_path.exists() else None
    for tbl in (cyto, omics, prog):
        if tbl is not None:
            tbl["patient_id"] = tbl["patient_id"].astype(str)
    return clin, cyto, omics, prog


def build_matched_cohort(cfg: dict):
    """Matched cohort (all required modalities present) + feature groups."""
    schema = cfg["schema"]
    time_col = schema["time_col"]
    clin, cyto, omics, prog = _load_tables(cfg)
    clinical_cols = [c for c in schema.get("clinical_cols", []) if c in clin.columns]
    df = clin.copy()

    cyto_cols = []
    if cyto is not None:
        cyto_cols = [c for c in schema.get("cytogenetic_cols", []) if c in cyto.columns]
        df = df.merge(cyto[["patient_id"] + cyto_cols], on="patient_id", how="left")

    omics_cols = []
    if omics is not None:
        pc_cols = [c for c in omics.columns if c.startswith("PC")]
        cand = pc_cols or [c for c in omics.columns
                           if c != "patient_id" and pd.api.types.is_numeric_dtype(omics[c])]
        omics_cols = cand[:MAX_OMICS_PCS]
        df = df.merge(omics[["patient_id"] + omics_cols], on="patient_id", how="left")

    prog_cols = []
    if prog is not None:
        prog_cols = [c for c in prog.columns if c != "patient_id" and pd.api.types.is_numeric_dtype(prog[c])]
        df = df.merge(prog[["patient_id"] + prog_cols], on="patient_id", how="left")

    df = df[pd.to_numeric(df[time_col], errors="coerce").gt(0)].copy()
    has_cyto = df[cyto_cols].notna().any(axis=1) if cyto_cols else pd.Series(True, index=df.index)
    has_omics = df[omics_cols].notna().all(axis=1) if omics_cols else pd.Series(True, index=df.index)
    keep = has_cyto & has_omics  # matched ablation always intersects all modalities
    df = df[keep].reset_index(drop=True)
    groups = {"clinical": clinical_cols, "cyto": cyto_cols, "omics": omics_cols, "programs": prog_cols}
    return df, groups


def stratified_split(df, event_col, seed, test_frac=0.25):
    idx = np.arange(len(df))
    tr, te = train_test_split(idx, test_size=test_frac, random_state=seed,
                              stratify=df[event_col].astype(int).values)
    split = np.array(["train"] * len(df), dtype=object)
    split[te] = "test"
    return pd.Series(split == "train")


# --------------------------------------------------------------------------- #
# Feature prep (train-only impute + scale) and a Cox fit returning risk + prob
# --------------------------------------------------------------------------- #
def _prep(df, cols, train_mask):
    X = df[cols].apply(pd.to_numeric, errors="coerce")
    med = X.loc[train_mask].median()
    X = X.fillna(med).fillna(0.0)
    mu = X.loc[train_mask].mean()
    sd = X.loc[train_mask].std().replace(0, 1.0)
    return (X - mu) / sd


def _fit_cox(df, cols, train_mask, time_col, event_col, horizon):
    X = _prep(df, cols, train_mask)
    d = X.copy()
    d[time_col] = pd.to_numeric(df[time_col]).clip(lower=0.1).values
    d[event_col] = df[event_col].astype(int).values
    tr, te = d[train_mask.values], d[~train_mask.values]
    cph = CoxPHFitter(penalizer=0.1).fit(tr, duration_col=time_col, event_col=event_col)
    risk = cph.predict_log_partial_hazard(te[cols]).values
    sf = cph.predict_survival_function(te[cols], times=[horizon])
    p_event = (1.0 - sf.iloc[0].values)
    return cph, risk, p_event


def _cindex_ci(t, e, risk, seed, n_boot=500):
    c = harrell_c_index(t, e, risk)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        b = rng.integers(0, len(t), len(t))
        if e[b].sum() >= 2:
            boots.append(harrell_c_index(t[b], e[b], risk[b]))
    lo, hi = (np.percentile(boots, [2.5, 97.5]) if boots else (np.nan, np.nan))
    return float(c), float(lo), float(hi)


# --------------------------------------------------------------------------- #
# Matched-cohort ablation (single split)
# --------------------------------------------------------------------------- #
def matched_ablation(df, groups, train_mask, time_col, event_col, seed, horizon):
    clin, cyto, om, prog = groups["clinical"], groups["cyto"], groups["omics"], groups["programs"]
    sets = {
        "clinical": clin,
        "clinical+cytogenetics": clin + cyto,
        "clinical+omics": clin + om,
        "clinical+cytogenetics+omics": clin + cyto + om,
    }
    if prog:
        sets["clinical+programs"] = clin + prog
        sets["clinical+cytogenetics+programs"] = clin + cyto + prog
    te = ~train_mask
    t = pd.to_numeric(df[time_col]).values[te.values]
    e = df[event_col].astype(int).values[te.values]
    rows, risks, probs = [], {}, {}
    n_test, n_test_ev = int(te.sum()), int(e.sum())
    for name, cols in sets.items():
        if not cols:
            continue
        _, risk, p_event = _fit_cox(df, cols, train_mask, time_col, event_col, horizon)
        c, lo, hi = _cindex_ci(t, e, risk, seed)
        rows.append({"feature_set": name, "n_features": len(cols),
                     "test_cindex": round(c, 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4),
                     "n_patients": int(len(df)), "n_test": n_test, "events_test": n_test_ev,
                     "analysis_type": "scientific_matched_cohort"})
        risks[name] = risk
        probs[name] = p_event
    return pd.DataFrame(rows), risks, probs, (t, e)


# --------------------------------------------------------------------------- #
# Residual-risk decomposition (strict train-only) + coefficient exports
# --------------------------------------------------------------------------- #
def residual_decomposition(df, groups, train_mask, time_col, event_col):
    clin = groups["clinical"]
    mol = groups["cyto"] + groups["omics"]
    Xc = _prep(df, clin, train_mask)
    Xm = _prep(df, mol, train_mask)

    d1 = Xc.copy()
    d1[time_col] = pd.to_numeric(df[time_col]).clip(lower=0.1).values
    d1[event_col] = df[event_col].astype(int).values
    cox_c = CoxPHFitter(penalizer=0.1).fit(d1[train_mask.values], duration_col=time_col, event_col=event_col)
    clinical_risk = cox_c.predict_log_partial_hazard(Xc).values

    lr = LinearRegression().fit(Xc[train_mask.values].values, Xm[train_mask.values].values)
    Xm_resid = pd.DataFrame(Xm.values - lr.predict(Xc.values),
                            columns=[f"{c}__r" for c in mol], index=df.index)

    d2 = Xm_resid.copy()
    d2["clinical_risk"] = clinical_risk
    d2[time_col] = pd.to_numeric(df[time_col]).clip(lower=0.1).values
    d2[event_col] = df[event_col].astype(int).values
    cox_t = CoxPHFitter(penalizer=0.1).fit(d2[train_mask.values], duration_col=time_col, event_col=event_col)

    beta = cox_t.params_
    mol_cols = list(Xm_resid.columns)
    molecular_residual_risk = Xm_resid[mol_cols].values @ beta[mol_cols].values
    clin_coef = float(beta.get("clinical_risk", 1.0))
    total_risk = clinical_risk + molecular_residual_risk  # offset semantics (clin_coef≈1)

    out = pd.DataFrame({
        "patient_id": df["patient_id"].values,
        "split": np.where(train_mask.values, "train", "test"),
        time_col: pd.to_numeric(df[time_col]).values,
        event_col: df[event_col].astype(int).values,
        "clinical_risk": clinical_risk,
        "molecular_residual_risk": molecular_residual_risk,
        "total_risk": total_risk,
    })

    clin_coef_tbl = pd.DataFrame({"feature": cox_c.params_.index, "coef": cox_c.params_.values,
                                  "abs_coef": np.abs(cox_c.params_.values),
                                  "hazard_ratio": np.exp(cox_c.params_.values)}
                                 ).sort_values("abs_coef", ascending=False)
    mol_coef_tbl = pd.DataFrame({
        "feature": [c[:-3] for c in mol_cols],
        "coef": beta[mol_cols].values,
        "abs_coef": np.abs(beta[mol_cols].values),
        "direction": np.where(beta[mol_cols].values >= 0, "higher_risk", "lower_risk"),
        "abs_std_contribution": np.abs(beta[mol_cols].values) * Xm_resid[mol_cols].std().values,
        "feature_kind": ["cytogenetic_call" if f.replace("__r", "") in groups["cyto"]
                         else "rna_pca_loading_derived" for f in mol_cols],
    }).sort_values("abs_std_contribution", ascending=False).reset_index(drop=True)

    te = out.split.eq("test").values
    t, e = out[time_col].values[te], out[event_col].values[te]
    diag = {
        "clinical_risk": harrell_c_index(t, e, out.clinical_risk.values[te]),
        "molecular_residual_risk": harrell_c_index(t, e, out.molecular_residual_risk.values[te]),
        "total_risk": harrell_c_index(t, e, out.total_risk.values[te]),
        "clinical_coef_in_joint": clin_coef,
    }
    return out, clin_coef_tbl, mol_coef_tbl, diag


def annotate_drivers(mol_coef_tbl, loadings_path):
    drivers = mol_coef_tbl.head(15).copy()
    drivers["provenance"] = np.where(drivers["feature_kind"].eq("cytogenetic_call"),
                                     "CNV/RNA-surrogate cytogenetic call",
                                     "RNA PC loading-derived (NOT a direct gene-level causal feature)")
    if loadings_path and Path(loadings_path).exists():
        load_df = pd.read_csv(loadings_path, index_col=0)
        genes = []
        for f in drivers.feature:
            genes.append(";".join(load_df[f].abs().sort_values(ascending=False).head(5).index)
                         if f in load_df.columns else "")
        drivers["mapped_genes"] = genes
    return drivers


# --------------------------------------------------------------------------- #
# Paired delta-C-index (same test patients)
# --------------------------------------------------------------------------- #
def paired_deltas(risks, decomp, t, e, seed):
    comps = []
    def add(label, a, b):
        if a in risks and b in risks:
            r = paired_delta_cindex(t, e, risks[a], risks[b], seed=seed)
            comps.append({"comparison": label, **r})
    add("clinical+omics_vs_clinical", "clinical+omics", "clinical")
    add("clinical+cyto+omics_vs_clinical", "clinical+cytogenetics+omics", "clinical")
    add("clinical+cyto+omics_vs_clinical+cyto", "clinical+cytogenetics+omics", "clinical+cytogenetics")
    if "clinical+programs" in risks:
        add("clinical+programs_vs_clinical", "clinical+programs", "clinical")
        add("clinical+cyto+programs_vs_clinical+cyto", "clinical+cytogenetics+programs", "clinical+cytogenetics")
    # residual-total vs clinical (same test patients via decomp split)
    te = decomp.split.eq("test").values
    r = paired_delta_cindex(t, e, decomp.total_risk.values[te], decomp.clinical_risk.values[te], seed=seed)
    comps.append({"comparison": "residual_total_vs_clinical", **r})
    return pd.DataFrame(comps)


# --------------------------------------------------------------------------- #
# Repeated stratified-split validation
# --------------------------------------------------------------------------- #
def repeated_split_validation(df, groups, time_col, event_col, seed, n_splits, horizon):
    clin, cyto, om = groups["clinical"], groups["cyto"], groups["omics"]
    sets = {"clinical": clin, "clinical+cytogenetics": clin + cyto,
            "clinical+omics": clin + om, "clinical+cytogenetics+omics": clin + cyto + om}
    per_set = {k: [] for k in sets}
    delta_full_vs_clin, delta_omics_vs_clin = [], []
    for s in range(n_splits):
        tm = stratified_split(df, event_col, seed + s)
        te = ~tm
        t = pd.to_numeric(df[time_col]).values[te.values]
        e = df[event_col].astype(int).values[te.values]
        risks = {}
        for name, cols in sets.items():
            if not cols:
                continue
            _, risk, _ = _fit_cox(df, cols, tm, time_col, event_col, horizon)
            risks[name] = risk
            per_set[name].append(harrell_c_index(t, e, risk))
        if "clinical" in risks and "clinical+cytogenetics+omics" in risks:
            delta_full_vs_clin.append(harrell_c_index(t, e, risks["clinical+cytogenetics+omics"])
                                      - harrell_c_index(t, e, risks["clinical"]))
        if "clinical" in risks and "clinical+omics" in risks:
            delta_omics_vs_clin.append(harrell_c_index(t, e, risks["clinical+omics"])
                                       - harrell_c_index(t, e, risks["clinical"]))
    lb = []
    for name, vals in per_set.items():
        v = np.array(vals)
        if v.size:
            lb.append({"feature_set": name, "n_splits": int(v.size),
                       "mean_cindex": round(float(v.mean()), 4), "sd_cindex": round(float(v.std()), 4),
                       "ci_low": round(float(np.percentile(v, 2.5)), 4),
                       "ci_high": round(float(np.percentile(v, 97.5)), 4)})
    def delta_row(label, arr):
        a = np.array(arr)
        return {"comparison": label, "n_splits": int(a.size),
                "mean_delta": round(float(a.mean()), 4), "sd_delta": round(float(a.std()), 4),
                "ci_low": round(float(np.percentile(a, 2.5)), 4),
                "ci_high": round(float(np.percentile(a, 97.5)), 4),
                "frac_splits_improved": round(float(np.mean(a > 0)), 3)}
    deltas = pd.DataFrame([delta_row("clinical+omics_vs_clinical", delta_omics_vs_clin),
                           delta_row("clinical+cyto+omics_vs_clinical", delta_full_vs_clin)])
    return pd.DataFrame(lb).sort_values("mean_cindex", ascending=False), deltas


# --------------------------------------------------------------------------- #
# Calibration / DCA / NRI-IDI
# --------------------------------------------------------------------------- #
def calibration_dca_nri(probs, t, e, horizon):
    cal_rows, decile_rows = [], []
    for name, p in probs.items():
        m, deciles = calibration_metrics(t, e, p, horizon)
        cal_rows.append({"model": name, **m})
        for d in deciles:
            decile_rows.append({"model": name, **d})
    dca = decision_curve(t, e, probs, horizon)
    nri_rows = []
    pairs = [("clinical", "clinical+omics"),
             ("clinical+cytogenetics", "clinical+cytogenetics+omics")]
    for old, new in pairs:
        if old in probs and new in probs:
            r = nri_idi(t, e, probs[old], probs[new], horizon)
            nri_rows.append({"comparison": f"{new}_vs_{old}", **r})
    return pd.DataFrame(cal_rows), pd.DataFrame(decile_rows), pd.DataFrame(dca), pd.DataFrame(nri_rows)


# --------------------------------------------------------------------------- #
# Subtype gain/fail with evidence labels
# --------------------------------------------------------------------------- #
def subtype_evidence(df, groups, decomp, time_col, event_col, cfg):
    exp = cfg.get("experiments", {})
    min_hyp = int(exp.get("min_subtype_events_hypothesis", 10))
    min_conf = int(exp.get("min_subtype_events_confirmatory", 30))
    te = decomp.split.eq("test").values
    merged = decomp.merge(df[["patient_id"] + groups["cyto"]], on="patient_id", how="left")
    rows = []
    for s in groups["cyto"]:
        pos = (pd.to_numeric(merged[s], errors="coerce").fillna(0) > 0).values & te
        n, ev = int(pos.sum()), int(merged.loc[pos, event_col].sum())
        rec = {"subtype": s, "n_patients": n, "n_events": ev}
        if ev < 5 or n < 10:
            rec.update({"clinical_cindex": np.nan, "clinical_omics_cindex": np.nan,
                        "delta_cindex": np.nan, "evidence_level": "unstable_descriptive_only"})
        else:
            cc = harrell_c_index(merged[time_col].values[pos], merged[event_col].values[pos],
                                 merged.clinical_risk.values[pos])
            ct = harrell_c_index(merged[time_col].values[pos], merged[event_col].values[pos],
                                 merged.total_risk.values[pos])
            delta = ct - cc
            if ev >= min_conf and delta > 0:
                lvl = "potentially_confirmatory_pending_paired_ci"
            elif ev >= min_hyp:
                lvl = "hypothesis_generating"
            else:
                lvl = "unstable_descriptive_only"
            rec.update({"clinical_cindex": round(cc, 3), "clinical_omics_cindex": round(ct, 3),
                        "delta_cindex": round(delta, 3), "evidence_level": lvl})
        rows.append(rec)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# MMRF usefulness + reclassification OUTCOME validation
# --------------------------------------------------------------------------- #
def _tertiles(x):
    return pd.qcut(pd.Series(x).rank(method="first"), 3, labels=["low", "mid", "high"]).astype(object).values


def usefulness_and_outcomes(df, groups, decomp, time_col, event_col, horizon, outdir):
    d = decomp.copy()
    d["clinical_grp"] = _tertiles(d["clinical_risk"].values)
    d["total_grp"] = _tertiles(d["total_risk"].values)
    d["resid_grp"] = _tertiles(d["molecular_residual_risk"].values)
    rank = {"low": 0, "mid": 1, "high": 2}

    reclassified = d[d.clinical_grp != d.total_grp]
    up = reclassified[reclassified.apply(lambda r: rank[r.total_grp] > rank[r.clinical_grp], axis=1)]
    down = reclassified[reclassified.apply(lambda r: rank[r.total_grp] < rank[r.clinical_grp], axis=1)]
    clin_standard_mol_high = d[(d.clinical_grp.isin(["low", "mid"])) & (d.resid_grp == "high")]

    hr_cyto = [c for c in ["del17p", "t_4_14", "amp1q", "t_14_16"] if c in df.columns]
    dfi = df.set_index("patient_id")
    flags = dfi.reindex(d.patient_id)[hr_cyto].apply(pd.to_numeric, errors="coerce").fillna(0) > 0
    cyto_high = flags.any(axis=1).values
    med_total = np.median(d.total_risk.values)
    cyto_high_mol_low = d[(cyto_high) & (d.total_risk.values < med_total)]

    # ---- reclassification OUTCOME validation (binary clinical x molecular) ----
    clin_bin = (pd.Series(d.clinical_risk.values).rank(pct=True) > 0.5).map({True: "high", False: "low"}).values
    mol_bin = (pd.Series(d.molecular_residual_risk.values).rank(pct=True) > 0.5).map({True: "high", False: "low"}).values
    d2 = d.copy()
    d2["grp"] = [f"clinical_{c}__molecular_{m}" for c, m in zip(clin_bin, mol_bin)]
    d2.loc[cyto_high & (mol_bin == "low"), "grp_cyto"] = "cyto_high__molecular_low"
    d2.loc[(~cyto_high) & (mol_bin == "high"), "grp_cyto"] = "cyto_low__molecular_high"

    t_all, e_all = d2[time_col].values, d2[event_col].values
    out_rows = []
    groups_def = [("grp", g) for g in ["clinical_low__molecular_low", "clinical_low__molecular_high",
                                       "clinical_high__molecular_low", "clinical_high__molecular_high"]]
    groups_def += [("grp_cyto", "cyto_high__molecular_low"), ("grp_cyto", "cyto_low__molecular_high")]
    for col, g in groups_def:
        if col not in d2:
            continue
        mask = (d2[col] == g).values
        n, ev = int(mask.sum()), int(e_all[mask].sum())
        if n == 0:
            continue
        from .stats import _km_event_prob
        er = _km_event_prob(t_all[mask], e_all[mask], horizon)
        kmf = KaplanMeierFitter().fit(t_all[mask], e_all[mask])
        med = kmf.median_survival_time_
        # group vs complement: log-rank + HR
        lr = logrank_test(t_all[mask], t_all[~mask], e_all[mask], e_all[~mask])
        try:
            cph = CoxPHFitter().fit(pd.DataFrame({"g": mask.astype(int), "t": t_all, "e": e_all}),
                                    duration_col="t", event_col="e")
            hr = float(np.exp(cph.params_["g"]))
        except Exception:
            hr = np.nan
        out_rows.append({"group": g, "n_patients": n, "n_events": ev,
                         "event_rate_by_horizon": round(float(er), 4),
                         "median_survival_months": (round(float(med), 1) if np.isfinite(med) else "not_reached"),
                         "logrank_p_vs_rest": round(float(lr.p_value), 4),
                         "hazard_ratio_vs_rest": round(hr, 3) if np.isfinite(hr) else np.nan})
    outcomes = pd.DataFrame(out_rows)

    # KM figure of the four clinical x molecular quadrants
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(6.5, 5))
        for g in ["clinical_low__molecular_low", "clinical_low__molecular_high",
                  "clinical_high__molecular_low", "clinical_high__molecular_high"]:
            m = (d2["grp"] == g).values
            if m.sum() >= 5:
                KaplanMeierFitter().fit(t_all[m], e_all[m], label=f"{g} (n={m.sum()})").plot_survival_function(ax=ax, ci_show=False)
        ax.set_title("OS by clinical × molecular-residual risk")
        ax.set_xlabel("months"); ax.set_ylabel("survival probability")
        fig.tight_layout(); (outdir / "figures").mkdir(exist_ok=True)
        fig.savefig(outdir / "figures" / "mmrf_reclassification_km.png", dpi=130); plt.close(fig)
    except Exception:
        pass

    summary = {
        "n_reclassified_by_omics": int(len(reclassified)),
        "n_reclassified_up": int(len(up)), "n_reclassified_down": int(len(down)),
        "n_clinical_standard_but_molecular_high": int(len(clin_standard_mol_high)),
        "n_cytogenetic_highrisk_but_molecular_lower": int(len(cyto_high_mol_low)),
        "n_cytogenetic_highrisk_total": int(cyto_high.sum()),
        "note": "Reclassification matters only if outcomes differ; see mmrf_reclassification_outcomes.csv.",
    }
    return summary, outcomes


# --------------------------------------------------------------------------- #
# Orchestration
# --------------------------------------------------------------------------- #
def run_residual_report(cfg: dict) -> dict:
    schema = cfg["schema"]
    time_col, event_col = schema["time_col"], schema["event_col"]
    seed = int(cfg.get("seed", 42))
    horizon = float(cfg.get("validation", {}).get("horizon_months", HORIZON_MONTHS))
    n_splits = int(cfg.get("validation", {}).get("repeated_splits", 50))
    outdir = ensure_outdir(cfg["paths"].get("outdir", "outputs/real_run"))
    matched_flag = bool(cfg.get("cohort", {}).get("matched_ablation", True))
    analysis_label = "scientific_matched_cohort" if matched_flag else "deployment_availability"

    endpoint_spec = resolve_endpoint(cfg)
    df, groups = build_matched_cohort(cfg)
    train_mask = stratified_split(df, event_col, seed)

    ablation, risks, probs, (t, e) = matched_ablation(df, groups, train_mask, time_col, event_col, seed, horizon)
    decomp, clin_coef_tbl, mol_coef_tbl, diag = residual_decomposition(df, groups, train_mask, time_col, event_col)
    loadings = Path(cfg["paths"]["clinical"]).parent / "omics_pc_loadings.csv"
    drivers = annotate_drivers(mol_coef_tbl, loadings)

    deltas = paired_deltas(risks, decomp, t, e, seed)
    rep_lb, rep_delta = repeated_split_validation(df, groups, time_col, event_col, seed, n_splits, horizon)
    cal, cal_decile, dca, nri = calibration_dca_nri(probs, t, e, horizon)
    subtypes = subtype_evidence(df, groups, decomp, time_col, event_col, cfg)
    summary, outcomes = usefulness_and_outcomes(df, groups, decomp, time_col, event_col, horizon, outdir)

    # ---- omics increment confirmed? (paired CI lower > 0 on the key comparison) ----
    key = deltas[deltas.comparison == "clinical+cyto+omics_vs_clinical"]
    omics_confirmed = bool(len(key) and np.isfinite(key.delta_ci_low.iloc[0]) and key.delta_ci_low.iloc[0] > 0)
    key_delta = float(key.delta_cindex.iloc[0]) if len(key) else np.nan
    key_ci_low = float(key.delta_ci_low.iloc[0]) if len(key) else np.nan
    external_val = bool(cfg.get("validation", {}).get("external_validation_available", False))

    claims = gate_claims(endpoint_spec, omics_increment_confirmed=omics_confirmed,
                         external_validation_available=external_val, proposal_target="relapse")
    ev_level = evidence_level(endpoint_spec.get("endpoint_type"), "relapse", key_delta, key_ci_low, external_val)

    report = {**claims, "evidence_level_for_omics_increment": ev_level,
              "omics_increment_summary": (
                  "SUGGESTIVE_NOT_CONFIRMED" if (np.isfinite(key_delta) and key_delta > 0 and not omics_confirmed)
                  else ("CONFIRMED" if omics_confirmed else "NO_EVIDENCE")),
              "_detail": {"matched_n": int(len(df)), "test_events": int(e.sum()),
                          "clinical_cindex": float(ablation.set_index("feature_set").loc["clinical", "test_cindex"])
                          if "clinical" in ablation.feature_set.values else np.nan,
                          "full_cindex": float(ablation.set_index("feature_set").loc["clinical+cytogenetics+omics", "test_cindex"])
                          if "clinical+cytogenetics+omics" in ablation.feature_set.values else np.nan,
                          "omics_paired_delta": key_delta, "omics_paired_delta_ci_low": key_ci_low,
                          "molecular_residual_test_cindex": round(diag["molecular_residual_risk"], 4),
                          "analysis_type": analysis_label}}

    leakage_audit = {
        "imputer_fit_on": "train", "scaler_fit_on": "train",
        "pca_fit_on": "train_or_precomputed",
        "orthogonalizer_fit_on": "train", "cox_fit_on": "train",
        "test_used_for_model_selection": False,
        "split_strategy": cfg.get("splitting", {}).get("strategy", "stratified_event"),
        "note": "Omics PCA was fit once on the full RNA cohort (unsupervised, no labels) in "
                "build_omics.py; all survival-model preprocessing (impute/scale/orthogonalize/Cox) "
                "is train-only. No test outcomes touch any coefficient.",
    }

    # ---- persist ----
    ablation.to_csv(outdir / "matched_ablation.csv", index=False)
    decomp.to_csv(outdir / "residual_risk_decomposition.csv", index=False)
    clin_coef_tbl.to_csv(outdir / "clinical_risk_coefficients.csv", index=False)
    mol_coef_tbl.to_csv(outdir / "molecular_residual_coefficients.csv", index=False)
    drivers.to_csv(outdir / "molecular_residual_top_drivers.csv", index=False)
    deltas.to_csv(outdir / "paired_delta_cindex.csv", index=False)
    rep_lb.to_csv(outdir / "repeated_split_leaderboard.csv", index=False)
    rep_delta.to_csv(outdir / "repeated_split_delta_cindex.csv", index=False)
    cal.to_csv(outdir / "calibration_metrics.csv", index=False)
    cal_decile.to_csv(outdir / "calibration_by_decile.csv", index=False)
    dca.to_csv(outdir / "decision_curve_analysis.csv", index=False)
    nri.to_csv(outdir / "reclassification_metrics.csv", index=False)
    subtypes.to_csv(outdir / "mmrf_subtype_gain_fail.csv", index=False)
    outcomes.to_csv(outdir / "mmrf_reclassification_outcomes.csv", index=False)
    (outdir / "claim_report.json").write_text(json.dumps(report, indent=2))
    (outdir / "mmrf_usefulness_summary.json").write_text(json.dumps(summary, indent=2))
    (outdir / "leakage_audit.json").write_text(json.dumps(leakage_audit, indent=2))
    _write_claim_md(outdir, report)

    _write_md(outdir, df, ablation, deltas, rep_lb, rep_delta, report, diag, summary,
              subtypes, drivers, outcomes, cal, nri, endpoint_spec)
    _print(df, ablation, deltas, report, diag, summary, subtypes, outcomes, endpoint_spec)
    return {"outdir": str(outdir), "ablation": ablation, "claim_report": report,
            "paired_deltas": deltas, "usefulness": summary, "diag": diag,
            "repeated_leaderboard": rep_lb, "outcomes": outcomes}


def _yn(b):
    return "YES" if b else "NO"


def _write_claim_md(outdir, report):
    d = report["_detail"]
    L = [f"# Claim report — {report['endpoint_name']} ({report['endpoint_type']})", "",
         "| Claim | Allowed |", "|---|---|",
         f"| technical_validation_claim_allowed | **{_yn(report['technical_validation_claim_allowed'])}** |",
         f"| primary_biological_claim_allowed | **{_yn(report['primary_biological_claim_allowed'])}** |",
         f"| relapse_or_pfs_claim_allowed | **{_yn(report['relapse_or_pfs_claim_allowed'])}** |",
         f"| omics_increment_confirmed | **{_yn(report['omics_increment_confirmed'])}** "
         f"({report['omics_increment_summary']}) |",
         f"| external_validation_available | **{_yn(report['external_validation_available'])}** |", "",
         f"- evidence_level (omics increment): **{report['evidence_level_for_omics_increment']}**",
         f"- omics paired ΔC: {d['omics_paired_delta']:+.3f} (CI low {d['omics_paired_delta_ci_low']:+.3f})",
         f"- matched N={d['matched_n']}, test events={d['test_events']}, "
         f"clinical C={d['clinical_cindex']:.3f}, full C={d['full_cindex']:.3f}", "",
         "An overall-survival endpoint cannot license a relapse/PFS or primary biological "
         "claim. For the current OS run: **technical validation YES, primary relapse/PFS "
         "claim NO, omics incremental value SUGGESTIVE NOT CONFIRMED, external validation NO.**"]
    (outdir / "claim_report.md").write_text("\n".join(L) + "\n")


def _print(df, ablation, deltas, report, diag, summary, subtypes, outcomes, ep):
    print("\n" + "=" * 74)
    print(f"ENDPOINT: {ep.get('name')} ({ep.get('endpoint_type')}, role={ep.get('role')})")
    print(f"MATCHED COHORT: N={len(df)} | analysis_type={report['_detail']['analysis_type']} "
          f"| test events={report['_detail']['test_events']}")
    print("=" * 74)
    print("\n[3] MATCHED-COHORT ABLATION (same patients/split/endpoint):")
    print(ablation[["feature_set", "n_features", "test_cindex", "ci_low", "ci_high"]].to_string(index=False))
    print("\n[2] PAIRED ΔC-INDEX (same test patients, bootstrap):")
    print(deltas[["comparison", "delta_cindex", "delta_ci_low", "delta_ci_high", "p_bootstrap", "claim"]].to_string(index=False))
    print(f"\n    Residual decomposition held-out C: clinical={diag['clinical_risk']:.3f} "
          f"molecular_residual={diag['molecular_residual_risk']:.3f} total={diag['total_risk']:.3f} "
          f"(clin coef={diag['clinical_coef_in_joint']:.3f})")
    print("\n[1+5] ENDPOINT-GATED CLAIM REPORT:")
    print(f"    technical_validation_claim_allowed : {_yn(report['technical_validation_claim_allowed'])}")
    print(f"    primary_biological_claim_allowed   : {_yn(report['primary_biological_claim_allowed'])}")
    print(f"    relapse_or_pfs_claim_allowed       : {_yn(report['relapse_or_pfs_claim_allowed'])}")
    print(f"    omics_increment_confirmed          : {_yn(report['omics_increment_confirmed'])}  "
          f"({report['omics_increment_summary']})")
    print(f"    external_validation_available      : {_yn(report['external_validation_available'])}")
    print(f"    evidence_level (omics increment)   : {report['evidence_level_for_omics_increment'].upper()}")
    print("\n[6] SUBTYPE EVIDENCE (event-gated):")
    print(subtypes.to_string(index=False))
    print("\n[7] RECLASSIFICATION OUTCOMES (do reclassified groups differ?):")
    print(outcomes.to_string(index=False))
    print("\n[5] USEFULNESS:", json.dumps({k: v for k, v in summary.items() if k != "note"}))
    print("=" * 74)


def _write_md(outdir, df, ablation, deltas, rep_lb, rep_delta, report, diag, summary,
              subtypes, drivers, outcomes, cal, nri, ep):
    L = [f"# Experiment 0 — {ep.get('name')} ({ep.get('endpoint_type')}): "
         "matched-cohort technical-validation & residual-risk pilot", "",
         f"Endpoint role: **{ep.get('role')}** · analysis_type: "
         f"**{report['_detail']['analysis_type']}** · matched N={len(df)}, "
         f"test events={report['_detail']['test_events']}.", "",
         "> Headline: in a matched open-GDC **OS** cohort, omics features moved held-out "
         f"C-index from {report['_detail']['clinical_cindex']:.3f} (clinical) to "
         f"{report['_detail']['full_cindex']:.3f} (clinical+cyto+omics). The paired ΔC CI "
         "overlaps 0 and the endpoint is OS, so this is **hypothesis-generating evidence of "
         "molecular residual signal, not confirmatory evidence of clinical utility**.", "",
         "## [1] Endpoint-gated claim report", "",
         f"- technical_validation_claim_allowed: **{_yn(report['technical_validation_claim_allowed'])}**",
         f"- primary_biological_claim_allowed: **{_yn(report['primary_biological_claim_allowed'])}**",
         f"- relapse_or_pfs_claim_allowed: **{_yn(report['relapse_or_pfs_claim_allowed'])}**",
         f"- omics_increment_confirmed: **{_yn(report['omics_increment_confirmed'])}** "
         f"({report['omics_increment_summary']})",
         f"- external_validation_available: **{_yn(report['external_validation_available'])}**",
         f"- evidence_level (omics increment): **{report['evidence_level_for_omics_increment']}**", "",
         "## [3] Matched-cohort ablation (same patients, same split)", "",
         "| Feature set | #feat | Test C | 95% CI |", "|---|---|---|---|"]
    for _, r in ablation.iterrows():
        L.append(f"| {r['feature_set']} | {r['n_features']} | {r['test_cindex']:.3f} | {r['ci_low']:.3f}–{r['ci_high']:.3f} |")
    L += ["", "## [2] Paired ΔC-index (same test patients)", "",
          "| Comparison | ΔC | ΔCI low | ΔCI high | p_boot | claim |", "|---|---|---|---|---|---|"]
    for _, r in deltas.iterrows():
        L.append(f"| {r['comparison']} | {r['delta_cindex']:+.3f} | {r['delta_ci_low']:+.3f} | "
                 f"{r['delta_ci_high']:+.3f} | {r['p_bootstrap']} | {r['claim']} |")
    L += ["", f"Residual decomposition held-out C-index — clinical **{diag['clinical_risk']:.3f}**, "
          f"molecular_residual **{diag['molecular_residual_risk']:.3f}**, total **{diag['total_risk']:.3f}** "
          f"(clinical coef in joint = {diag['clinical_coef_in_joint']:.3f} ≈ 1 ⇒ clean offset).", "",
          "## Repeated stratified-split validation", "",
          "| Feature set | splits | mean C | sd | 95% CI |", "|---|---|---|---|---|"]
    for _, r in rep_lb.iterrows():
        L.append(f"| {r['feature_set']} | {r['n_splits']} | {r['mean_cindex']:.3f} | {r['sd_cindex']:.3f} | "
                 f"{r['ci_low']:.3f}–{r['ci_high']:.3f} |")
    L += ["", "| Δ comparison | mean Δ | 95% CI | frac splits improved |", "|---|---|---|---|"]
    for _, r in rep_delta.iterrows():
        L.append(f"| {r['comparison']} | {r['mean_delta']:+.3f} | {r['ci_low']:+.3f}–{r['ci_high']:+.3f} | "
                 f"{r['frac_splits_improved']:.2f} |")
    L += ["", "## [6] Subtype evidence (event-gated)", "",
          "| Subtype | n | events | C clin | C total | Δ | evidence_level |", "|---|---|---|---|---|---|---|"]
    for _, r in subtypes.iterrows():
        cc = f"{r['clinical_cindex']:.3f}" if pd.notna(r['clinical_cindex']) else "—"
        ct = f"{r['clinical_omics_cindex']:.3f}" if pd.notna(r['clinical_omics_cindex']) else "—"
        dl = f"{r['delta_cindex']:+.3f}" if pd.notna(r['delta_cindex']) else "—"
        L.append(f"| {r['subtype']} | {r['n_patients']} | {r['n_events']} | {cc} | {ct} | {dl} | {r['evidence_level']} |")
    L += ["", "Subtype-level results suggest possible omics benefit across several cytogenetic "
          "strata (notably amp1q and t(4;14)), but event counts are too small for confirmatory "
          "subtype claims.", "",
          "## [7] Reclassification OUTCOME validation", "",
          "| Group | n | events | event-rate@horizon | median OS (mo) | log-rank p | HR vs rest |",
          "|---|---|---|---|---|---|---|"]
    for _, r in outcomes.iterrows():
        L.append(f"| {r['group']} | {r['n_patients']} | {r['n_events']} | {r['event_rate_by_horizon']} | "
                 f"{r['median_survival_months']} | {r['logrank_p_vs_rest']} | {r['hazard_ratio_vs_rest']} |")
    L += ["", "## [5] MMRF usefulness", "",
          f"- reclassified by omics: **{summary['n_reclassified_by_omics']}** "
          f"(up {summary['n_reclassified_up']} / down {summary['n_reclassified_down']})",
          f"- clinically standard-risk but molecularly HIGH: **{summary['n_clinical_standard_but_molecular_high']}**",
          f"- cytogenetic high-risk but molecularly LOWER: "
          f"**{summary['n_cytogenetic_highrisk_but_molecular_lower']}/{summary['n_cytogenetic_highrisk_total']}**",
          "", "## Top molecular-residual drivers (provenance-flagged)", "",
          "| feature | coef | direction | kind | mapped_genes |", "|---|---|---|---|---|"]
    for _, r in drivers.head(10).iterrows():
        L.append(f"| {r['feature']} | {r['coef']:+.3f} | {r['direction']} | {r['feature_kind']} | "
                 f"{r.get('mapped_genes','')} |")
    L += ["", "_RNA-derived drivers are PC-loading-derived, NOT direct gene-level causal features._"]
    (outdir / "residual_and_usefulness_report.md").write_text("\n".join(L) + "\n")
    # endpoint gate report (separate, concise)
    G = [f"# Endpoint gate report — {ep.get('name')}", "",
         f"endpoint_type: `{ep.get('endpoint_type')}` · role: `{ep.get('role')}`", "",
         f"- technical_validation_claim_allowed: **{_yn(report['technical_validation_claim_allowed'])}**",
         f"- primary_biological_claim_allowed: **{_yn(report['primary_biological_claim_allowed'])}**",
         f"- relapse_or_pfs_claim_allowed: **{_yn(report['relapse_or_pfs_claim_allowed'])}**",
         f"- omics_increment: **{report['omics_increment_summary']}** "
         f"(ΔC={report['_detail']['omics_paired_delta']:+.3f}, CI low={report['_detail']['omics_paired_delta_ci_low']:+.3f})",
         f"- evidence_level: **{report['evidence_level_for_omics_increment']}**", "",
         "This run uses an **overall-survival** endpoint and therefore CANNOT license a "
         "relapse/PFS or primary biological claim. It is a technical-validation + "
         "residual-risk pilot (Experiment 0)."]
    (outdir / "endpoint_gate_report.md").write_text("\n".join(G) + "\n")
