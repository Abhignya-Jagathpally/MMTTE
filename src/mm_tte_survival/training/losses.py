from __future__ import annotations

import torch
from torch import Tensor

_EPS = 1e-8


def cox_ph_loss(risk: Tensor, time: Tensor, event: Tensor) -> Tensor:
    """Negative Cox partial log likelihood.

    risk: higher means greater instantaneous hazard.
    time/event: right-censored survival labels.
    """
    risk = risk.reshape(-1)
    time = time.reshape(-1)
    event = event.reshape(-1).float()
    order = torch.argsort(time, descending=True)
    risk_ord = risk[order]
    event_ord = event[order]
    log_cum_hazard = torch.logcumsumexp(risk_ord, dim=0)
    partial = risk_ord - log_cum_hazard
    denom = torch.clamp(event_ord.sum(), min=1.0)
    return -(partial * event_ord).sum() / denom


def lognormal_aft_loss(params: Tensor, time: Tensor, event: Tensor) -> Tensor:
    """Right-censored log-normal accelerated failure time NLL."""
    mu = params[:, 0]
    log_sigma = torch.clamp(params[:, 1], -5.0, 3.0)
    sigma = torch.exp(log_sigma) + _EPS
    y = torch.log(torch.clamp(time.reshape(-1), min=_EPS))
    event = event.reshape(-1).float()
    z = (y - mu) / sigma
    normal = torch.distributions.Normal(torch.tensor(0.0, device=time.device), torch.tensor(1.0, device=time.device))
    log_pdf = normal.log_prob(z) - torch.log(sigma) - y
    surv = torch.clamp(1.0 - normal.cdf(z), min=_EPS)
    log_surv = torch.log(surv)
    nll = -(event * log_pdf + (1.0 - event) * log_surv)
    return nll.mean()


def first_hitting_time_loss(params: Tensor, time: Tensor, event: Tensor) -> Tensor:
    """Inverse-Gaussian first-hitting-time NLL for right-censored outcomes.

    The head predicts log_mu and log_lambda. This is a practical Brownian first
    passage approximation: T ~ IG(mu, lambda), where mu captures expected time
    to cross a resistance/progression boundary and lambda controls path noise.
    """
    log_mu = torch.clamp(params[:, 0], -5.0, 6.0)
    log_lam = torch.clamp(params[:, 1], -5.0, 6.0)
    mu = torch.exp(log_mu) + _EPS
    lam = torch.exp(log_lam) + _EPS
    t = torch.clamp(time.reshape(-1), min=_EPS)
    event = event.reshape(-1).float()

    log_pdf = 0.5 * (torch.log(lam) - torch.log(torch.tensor(2.0 * torch.pi, device=t.device)) - 3.0 * torch.log(t))
    log_pdf = log_pdf - lam * (t - mu) ** 2 / (2.0 * mu ** 2 * t + _EPS)

    normal = torch.distributions.Normal(torch.tensor(0.0, device=t.device), torch.tensor(1.0, device=t.device))
    sqrt_lam_t = torch.sqrt(lam / t)
    a = sqrt_lam_t * (t / mu - 1.0)
    b = -sqrt_lam_t * (t / mu + 1.0)
    exp_term = torch.exp(torch.clamp(2.0 * lam / mu, max=50.0))
    cdf = normal.cdf(a) + exp_term * normal.cdf(b)
    cdf = torch.clamp(cdf, min=0.0, max=1.0 - _EPS)
    log_surv = torch.log(torch.clamp(1.0 - cdf, min=_EPS))
    nll = -(event * log_pdf + (1.0 - event) * log_surv)
    return torch.nan_to_num(nll, nan=50.0, posinf=50.0, neginf=50.0).mean()


def risk_from_output(model_type: str, output: Tensor) -> Tensor:
    if model_type.endswith("cox") or model_type == "cox":
        return output.reshape(-1)
    # For AFT and FHT, shorter expected time means higher risk.
    return -output[:, 0].reshape(-1)


def soft_distillation_loss(student_risk: Tensor, teacher_risk: Tensor) -> Tensor:
    """MSE on standardized risk logits from an on-policy teacher.

    NOTE: a former `temperature` argument was a no-op — dividing by T and then
    z-standardizing cancels T exactly. It has been removed. This loss transfers
    only the risk *ranking*; prefer `survival_curve_distill` to transfer the
    calibrated survival distribution.
    """
    s = (student_risk - student_risk.mean()) / (student_risk.std(unbiased=False) + 1e-6)
    t = teacher_risk.detach()
    t = (t - t.mean()) / (t.std(unbiased=False) + 1e-6)
    return torch.mean((s - t) ** 2)


def cox_survival_curve(eta: Tensor, H_grid: Tensor) -> Tensor:
    """Differentiable S(tau|x) = exp(-H0(tau) exp(eta)) for a Cox head.

    eta: (n,) linear predictor; H_grid: (T,) detached Breslow baseline at the grid
    times. Returns (n, T). H_grid is treated as a constant (detached) so gradients
    flow only through eta — this is the standard curve-distillation surrogate.
    """
    return torch.exp(-torch.exp(eta).unsqueeze(1) * H_grid.unsqueeze(0))


def survival_curve_distill(s_student: Tensor, s_teacher: Tensor) -> Tensor:
    """Distributional self-distillation for censored survival.

    Squared difference between the student's and the (detached) teacher's
    predicted survival curves S(tau). Unlike `soft_distillation_loss` (ranking
    only), this transfers the calibrated risk — the under-explored target that
    should move IBS / D-calibration where global discrimination is ceilinged.
    """
    return torch.mean((s_student - s_teacher.detach()) ** 2)


def partial_multivariate_logrank_loss(group_probs: Tensor, time: Tensor, event: Tensor) -> Tensor:
    """Differentiable survival-separation auxiliary inspired by partial multivariate log-rank loss.

    group_probs is n x k soft assignment matrix. The loss maximizes squared
    observed-minus-expected event imbalance across soft groups. Use as an
    auxiliary only; supervised Cox/AFT/FHT losses remain the primary endpoints.
    """
    n, k = group_probs.shape
    order = torch.argsort(time.reshape(-1), descending=False)
    t = time.reshape(-1)[order]
    e = event.reshape(-1).float()[order]
    g = group_probs[order]
    observed = torch.zeros(k, device=time.device)
    expected = torch.zeros(k, device=time.device)
    variance = torch.zeros(k, device=time.device)
    for i in range(n):
        if e[i] <= 0:
            continue
        at_risk = t >= t[i]
        risk_weights = g[at_risk].sum(dim=0)
        total_risk = torch.clamp(risk_weights.sum(), min=1.0)
        observed = observed + g[i]
        expected = expected + risk_weights / total_risk
        p = risk_weights / total_risk
        variance = variance + p * (1.0 - p)
    z2 = (observed - expected) ** 2 / torch.clamp(variance, min=1e-3)
    return -torch.mean(z2)
