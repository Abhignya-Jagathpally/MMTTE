"""Model / claim / data cards + MMRF usefulness + experiment summary (markdown)."""
from __future__ import annotations

from pathlib import Path
import pandas as pd


def _yn(b):
    return "YES" if b else "NO"


def write_claim_card(outdir: Path, ep, claim, detail):
    L = [f"# Claim card — {ep.get('name')} ({ep.get('endpoint_type')})", "",
         f"- Endpoint: **{ep.get('endpoint_type')}** · dataset role: **{ep.get('role')}**",
         f"- Technical validation allowed: **{_yn(claim['technical_validation_claim_allowed'])}**",
         f"- Primary biological claim allowed: **{_yn(claim['primary_biological_claim_allowed'])}**",
         f"- Relapse/PFS claim allowed: **{_yn(claim['relapse_or_pfs_claim_allowed'])}**",
         f"- External validation: **{_yn(claim['external_validation_available'])}**",
         f"- Omics increment: **{claim['omics_increment_summary']}** "
         f"(ΔC={detail['omics_paired_delta']:+.3f}, CI low {detail['omics_paired_delta_ci_low']:+.3f})",
         f"- Evidence level: **{claim['evidence_level_for_omics_increment']}**",
         "- Clinical use: **no** · Research use: **yes**", "",
         "An overall-survival endpoint cannot license a relapse/PFS or primary biological claim."]
    (outdir / "claim_card.md").write_text("\n".join(L) + "\n")


def write_data_card(outdir: Path, ep, df, groups, detail):
    L = [f"# Data card — {ep.get('name')}", "",
         f"- Matched cohort: **{len(df)}** patients (all modalities), test events {detail['test_events']}",
         f"- Endpoint: {ep.get('endpoint_type')} (OS — progression/PFS not in open GDC clinical)",
         f"- Clinical features: {len(groups['clinical'])} · cytogenetics: {len(groups['cyto'])} "
         f"(SEQUENCING-INFERRED, NOT FISH; see cytogenetics_provenance.csv) · omics PCs: {len(groups['omics'])} "
         f"· programs: {len(groups['programs'])}",
         "- Provenance (all sequencing-inferred, NOT FISH): amp1q/del1p/del13q/del17p/hyperdiploid = "
         "GDC copy-number segments; t(4;14)/t(11;14)/t(14;16) = RNA expression surrogates. "
         "Externally FISH-validated only for del13/hyperdiploid (GSE6477); see docs/subtype_label_validation.md.",
         "- Preprocessing: train-only impute/scale; omics PCA unsupervised on full RNA cohort.",
         "- Splits: stratified-by-event, patient-disjoint."]
    (outdir / "data_card.md").write_text("\n".join(L) + "\n")


def write_model_card(outdir: Path, ep, diag, ablation, detail):
    a = ablation.set_index("feature_set")
    L = [f"# Model card — residual-risk TTE ({ep.get('name')})", "",
         "## Intended use", "Research-only residual-risk estimation. Not validated for clinical "
         "deployment, patient management, or treatment selection.", "",
         "## Architecture",
         "- Production model: ResidualRiskModel = clinical Cox + molecular-residual Cox "
         "(molecular orthogonalised vs clinical; total = clinical + residual, exact).",
         "- Parallel experimental: MultiHeadSurvivalModel (encoder + Cox/AFT/FHT); OPSD optional & claim-gated.", "",
         "## Performance (held-out, matched cohort)",
         f"- clinical C={detail['clinical_cindex']:.3f}; clinical+cyto+omics C={detail['full_cindex']:.3f}",
         f"- residual decomposition: clinical {diag['clinical_risk']:.3f} / "
         f"molecular_residual {diag['molecular_residual_risk']:.3f} / total {diag['total_risk']:.3f}", "",
         "## Limitations",
         "- Endpoint is OS, not PFS/relapse; wide CIs (small test); single cohort (no external validation).",
         "- RNA-derived drivers are PC-loading-derived, not direct gene-level causal features."]
    (outdir / "model_card.md").write_text("\n".join(L) + "\n")


def write_mmrf_usefulness(outdir: Path, summary, subtypes, outcomes, claim):
    L = ["# MMRF usefulness report", "",
         f"- Patients reclassified by omics: **{summary['n_reclassified_by_omics']}** "
         f"(up {summary['n_reclassified_up']} / down {summary['n_reclassified_down']})",
         f"- Clinically standard-risk but molecularly HIGH: **{summary['n_clinical_standard_but_molecular_high']}**",
         f"- Cytogenetic high-risk but molecularly LOWER: "
         f"**{summary['n_cytogenetic_highrisk_but_molecular_lower']}/{summary['n_cytogenetic_highrisk_total']}**",
         "", "## Did reclassified groups have different outcomes?", "",
         "| Group | n | events | event-rate@horizon | median OS | log-rank p | HR vs rest |",
         "|---|---|---|---|---|---|---|"]
    for _, r in outcomes.iterrows():
        L.append(f"| {r['group']} | {r['n_patients']} | {r['n_events']} | {r['event_rate_by_horizon']} | "
                 f"{r['median_survival_months']} | {r['logrank_p_vs_rest']} | {r['hazard_ratio_vs_rest']} |")
    L += ["", "## Which cytogenetic subtypes showed possible gain (event-gated)?", "",
          "| Subtype | n | events | Δ C-index | evidence_level |", "|---|---|---|---|---|"]
    for _, r in subtypes.iterrows():
        dl = f"{r['delta_cindex']:+.3f}" if pd.notna(r['delta_cindex']) else "—"
        L.append(f"| {r['subtype']} | {r['n_patients']} | {r['n_events']} | {dl} | {r['evidence_level']} |")
    L += ["", "## What can / cannot be claimed?",
          f"- technical validation: **{_yn(claim['technical_validation_claim_allowed'])}**; "
          f"relapse/PFS: **{_yn(claim['relapse_or_pfs_claim_allowed'])}**; "
          f"omics increment: **{claim['omics_increment_summary']}**.",
          "- Subtype results suggest possible omics benefit (notably amp1q, t(4;14)) but event counts "
          "are too small for confirmatory subtype claims."]
    (outdir / "mmrf_usefulness_report.md").write_text("\n".join(L) + "\n")


def write_experiment_summary(outdir: Path, ep, detail, claim, summary):
    L = [f"# Experiment summary — {ep.get('name')}", "",
         f"Matched N={detail['matched_n']}, test events={detail['test_events']}, "
         f"analysis={detail['analysis_type']}.", "",
         f"Clinical C={detail['clinical_cindex']:.3f} → clinical+cyto+omics C={detail['full_cindex']:.3f}; "
         f"omics increment **{claim['omics_increment_summary']}** (evidence_level "
         f"{claim['evidence_level_for_omics_increment']}).", "",
         "Hypothesis-generating evidence of molecular residual signal on OS; NOT confirmatory. "
         f"{summary['n_reclassified_by_omics']} patients reclassified; outcome-validated in "
         "mmrf_reclassification_outcomes.csv. See claim_card.md / data_card.md / model_card.md."]
    (outdir / "experiment_summary.md").write_text("\n".join(L) + "\n")
