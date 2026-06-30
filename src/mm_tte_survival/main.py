"""High-level production entrypoint.

Exposes the abstract scientific workflow: configuration, endpoint resolution,
data loading + contracts, matched-cohort construction, train-only preprocessing,
the residual-risk model + endpoint-correct evaluation suite, and endpoint-gated
reporting. The neural MultiHeadSurvivalModel is a parallel experimental path; the
default production model is the interpretable ResidualRiskModel.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from mm_tte_survival.config import load_app_config, set_seed
from mm_tte_survival.endpoints import resolve_endpoint
from mm_tte_survival.data.loaders import load_modalities
from mm_tte_survival.data.contracts import validate_all_inputs
from mm_tte_survival.evaluation.evaluate import evaluate_model_suite
from mm_tte_survival.reports.run_reports import write_all_reports


def run_pipeline(config_path: str) -> dict:
    cfg = load_app_config(config_path)
    set_seed(cfg.seed)
    raw_cfg = cfg.to_dict()

    # 1. endpoint + claim context
    endpoint = resolve_endpoint(raw_cfg)

    # 2. data loading
    raw = load_modalities(
        clinical_path=cfg.paths.clinical,
        cytogenetics_path=cfg.paths.cytogenetics,
        omics_path=cfg.paths.omics,
        program_activity_path=getattr(cfg.paths, "program_activity", None),
    )

    # 3. contracts / leakage / provenance checks
    validate_all_inputs(raw=raw, endpoint=endpoint, schema=raw_cfg["schema"],
                        output_dir=cfg.paths.outdir)

    # 4-8. matched cohort, train-only preprocessing, residual-risk model, evaluation suite
    results = evaluate_model_suite(raw_cfg)

    # 9. endpoint-gated reports + cards
    outdir = write_all_reports(raw_cfg, results)

    c = results["claim_report"]
    print(f"[{endpoint['name']} / {endpoint['endpoint_type']}] "
          f"technical_validation={c['technical_validation_claim_allowed']} "
          f"relapse_pfs={c['relapse_or_pfs_claim_allowed']} "
          f"omics={c['omics_increment_summary']} -> {outdir}")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="MM-TTE residual-risk pipeline")
    parser.add_argument("--config", default="configs/experiments/experiment0_open_gdc_os.yaml",
                        help="Path to experiment config.")
    args = parser.parse_args()
    run_pipeline(args.config)


if __name__ == "__main__":
    main()
