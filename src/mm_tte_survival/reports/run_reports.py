"""write_all_reports — persist every artifact from evaluate_model_suite."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from ..config import ensure_outdir
from . import cards
from .figures import write_reclassification_km


def _yn(b):
    return "YES" if b else "NO"


def write_all_reports(cfg: dict, results: dict, extra: dict | None = None) -> Path:
    outdir = ensure_outdir(cfg["paths"].get("outdir", "outputs/run"))
    ep = results["endpoint_spec"]
    claim = results["claim_report"]
    detail = claim["_detail"]
    diag = results["diag"]

    # annotate molecular drivers with provenance + mapped genes
    drivers = results["molecular_coef"].head(15).copy()
    drivers["provenance"] = drivers["feature_kind"].map(
        lambda k: "CNV/RNA-surrogate cytogenetic call" if k == "cytogenetic_call"
        else "RNA PC loading-derived (NOT a direct gene-level causal feature)")
    loadings = Path(cfg["paths"]["clinical"]).parent / "omics_pc_loadings.csv"
    if loadings.exists():
        load_df = pd.read_csv(loadings, index_col=0)
        drivers["mapped_genes"] = [
            ";".join(load_df[f].abs().sort_values(ascending=False).head(5).index) if f in load_df.columns else ""
            for f in drivers.feature]

    # ---- CSV / JSON ----
    results["ablation"].to_csv(outdir / "matched_ablation.csv", index=False)
    results["paired_deltas"].to_csv(outdir / "paired_delta_cindex.csv", index=False)
    results["decomposition"].to_csv(outdir / "residual_risk_decomposition.csv", index=False)
    results["clinical_coef"].to_csv(outdir / "clinical_risk_coefficients.csv", index=False)
    results["molecular_coef"].to_csv(outdir / "molecular_residual_coefficients.csv", index=False)
    drivers.to_csv(outdir / "molecular_residual_top_drivers.csv", index=False)
    results["repeated_leaderboard"].to_csv(outdir / "repeated_split_leaderboard.csv", index=False)
    results["repeated_delta"].to_csv(outdir / "repeated_split_delta_cindex.csv", index=False)
    results["calibration"].to_csv(outdir / "calibration_metrics.csv", index=False)
    results["calibration_decile"].to_csv(outdir / "calibration_by_decile.csv", index=False)
    results["dca"].to_csv(outdir / "decision_curve_analysis.csv", index=False)
    results["nri"].to_csv(outdir / "reclassification_metrics.csv", index=False)
    results["subtypes"].to_csv(outdir / "mmrf_subtype_gain_fail.csv", index=False)
    results["outcomes"].to_csv(outdir / "mmrf_reclassification_outcomes.csv", index=False)
    (outdir / "claim_report.json").write_text(json.dumps(claim, indent=2))
    (outdir / "mmrf_usefulness_summary.json").write_text(json.dumps(results["usefulness"], indent=2))
    (outdir / "leakage_audit.json").write_text(json.dumps(results["leakage_audit"], indent=2))

    # ---- figure ----
    write_reclassification_km(outdir, results["quadrants"], cfg["schema"]["time_col"],
                              cfg["schema"]["event_col"])

    # ---- markdown reports + cards ----
    _write_main_md(outdir, results, drivers)
    _write_claim_md(outdir, claim)
    _write_gate_md(outdir, ep, claim)
    cards.write_claim_card(outdir, ep, claim, detail)
    cards.write_data_card(outdir, ep, results["cohort_df"], results["groups"], detail)
    cards.write_model_card(outdir, ep, diag, results["ablation"], detail)
    cards.write_mmrf_usefulness(outdir, results["usefulness"], results["subtypes"],
                                results["outcomes"], claim)
    cards.write_experiment_summary(outdir, ep, detail, claim, results["usefulness"])
    return outdir


def _write_main_md(outdir, results, drivers):
    ep, claim, diag = results["endpoint_spec"], results["claim_report"], results["diag"]
    detail = claim["_detail"]
    ab, de = results["ablation"], results["paired_deltas"]
    L = [f"# Experiment 0 — {ep.get('name')} ({ep.get('endpoint_type')}): matched-cohort "
         "technical-validation & residual-risk pilot", "",
         f"analysis_type **{detail['analysis_type']}** · matched N={detail['matched_n']} · "
         f"test events={detail['test_events']}.", "",
         f"> Headline: omics moved held-out C from {detail['clinical_cindex']:.3f} (clinical) to "
         f"{detail['full_cindex']:.3f} (clinical+cyto+omics). Paired ΔC CI overlaps 0 and the endpoint "
         "is OS ⇒ **hypothesis-generating evidence of molecular residual signal, not confirmatory.**", "",
         "## [1] Endpoint-gated claim report", "",
         f"- technical_validation_claim_allowed: **{_yn(claim['technical_validation_claim_allowed'])}**",
         f"- primary_biological_claim_allowed: **{_yn(claim['primary_biological_claim_allowed'])}**",
         f"- relapse_or_pfs_claim_allowed: **{_yn(claim['relapse_or_pfs_claim_allowed'])}**",
         f"- omics_increment_confirmed: **{_yn(claim['omics_increment_confirmed'])}** "
         f"({claim['omics_increment_summary']})",
         f"- external_validation_available: **{_yn(claim['external_validation_available'])}**",
         f"- evidence_level: **{claim['evidence_level_for_omics_increment']}**", "",
         "## [3] Matched-cohort ablation", "", "| Feature set | #feat | Test C | 95% CI |", "|---|---|---|---|"]
    for _, r in ab.iterrows():
        L.append(f"| {r['feature_set']} | {r['n_features']} | {r['test_cindex']:.3f} | {r['ci_low']:.3f}–{r['ci_high']:.3f} |")
    L += ["", "## [2] Paired ΔC-index (same test patients)", "",
          "| Comparison | ΔC | ΔCI low | ΔCI high | p_boot | claim |", "|---|---|---|---|---|---|"]
    for _, r in de.iterrows():
        L.append(f"| {r['comparison']} | {r['delta_cindex']:+.3f} | {r['delta_ci_low']:+.3f} | "
                 f"{r['delta_ci_high']:+.3f} | {r['p_bootstrap']} | {r['claim']} |")
    L += ["", f"Residual decomposition held-out C — clinical **{diag['clinical_risk']:.3f}**, "
          f"molecular_residual **{diag['molecular_residual_risk']:.3f}**, total **{diag['total_risk']:.3f}** "
          f"(clinical coef in joint {diag['clinical_coef_in_joint']:.3f} ≈ 1 ⇒ clean offset).", "",
          "## Repeated stratified-split validation", "", "| Feature set | splits | mean C | sd | 95% CI |",
          "|---|---|---|---|---|"]
    for _, r in results["repeated_leaderboard"].iterrows():
        L.append(f"| {r['feature_set']} | {r['n_splits']} | {r['mean_cindex']:.3f} | {r['sd_cindex']:.3f} | "
                 f"{r['ci_low']:.3f}–{r['ci_high']:.3f} |")
    L += ["", "| Δ comparison | mean Δ | 95% CI | frac improved |", "|---|---|---|---|"]
    for _, r in results["repeated_delta"].iterrows():
        L.append(f"| {r['comparison']} | {r['mean_delta']:+.3f} | {r['ci_low']:+.3f}–{r['ci_high']:+.3f} | "
                 f"{r['frac_splits_improved']:.2f} |")
    L += ["", "## [7] Reclassification OUTCOME validation", "",
          "| Group | n | events | event-rate@h | median OS | log-rank p | HR vs rest |",
          "|---|---|---|---|---|---|---|"]
    for _, r in results["outcomes"].iterrows():
        L.append(f"| {r['group']} | {r['n_patients']} | {r['n_events']} | {r['event_rate_by_horizon']} | "
                 f"{r['median_survival_months']} | {r['logrank_p_vs_rest']} | {r['hazard_ratio_vs_rest']} |")
    L += ["", "## Top molecular-residual drivers (provenance-flagged)", "",
          "| feature | coef | direction | kind | mapped_genes |", "|---|---|---|---|---|"]
    for _, r in drivers.head(10).iterrows():
        L.append(f"| {r['feature']} | {r['coef']:+.3f} | {r['direction']} | {r['feature_kind']} | "
                 f"{r.get('mapped_genes','')} |")
    L += ["", "_RNA drivers are PC-loading-derived, NOT direct gene-level causal features._"]
    (outdir / "residual_and_usefulness_report.md").write_text("\n".join(L) + "\n")


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
         f"- evidence_level: **{report['evidence_level_for_omics_increment']}**",
         f"- omics paired ΔC: {d['omics_paired_delta']:+.3f} (CI low {d['omics_paired_delta_ci_low']:+.3f})",
         "", "An OS endpoint cannot license a relapse/PFS or primary biological claim."]
    (outdir / "claim_report.md").write_text("\n".join(L) + "\n")


def _write_gate_md(outdir, ep, report):
    d = report["_detail"]
    L = [f"# Endpoint gate report — {ep.get('name')}", "",
         f"endpoint_type: `{ep.get('endpoint_type')}` · role: `{ep.get('role')}`", "",
         f"- technical_validation_claim_allowed: **{_yn(report['technical_validation_claim_allowed'])}**",
         f"- primary_biological_claim_allowed: **{_yn(report['primary_biological_claim_allowed'])}**",
         f"- relapse_or_pfs_claim_allowed: **{_yn(report['relapse_or_pfs_claim_allowed'])}**",
         f"- omics_increment: **{report['omics_increment_summary']}** "
         f"(ΔC={d['omics_paired_delta']:+.3f}, CI low={d['omics_paired_delta_ci_low']:+.3f})",
         f"- evidence_level: **{report['evidence_level_for_omics_increment']}**", "",
         "This run uses an **overall-survival** endpoint and therefore CANNOT license a relapse/PFS "
         "or primary biological claim (technical-validation + residual-risk pilot, Experiment 0)."]
    (outdir / "endpoint_gate_report.md").write_text("\n".join(L) + "\n")
