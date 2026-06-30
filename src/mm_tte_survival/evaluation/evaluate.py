"""evaluate_model_suite — the full endpoint-correct evaluation on the matched cohort.

Produces (returned in a results dict; persisted by reports.run_reports):
matched ablation, paired ΔC-index, residual-risk decomposition, repeated-split
validation, calibration / DCA / NRI-IDI, subtype evidence labels, reclassification
outcomes, MMRF usefulness, leakage audit, and the endpoint-gated claim report.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
from sklearn.linear_model import LinearRegression

from ..metrics import fast_c_index as cidx
from ..endpoints import resolve_endpoint
from ..models.residual_risk import ResidualRiskModel
from ..data.cohort import build_matched_cohort
from ..data.splits import stratified_event_split
from .stats import (paired_delta_cindex, calibration_metrics, decision_curve,
                    nri_idi, _km_event_prob)
from .claim_gate import build_claim_report

HORIZON_MONTHS = 24.0


def _prep(df, cols, train_mask):
    X = df[cols].apply(pd.to_numeric, errors="coerce")
    X = X.fillna(X.loc[train_mask].median()).fillna(0.0)
    mu, sd = X.loc[train_mask].mean(), X.loc[train_mask].std().replace(0, 1.0)
    return (X - mu) / sd


def _fit_cox(df, cols, train_mask, time_col, event_col, horizon):
    X = _prep(df, cols, train_mask)
    d = X.copy()
    d[time_col] = pd.to_numeric(df[time_col]).clip(lower=0.1).values
    d[event_col] = df[event_col].astype(int).values
    cph = CoxPHFitter(penalizer=0.1).fit(d[train_mask.values], duration_col=time_col, event_col=event_col)
    te = d[~train_mask.values]
    risk = cph.predict_log_partial_hazard(te[cols]).values
    p_event = 1.0 - cph.predict_survival_function(te[cols], times=[horizon]).iloc[0].values
    return risk, p_event


def _cindex_ci(t, e, risk, seed, n_boot=500):
    c = cidx(t, e, risk)
    rng = np.random.default_rng(seed)
    boots = [cidx(t[b], e[b], risk[b]) for b in (rng.integers(0, len(t), len(t)) for _ in range(n_boot))]
    boots = [x for x in boots if np.isfinite(x)]
    lo, hi = (np.percentile(boots, [2.5, 97.5]) if boots else (np.nan, np.nan))
    return float(c), float(lo), float(hi)


def _ablation(df, groups, tm, time_col, event_col, seed, horizon):
    clin, cyto, om, prog = groups["clinical"], groups["cyto"], groups["omics"], groups["programs"]
    sets = {"clinical": clin, "clinical+cytogenetics": clin + cyto,
            "clinical+omics": clin + om, "clinical+cytogenetics+omics": clin + cyto + om}
    if prog:
        sets["clinical+programs"] = clin + prog
        sets["clinical+cytogenetics+programs"] = clin + cyto + prog
    te = ~tm
    t = pd.to_numeric(df[time_col]).values[te.values]
    e = df[event_col].astype(int).values[te.values]
    rows, risks, probs = [], {}, {}
    for name, cols in sets.items():
        if not cols:
            continue
        risk, p = _fit_cox(df, cols, tm, time_col, event_col, horizon)
        c, lo, hi = _cindex_ci(t, e, risk, seed)
        rows.append({"feature_set": name, "n_features": len(cols), "test_cindex": round(c, 4),
                     "ci_low": round(lo, 4), "ci_high": round(hi, 4), "n_patients": int(len(df)),
                     "n_test": int(te.sum()), "events_test": int(e.sum()),
                     "analysis_type": "scientific_matched_cohort"})
        risks[name], probs[name] = risk, p
    return pd.DataFrame(rows), risks, probs, (t, e)


def _decomposition(df, groups, tm, time_col, event_col):
    model = ResidualRiskModel(groups["clinical"], groups["cyto"] + groups["omics"],
                              time_col=time_col, event_col=event_col).fit(df[tm.values])
    pred = model.predict(df)
    out = pd.DataFrame({
        "patient_id": df["patient_id"].values,
        "split": np.where(tm.values, "train", "test"),
        time_col: pd.to_numeric(df[time_col]).values, event_col: df[event_col].astype(int).values,
        "clinical_risk": pred.clinical_risk.values,
        "molecular_residual_risk": pred.molecular_residual_risk.values,
        "total_risk": pred.total_risk.values})
    clin_tbl, mol_tbl = model.coefficients()
    mol_tbl["feature_kind"] = ["cytogenetic_call" if f in groups["cyto"] else "rna_pca_loading_derived"
                              for f in mol_tbl.feature]
    te = out.split.eq("test").values
    t, e = out[time_col].values[te], out[event_col].values[te]
    diag = {"clinical_risk": cidx(t, e, out.clinical_risk.values[te]),
            "molecular_residual_risk": cidx(t, e, out.molecular_residual_risk.values[te]),
            "total_risk": cidx(t, e, out.total_risk.values[te]),
            "clinical_coef_in_joint": model.clinical_coef_in_joint}
    return out, clin_tbl, mol_tbl, diag


def _paired(risks, decomp, t, e, seed):
    comps = []
    def add(label, a, b):
        if a in risks and b in risks:
            comps.append({"comparison": label, **paired_delta_cindex(t, e, risks[a], risks[b], seed=seed)})
    add("clinical+omics_vs_clinical", "clinical+omics", "clinical")
    add("clinical+cyto+omics_vs_clinical", "clinical+cytogenetics+omics", "clinical")
    add("clinical+cyto+omics_vs_clinical+cyto", "clinical+cytogenetics+omics", "clinical+cytogenetics")
    if "clinical+programs" in risks:
        add("clinical+programs_vs_clinical", "clinical+programs", "clinical")
        add("clinical+cyto+programs_vs_clinical+cyto", "clinical+cytogenetics+programs", "clinical+cytogenetics")
    te = decomp.split.eq("test").values
    comps.append({"comparison": "residual_total_vs_clinical",
                  **paired_delta_cindex(t, e, decomp.total_risk.values[te], decomp.clinical_risk.values[te], seed=seed)})
    return pd.DataFrame(comps)


def _repeated(df, groups, time_col, event_col, seed, n_splits, horizon):
    clin, cyto, om = groups["clinical"], groups["cyto"], groups["omics"]
    sets = {"clinical": clin, "clinical+cytogenetics": clin + cyto,
            "clinical+omics": clin + om, "clinical+cytogenetics+omics": clin + cyto + om}
    per = {k: [] for k in sets}
    d_full, d_om = [], []
    for s in range(n_splits):
        tm = stratified_event_split(df, event_col, seed + s)
        te = ~tm
        t = pd.to_numeric(df[time_col]).values[te.values]
        e = df[event_col].astype(int).values[te.values]
        r = {}
        for name, cols in sets.items():
            if not cols:
                continue
            risk, _ = _fit_cox(df, cols, tm, time_col, event_col, horizon)
            r[name] = cidx(t, e, risk)
            per[name].append(r[name])
        if "clinical" in r and "clinical+cytogenetics+omics" in r:
            d_full.append(r["clinical+cytogenetics+omics"] - r["clinical"])
        if "clinical" in r and "clinical+omics" in r:
            d_om.append(r["clinical+omics"] - r["clinical"])
    lb = [{"feature_set": k, "n_splits": len(v), "mean_cindex": round(np.mean(v), 4),
           "sd_cindex": round(np.std(v), 4), "ci_low": round(np.percentile(v, 2.5), 4),
           "ci_high": round(np.percentile(v, 97.5), 4)} for k, v in per.items() if v]
    def drow(lbl, a):
        a = np.array(a)
        return {"comparison": lbl, "n_splits": len(a), "mean_delta": round(a.mean(), 4),
                "sd_delta": round(a.std(), 4), "ci_low": round(np.percentile(a, 2.5), 4),
                "ci_high": round(np.percentile(a, 97.5), 4), "frac_splits_improved": round(np.mean(a > 0), 3)}
    deltas = pd.DataFrame([drow("clinical+omics_vs_clinical", d_om),
                           drow("clinical+cyto+omics_vs_clinical", d_full)])
    return pd.DataFrame(lb).sort_values("mean_cindex", ascending=False), deltas


def _cal_dca_nri(probs, t, e, horizon):
    cal, dec = [], []
    for name, p in probs.items():
        m, deciles = calibration_metrics(t, e, p, horizon)
        cal.append({"model": name, **m})
        for d in deciles:
            dec.append({"model": name, **d})
    nri = []
    for old, new in [("clinical", "clinical+omics"),
                     ("clinical+cytogenetics", "clinical+cytogenetics+omics")]:
        if old in probs and new in probs:
            nri.append({"comparison": f"{new}_vs_{old}", **nri_idi(t, e, probs[old], probs[new], horizon)})
    return pd.DataFrame(cal), pd.DataFrame(dec), pd.DataFrame(decision_curve(t, e, probs, horizon)), pd.DataFrame(nri)


def _subtypes(df, groups, decomp, time_col, event_col, cfg):
    exp = cfg.get("experiments", {})
    mh = int(exp.get("min_subtype_events_hypothesis", 10))
    mc = int(exp.get("min_subtype_events_confirmatory", 30))
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
            cc = cidx(merged[time_col].values[pos], merged[event_col].values[pos], merged.clinical_risk.values[pos])
            ct = cidx(merged[time_col].values[pos], merged[event_col].values[pos], merged.total_risk.values[pos])
            d = ct - cc
            lvl = ("potentially_confirmatory_pending_paired_ci" if ev >= mc and d > 0
                   else "hypothesis_generating" if ev >= mh else "unstable_descriptive_only")
            rec.update({"clinical_cindex": round(cc, 3), "clinical_omics_cindex": round(ct, 3),
                        "delta_cindex": round(d, 3), "evidence_level": lvl})
        rows.append(rec)
    return pd.DataFrame(rows)


def _tertiles(x):
    return pd.qcut(pd.Series(x).rank(method="first"), 3, labels=["low", "mid", "high"]).astype(object).values


def _usefulness_outcomes(df, groups, decomp, time_col, event_col, horizon):
    d = decomp.copy()
    d["clinical_grp"] = _tertiles(d.clinical_risk.values)
    d["total_grp"] = _tertiles(d.total_risk.values)
    d["resid_grp"] = _tertiles(d.molecular_residual_risk.values)
    rk = {"low": 0, "mid": 1, "high": 2}
    rec = d[d.clinical_grp != d.total_grp]
    up = rec[rec.apply(lambda r: rk[r.total_grp] > rk[r.clinical_grp], axis=1)]
    down = rec[rec.apply(lambda r: rk[r.total_grp] < rk[r.clinical_grp], axis=1)]
    cs_mh = d[(d.clinical_grp.isin(["low", "mid"])) & (d.resid_grp == "high")]
    hr_cyto = [c for c in ["del17p", "t_4_14", "amp1q", "t_14_16"] if c in df.columns]
    dfi = df.set_index("patient_id")
    flags = dfi.reindex(d.patient_id)[hr_cyto].apply(pd.to_numeric, errors="coerce").fillna(0) > 0
    cyto_high = flags.any(axis=1).values
    cyto_high_mol_low = d[(cyto_high) & (d.total_risk.values < np.median(d.total_risk.values))]

    clin_bin = np.where(pd.Series(d.clinical_risk.values).rank(pct=True) > 0.5, "high", "low")
    mol_bin = np.where(pd.Series(d.molecular_residual_risk.values).rank(pct=True) > 0.5, "high", "low")
    d2 = d.copy()
    d2["grp"] = [f"clinical_{c}__molecular_{m}" for c, m in zip(clin_bin, mol_bin)]
    d2.loc[cyto_high & (mol_bin == "low"), "grp_cyto"] = "cyto_high__molecular_low"
    d2.loc[(~cyto_high) & (mol_bin == "high"), "grp_cyto"] = "cyto_low__molecular_high"
    t_all, e_all = d2[time_col].values, d2[event_col].values
    rows = []
    gd = [("grp", g) for g in ["clinical_low__molecular_low", "clinical_low__molecular_high",
                               "clinical_high__molecular_low", "clinical_high__molecular_high"]]
    gd += [("grp_cyto", "cyto_high__molecular_low"), ("grp_cyto", "cyto_low__molecular_high")]
    for col, g in gd:
        if col not in d2:
            continue
        m = (d2[col] == g).values
        n, ev = int(m.sum()), int(e_all[m].sum())
        if n == 0:
            continue
        er = _km_event_prob(t_all[m], e_all[m], horizon)
        med = KaplanMeierFitter().fit(t_all[m], e_all[m]).median_survival_time_
        lr = logrank_test(t_all[m], t_all[~m], e_all[m], e_all[~m])
        try:
            cph = CoxPHFitter().fit(pd.DataFrame({"g": m.astype(int), "t": t_all, "e": e_all}),
                                    duration_col="t", event_col="e")
            hr = float(np.exp(cph.params_["g"]))
        except Exception:
            hr = np.nan
        rows.append({"group": g, "n_patients": n, "n_events": ev,
                     "event_rate_by_horizon": round(float(er), 4),
                     "median_survival_months": (round(float(med), 1) if np.isfinite(med) else "not_reached"),
                     "logrank_p_vs_rest": round(float(lr.p_value), 4),
                     "hazard_ratio_vs_rest": round(hr, 3) if np.isfinite(hr) else np.nan})
    summary = {"n_reclassified_by_omics": int(len(rec)), "n_reclassified_up": int(len(up)),
               "n_reclassified_down": int(len(down)),
               "n_clinical_standard_but_molecular_high": int(len(cs_mh)),
               "n_cytogenetic_highrisk_but_molecular_lower": int(len(cyto_high_mol_low)),
               "n_cytogenetic_highrisk_total": int(cyto_high.sum()),
               "note": "Reclassification matters only if outcomes differ; see mmrf_reclassification_outcomes.csv."}
    return summary, pd.DataFrame(rows), d2


def evaluate_model_suite(cfg: dict) -> dict:
    schema = cfg["schema"]
    time_col, event_col = schema["time_col"], schema["event_col"]
    seed = int(cfg.get("seed", 42))
    horizon = float(cfg.get("validation", {}).get("horizon_months", HORIZON_MONTHS))
    n_splits = int(cfg.get("validation", {}).get("repeated_splits", 50))
    external_val = bool(cfg.get("validation", {}).get("external_validation_available", False))
    endpoint_spec = resolve_endpoint(cfg)

    df, groups = build_matched_cohort(cfg)
    tm = stratified_event_split(df, event_col, seed)

    ablation, risks, probs, (t, e) = _ablation(df, groups, tm, time_col, event_col, seed, horizon)
    decomp, clin_coef, mol_coef, diag = _decomposition(df, groups, tm, time_col, event_col)
    deltas = _paired(risks, decomp, t, e, seed)
    rep_lb, rep_delta = _repeated(df, groups, time_col, event_col, seed, n_splits, horizon)
    cal, cal_decile, dca, nri = _cal_dca_nri(probs, t, e, horizon)
    subtypes = _subtypes(df, groups, decomp, time_col, event_col, cfg)
    summary, outcomes, quad = _usefulness_outcomes(df, groups, decomp, time_col, event_col, horizon)

    a = ablation.set_index("feature_set")
    key = deltas[deltas.comparison == "clinical+cyto+omics_vs_clinical"]
    kd = float(key.delta_cindex.iloc[0]) if len(key) else np.nan
    kci = float(key.delta_ci_low.iloc[0]) if len(key) else np.nan
    detail = {"matched_n": int(len(df)), "test_events": int(e.sum()),
              "analysis_type": "scientific_matched_cohort" if cfg.get("cohort", {}).get("matched_ablation", True)
              else "deployment_availability",
              "clinical_cindex": float(a.loc["clinical", "test_cindex"]) if "clinical" in a.index else np.nan,
              "full_cindex": float(a.loc["clinical+cytogenetics+omics", "test_cindex"])
              if "clinical+cytogenetics+omics" in a.index else np.nan,
              "omics_paired_delta": kd, "omics_paired_delta_ci_low": kci,
              "molecular_residual_test_cindex": round(diag["molecular_residual_risk"], 4)}
    claim = build_claim_report(endpoint_spec, omics_delta=kd, omics_delta_ci_low=kci,
                               external_validation_available=external_val, detail=detail)
    leakage = {"imputer_fit_on": "train", "scaler_fit_on": "train", "pca_fit_on": "train_or_precomputed",
               "orthogonalizer_fit_on": "train", "cox_fit_on": "train", "test_used_for_model_selection": False,
               "split_strategy": cfg.get("splitting", {}).get("strategy", "stratified_event"),
               "note": "Omics PCA fit once on full RNA cohort (unsupervised); all survival-model "
                       "preprocessing is train-only. No test outcomes touch any coefficient."}

    return {"endpoint_spec": endpoint_spec, "cohort_df": df, "groups": groups,
            "ablation": ablation, "paired_deltas": deltas, "decomposition": decomp,
            "clinical_coef": clin_coef, "molecular_coef": mol_coef, "diag": diag,
            "repeated_leaderboard": rep_lb, "repeated_delta": rep_delta,
            "calibration": cal, "calibration_decile": cal_decile, "dca": dca, "nri": nri,
            "subtypes": subtypes, "usefulness": summary, "outcomes": outcomes, "quadrants": quad,
            "claim_report": claim, "leakage_audit": leakage, "horizon": horizon}
