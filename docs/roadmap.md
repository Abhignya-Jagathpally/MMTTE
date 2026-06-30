# Roadmap (Phases 2–5)

## Phase 2 — Experiment 0 frozen ✅
`outputs/experiment0_open_gdc_os/` is the frozen technical-validation package
(tag `v0.4-experiment0-frozen`). Interpretation:
- **Technical validation only** (pipeline works on real GDC MMRF data).
- **Hypothesis-generating** molecular residual signal (clinical C 0.72 →
  clinical+cyto+omics 0.78; paired ΔC CI overlaps 0; improves in 94% of 50 splits).
- **No relapse/PFS claim** (endpoint is OS — hard-gated off).
- **No clinical-use claim** (research use only).

## Phase 3 — endpoint-correct data (NEXT OPERATIONAL PRIORITY) ⛔ blocked on access
The single most important next step. Open GDC OS is insufficient for the proposal's
progression/relapse target. Required per-patient fields (see
`docs/pfs_data_acquisition_plan.md`):
`patient_id, baseline_date, progression_date, relapse_date, death_date,
last_follow_up_date, treatment_start/end_dates, line_of_therapy, censoring_status,
event_definition`.
Source: **MMRF CoMMpass Researcher Gateway / dbGaP controlled access** (requires
an approved data-use application — cannot be fetched from the open GDC API).

Checklist: apply for controlled access → derive `pfs_time`/`pfs_event` →
set `endpoint.name: controlled_commpass_pfs` → wire a 2nd cohort for external
validation → re-run.

## Phase 4 — convert OS → PFS / TTNT / early-progression (config swap, ready)
The pipeline is endpoint-agnostic. Once endpoint-correct tables exist, run the
prebuilt configs (`configs/experiments/experiment1_controlled_commpass_pfs.yaml`,
`experiment2_ttnt_proxy.yaml`) across:
clinical · +cytogenetics · +omics · +cyto+omics · +program activity ·
+cyto+program activity · residual-risk · neural Cox/AFT/FHT · OPSD variants.
Primary outputs (already implemented): paired ΔC-index, calibration, Brier,
decision-curve net benefit, NRI/IDI, subtype evidence, reclassification outcomes.
On a relapse-type endpoint the claim gate opens
(`primary_biological_claim_allowed` becomes possible with omics_increment_confirmed
+ external validation).

## Phase 5 — novelty claim (only after Phase 4 confirms)
- **If PFS/relapse/TTNT confirm the OS pattern:** "Molecular residual-risk modeling
  identifies clinically under-recognized progression-risk strata in multiple
  myeloma, especially within cytogenetic subtypes, under endpoint-correct TTE
  validation."
- **If not:** "A reproducible endpoint-gated framework showing where molecular data
  does and does not add risk information beyond clinical disease-burden markers."

Both are publishable if framed honestly.
