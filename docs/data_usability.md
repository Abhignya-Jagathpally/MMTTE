# Data Usability Map

## Directly usable for TTE survival modeling

1. **CoMMpass / MMRF clinical + RNA expression**
   - Required join keys: `patient_id`, survival endpoint time, event indicator, cytogenetic subtype fields, expression/program activity features.
   - Valid endpoints: PFS, OS, time-to-next-treatment / time-to-second-line as proxy if named explicitly.
   - Publication-grade rule: never mix OS, PFS, and TT2L as if they are the same endpoint.

2. **mmSYGNAL/MINER program activity matrices**
   - Use as interpretable molecular features, especially 0–140 program activities.
   - Fit Cox/AFT/FHT against the same patient-disjoint survival labels.
   - Compare subtype-specific models for amp(1q), del(13), del(1p), t(4;14), FGFR3, and agnostic setting.

3. **MMRF ImmuneAtlas / single-cell atlas features**
   - Use only after patient-level TTE labels and baseline/follow-up timing are available.
   - Pseudobulk per patient/timepoint or cell-composition signatures can become covariates.
   - Do not treat pseudotime as clinical event time.

## Not directly usable for TTE without labels

1. **SEGPC/PCMMD/MMDB plasma-cell images**
   - Useful for morphology feature extraction and diagnosis/classification.
   - Not sufficient for relapse/TTE unless image-level samples are linked to patient survival outcomes.

2. **Synthetic hematological malignancy datasets**
   - Useful for software smoke tests or fairness stress tests.
   - Not valid for SOTA claims.

3. **Cell-line drug screens**
   - Useful for drug-sensitivity pretraining and mechanism priors.
   - Not a direct endpoint for patient relapse/TTE.

## Minimum gates used by this repo

- ≥50 patients and ≥20 events for software-level survival experiments.
- Prefer ≥200 patients and ≥60 events for serious global modeling.
- For subtype-specific claims: report only subtypes with enough test patients/events; otherwise mark `too_sparse`.
- All imputation, scaling, PCA, cutpoint selection, and feature selection must be fit on training data only.
- Patient-disjoint splits are mandatory; sample-disjoint splits are insufficient if multiple samples per patient exist.

## Experiment 0 result (open-GDC OS, matched cohort) — framing

The earlier *unmatched* OS result suggested omics did not help. After enforcing a
matched-cohort comparison across all modalities, clinical+omics improved the
point-estimate C-index from 0.736 to 0.782 (improving in 94% of 50 repeated
stratified splits; NRI ≈ 0.40). Confidence intervals overlap and the endpoint
remains OS, so the finding supports a hypothesis of molecular residual signal but
does **not** confirm omics utility for relapse/PFS prediction. See
`docs/experiment0_framing.md`, `docs/mmrf_community_value.md`, and
`docs/pfs_data_acquisition_plan.md`. Claims are endpoint-gated in code: an OS run
cannot license a relapse/PFS claim.
