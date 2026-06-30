"""Endpoint-gated claim computation (wraps endpoints.gate_claims + evidence_level)."""
from __future__ import annotations

import numpy as np

from ..endpoints import gate_claims
from .stats import evidence_level


def build_claim_report(endpoint_spec, *, omics_delta, omics_delta_ci_low,
                       external_validation_available, detail) -> dict:
    omics_confirmed = bool(np.isfinite(omics_delta_ci_low) and omics_delta_ci_low > 0)
    claims = gate_claims(endpoint_spec, omics_increment_confirmed=omics_confirmed,
                         external_validation_available=external_validation_available,
                         proposal_target="relapse")
    ev = evidence_level(endpoint_spec.get("endpoint_type"), "relapse",
                        omics_delta, omics_delta_ci_low, external_validation_available)
    if np.isfinite(omics_delta) and omics_delta > 0 and not omics_confirmed:
        summary = "SUGGESTIVE_NOT_CONFIRMED"
    elif omics_confirmed:
        summary = "CONFIRMED"
    else:
        summary = "NO_EVIDENCE"
    return {**claims, "evidence_level_for_omics_increment": ev,
            "omics_increment_summary": summary, "_detail": detail}
