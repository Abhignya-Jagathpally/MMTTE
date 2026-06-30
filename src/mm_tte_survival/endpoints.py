"""Endpoint registry loader + claim gating.

The endpoint a run declares (cfg['endpoint']['name']) is resolved against
configs/endpoints.yaml. Claim flags are derived ONLY from the endpoint type and
the available evidence, so the code cannot emit a relapse/PFS claim on an OS run.
"""
from __future__ import annotations

from pathlib import Path
import yaml

RELAPSE_ENDPOINTS = {"pfs", "progression_free_survival", "time_to_progression",
                     "time_to_relapse", "early_progression", "early_progression_landmark"}


def load_registry(path: str | Path = "configs/endpoints.yaml") -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    with p.open() as f:
        return yaml.safe_load(f) or {}


def resolve_endpoint(cfg: dict, registry_path: str | Path = "configs/endpoints.yaml") -> dict:
    """Return the endpoint spec for this run (name from cfg, type from registry)."""
    ep = cfg.get("endpoint", {}) or {}
    name = ep.get("name", "unknown")
    reg = load_registry(registry_path)
    spec = dict(reg.get(name, {}))
    spec.setdefault("endpoint_type", _infer_type(ep))
    spec["name"] = name
    spec["claim_scope"] = ep.get("claim_scope", spec.get("role", "unknown"))
    return spec


def _infer_type(ep: dict) -> str:
    scope = (ep.get("claim_scope") or "").lower()
    if "pfs" in scope or "progression" in scope:
        return "progression_free_survival"
    if "overall_survival" in scope or "os" in scope:
        return "overall_survival"
    return "overall_survival"


def gate_claims(endpoint_spec: dict, *, omics_increment_confirmed: bool,
                external_validation_available: bool, proposal_target: str = "relapse") -> dict:
    """Compute the four separated claim flags.

    technical_validation is always allowed once the pipeline runs on real data;
    the biological/relapse claims are hard-gated on endpoint type + evidence.
    """
    et = endpoint_spec.get("endpoint_type", "overall_survival")
    is_relapse_endpoint = et in RELAPSE_ENDPOINTS

    technical_validation_claim_allowed = True
    relapse_or_pfs_claim_allowed = bool(is_relapse_endpoint)
    primary_biological_claim_allowed = bool(
        is_relapse_endpoint and external_validation_available and omics_increment_confirmed
    )
    return {
        "endpoint_name": endpoint_spec.get("name"),
        "endpoint_type": et,
        "endpoint_role": endpoint_spec.get("role", endpoint_spec.get("claim_scope")),
        "technical_validation_claim_allowed": technical_validation_claim_allowed,
        "primary_biological_claim_allowed": primary_biological_claim_allowed,
        "relapse_or_pfs_claim_allowed": relapse_or_pfs_claim_allowed,
        "omics_increment_confirmed": bool(omics_increment_confirmed),
        "external_validation_available": bool(external_validation_available),
        "proposal_target": proposal_target,
    }
