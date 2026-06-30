from __future__ import annotations

import numpy as np


def harrell_c_index(time, event, risk) -> float:
    """Harrell concordance for right-censored data.

    Higher risk should correspond to shorter event time.
    Pairs are comparable when the earlier observed time is an event.
    """
    t = np.asarray(time, dtype=float)
    e = np.asarray(event, dtype=int)
    r = np.asarray(risk, dtype=float)
    if len(t) != len(e) or len(t) != len(r):
        raise ValueError("time, event, risk must have the same length")
    concordant = 0.0
    permissible = 0.0
    n = len(t)
    for i in range(n):
        for j in range(i + 1, n):
            if t[i] == t[j]:
                continue
            if t[i] < t[j] and e[i] == 1:
                permissible += 1
                concordant += 1.0 if r[i] > r[j] else 0.5 if r[i] == r[j] else 0.0
            elif t[j] < t[i] and e[j] == 1:
                permissible += 1
                concordant += 1.0 if r[j] > r[i] else 0.5 if r[i] == r[j] else 0.0
    return float(concordant / permissible) if permissible > 0 else float("nan")


def fast_c_index(time, event, risk) -> float:
    """Vectorised Harrell C-index (numpy). Identical definition to
    harrell_c_index but O(n^2) in numpy instead of Python loops, for use in
    bootstrap- and repeated-split-heavy code paths."""
    t = np.asarray(time, dtype=float)
    e = np.asarray(event, dtype=int)
    r = np.asarray(risk, dtype=float)
    comparable = (t[:, None] < t[None, :]) & (e[:, None] == 1)
    den = comparable.sum()
    if den == 0:
        return float("nan")
    conc = (r[:, None] > r[None, :]).astype(float) + 0.5 * (r[:, None] == r[None, :])
    return float((comparable * conc).sum() / den)


def bootstrap_ci(time, event, risk, n_boot: int = 250, seed: int = 42, alpha: float = 0.05) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    time = np.asarray(time)
    event = np.asarray(event)
    risk = np.asarray(risk)
    vals = []
    n = len(time)
    for _ in range(n_boot):
        idx = rng.integers(0, n, size=n)
        val = harrell_c_index(time[idx], event[idx], risk[idx])
        if np.isfinite(val):
            vals.append(val)
    if not vals:
        return (float("nan"), float("nan"))
    return (float(np.quantile(vals, alpha / 2)), float(np.quantile(vals, 1 - alpha / 2)))


def integrated_brier_proxy(time, event, risk) -> float:
    """A lightweight risk-ranking Brier proxy.

    This is not a full IPCW integrated Brier score; it is included only as a
    smoke-test metric when scikit-survival is unavailable. Use scikit-survival
    or riskRegression for publication-grade IBS.
    """
    t = np.asarray(time, dtype=float)
    e = np.asarray(event, dtype=float)
    r = np.asarray(risk, dtype=float)
    if len(np.unique(r)) > 1:
        p = 1 / (1 + np.exp(-(r - np.mean(r)) / (np.std(r) + 1e-8)))
    else:
        p = np.repeat(np.mean(e), len(e))
    horizon = np.median(t)
    y = ((t <= horizon) & (e == 1)).astype(float)
    return float(np.mean((y - p) ** 2))
