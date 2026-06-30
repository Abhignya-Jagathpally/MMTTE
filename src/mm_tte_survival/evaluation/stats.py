"""Statistical helpers for endpoint-correct, claim-gated survival evaluation.

All functions are pure (operate on numpy arrays) so they can be unit-tested and
reused across the residual report and any future endpoint.
"""
from __future__ import annotations

import numpy as np

from ..metrics import fast_c_index as harrell_c_index


# --------------------------------------------------------------------------- #
# Paired delta C-index (same test patients) with bootstrap CI
# --------------------------------------------------------------------------- #
def paired_delta_cindex(t, e, risk_a, risk_b, n_boot=2000, seed=42):
    """C(A) - C(B) with a PAIRED bootstrap over the same resampled patients.

    A is the richer model, B the baseline. Returns dict with point estimate,
    95% CI, one-sided bootstrap p (P[delta<=0]), and a claim label.
    """
    t = np.asarray(t, float); e = np.asarray(e, int)
    ra = np.asarray(risk_a, float); rb = np.asarray(risk_b, float)
    c_a = harrell_c_index(t, e, ra)
    c_b = harrell_c_index(t, e, rb)
    delta = c_a - c_b
    rng = np.random.default_rng(seed)
    n = len(t)
    deltas = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        if e[idx].sum() < 2:
            continue
        da = harrell_c_index(t[idx], e[idx], ra[idx])
        db = harrell_c_index(t[idx], e[idx], rb[idx])
        if np.isfinite(da) and np.isfinite(db):
            deltas.append(da - db)
    deltas = np.asarray(deltas)
    if deltas.size == 0:
        lo = hi = p = np.nan
    else:
        lo, hi = np.percentile(deltas, [2.5, 97.5])
        p = float(np.mean(deltas <= 0))  # one-sided: evidence that A does NOT beat B
    if np.isfinite(lo) and lo > 0:
        claim = "confirmed_improvement"
    elif delta > 0:
        claim = "hypothesis_generating_improvement"
    else:
        claim = "no_evidence_of_improvement"
    return {"cindex_model_a": round(float(c_a), 4), "cindex_model_b": round(float(c_b), 4),
            "delta_cindex": round(float(delta), 4),
            "delta_ci_low": round(float(lo), 4) if np.isfinite(lo) else np.nan,
            "delta_ci_high": round(float(hi), 4) if np.isfinite(hi) else np.nan,
            "p_bootstrap": round(float(p), 4) if np.isfinite(p) else np.nan,
            "claim": claim}


# --------------------------------------------------------------------------- #
# Evidence-level labelling
# --------------------------------------------------------------------------- #
def evidence_level(endpoint_type, proposal_target, delta_cindex, delta_ci_low,
                   external_validation_available):
    """Map a result to confirmatory / hypothesis_generating / technical_validation_only
    / unsupported per the agreed rules."""
    relapse_targets = {"relapse", "pfs", "progression", "time_to_progression",
                       "time_to_relapse", "early_progression"}
    if endpoint_type in {"overall_survival", "os"} and proposal_target in relapse_targets:
        return "technical_validation_only"
    if (delta_ci_low is not None and np.isfinite(delta_ci_low)
            and delta_ci_low > 0 and external_validation_available):
        return "confirmatory"
    if delta_cindex is not None and delta_cindex > 0 and (delta_ci_low is None or delta_ci_low <= 0):
        return "hypothesis_generating"
    return "unsupported"


# --------------------------------------------------------------------------- #
# Calibration (needs predicted EVENT probability at a landmark horizon)
# --------------------------------------------------------------------------- #
def calibration_metrics(t, e, p_event, horizon, n_bins=10):
    """Calibration of predicted event probability by `horizon`.

    Observed risk per bin uses 1 - KM(horizon) within the bin (handles censoring).
    Returns scalar metrics + a per-decile table (list of dicts).
    """
    t = np.asarray(t, float); e = np.asarray(e, int); p = np.asarray(p_event, float)
    # Brier score at horizon with IPCW-free approximation (events known by horizon)
    y = ((t <= horizon) & (e == 1)).astype(float)
    known = ~((t < horizon) & (e == 0))  # exclude censored-before-horizon from naive Brier
    brier = float(np.mean((p[known] - y[known]) ** 2)) if known.sum() else np.nan

    # calibration slope / in-the-large via logistic-like fit on cloglog of p
    eps = 1e-6
    pc = np.clip(p, eps, 1 - eps)
    lp = np.log(-np.log(1 - pc))  # complementary log-log
    # observed per-bin KM
    order = np.argsort(p)
    bins = np.array_split(order, n_bins)
    rows, obs_all, pred_all = [], [], []
    for i, idx in enumerate(bins):
        if len(idx) == 0:
            continue
        obs = _km_event_prob(t[idx], e[idx], horizon)
        pred = float(np.mean(p[idx]))
        rows.append({"decile": i + 1, "n": int(len(idx)), "pred_event_prob": round(pred, 4),
                     "observed_event_prob": round(obs, 4) if np.isfinite(obs) else np.nan})
        if np.isfinite(obs):
            obs_all.append(obs); pred_all.append(pred)
    cal_slope = cal_large = np.nan
    if len(obs_all) >= 3:
        pred_all = np.array(pred_all); obs_all = np.array(obs_all)
        A = np.vstack([np.ones_like(pred_all), pred_all]).T
        coef, *_ = np.linalg.lstsq(A, obs_all, rcond=None)
        cal_large = float(coef[0] + (coef[1] - 1) * np.mean(pred_all))  # mean obs - mean pred proxy
        cal_slope = float(coef[1])
        cal_large = float(np.mean(obs_all) - np.mean(pred_all))
    return {"brier_at_horizon": round(brier, 4) if np.isfinite(brier) else np.nan,
            "calibration_slope": round(cal_slope, 4) if np.isfinite(cal_slope) else np.nan,
            "calibration_in_the_large": round(cal_large, 4) if np.isfinite(cal_large) else np.nan,
            "horizon": horizon}, rows


def _km_event_prob(t, e, horizon):
    """1 - KM(horizon): observed cumulative event probability with censoring."""
    t = np.asarray(t, float); e = np.asarray(e, int)
    order = np.argsort(t)
    t, e = t[order], e[order]
    surv, n = 1.0, len(t)
    at_risk = n
    seen = set()
    for i in range(n):
        if t[i] > horizon:
            break
        if e[i] == 1:
            surv *= (1 - 1.0 / at_risk)
        at_risk -= 1
        if at_risk <= 0:
            break
    return 1.0 - surv


# --------------------------------------------------------------------------- #
# Decision-curve analysis (net benefit at risk thresholds)
# --------------------------------------------------------------------------- #
def decision_curve(t, e, models: dict[str, np.ndarray], horizon,
                   thresholds=(0.1, 0.2, 0.3, 0.4, 0.5)):
    """Net benefit at each threshold for each model + treat-all / treat-none.

    models: name -> predicted event probability by horizon. Event prevalence and
    treat-all benefit use KM at horizon to respect censoring.
    """
    t = np.asarray(t, float); e = np.asarray(e, int)
    n = len(t)
    prev = _km_event_prob(t, e, horizon)
    rows = []
    for th in thresholds:
        w = th / (1 - th)
        row = {"threshold": th, "treat_all": round(prev - (1 - prev) * w, 4), "treat_none": 0.0}
        for name, p in models.items():
            p = np.asarray(p, float)
            flagged = p >= th
            nf = flagged.sum()
            if nf == 0:
                row[name] = 0.0
                continue
            tp_rate = _km_event_prob(t[flagged], e[flagged], horizon) * (nf / n)
            fp_rate = (1 - _km_event_prob(t[flagged], e[flagged], horizon)) * (nf / n)
            row[name] = round(float(tp_rate - fp_rate * w), 4)
        rows.append(row)
    return rows


# --------------------------------------------------------------------------- #
# NRI / IDI (predicted event probability, two models)
# --------------------------------------------------------------------------- #
def nri_idi(t, e, p_old, p_new, horizon, n_cat_bins=(0.1, 0.2, 0.3)):
    """Categorical NRI + IDI comparing p_old vs p_new at a horizon.

    Events = observed by horizon (excludes censored-before-horizon for NRI/IDI).
    """
    t = np.asarray(t, float); e = np.asarray(e, int)
    p_old = np.asarray(p_old, float); p_new = np.asarray(p_new, float)
    known = ~((t < horizon) & (e == 0))
    y = ((t <= horizon) & (e == 1)).astype(int)[known]
    po, pn = p_old[known], p_new[known]
    cats = np.array(n_cat_bins)

    def cat(p):
        return np.digitize(p, cats)
    co, cn = cat(po), cat(pn)
    ev, nev = y == 1, y == 0
    nri_ev = (np.sum(cn[ev] > co[ev]) - np.sum(cn[ev] < co[ev])) / max(ev.sum(), 1)
    nri_nev = (np.sum(cn[nev] < co[nev]) - np.sum(cn[nev] > co[nev])) / max(nev.sum(), 1)
    nri = nri_ev + nri_nev
    idi = (np.mean(pn[ev]) - np.mean(po[ev])) - (np.mean(pn[nev]) - np.mean(po[nev])) \
        if ev.sum() and nev.sum() else np.nan
    return {"nri": round(float(nri), 4), "nri_events": round(float(nri_ev), 4),
            "nri_nonevents": round(float(nri_nev), 4),
            "idi": round(float(idi), 4) if np.isfinite(idi) else np.nan,
            "n_events": int(ev.sum()), "n_nonevents": int(nev.sum()), "horizon": horizon}
