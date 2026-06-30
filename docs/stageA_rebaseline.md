# Stage A — leak-proof OS re-baseline (Gate 2)

Honest Experiment-0 re-baseline with **train-fold PCA**. Endpoint = OS technical
validation only (no relapse/PFS or clinical-use claims). Run: `mm-tte rebaseline`.

## What changed vs the prior baseline
- **Omics PCA is fit inside each train fold** (`OmicsInFoldPCA`: top-variable-gene
  selection + scaling + PCA all on train rows only), proven per fold in
  `pca_fit_manifest.csv` (`test_rows_in_fit=0`, `train_test_patient_overlap=0`).
- **Patient-disjoint, event-stratified** splits (`patient_disjoint_stratified_split`).
- **IPCW-IBS** (sksurv) replaces the old `risk_event_proxy` mis-labelled as IBS.
- Executable leakage audit -> `leakproof_leakage_audit.json` (fails loud).

## Subtype-label provenance (CNV-only primary)
Primary HSS membership uses CNV-derived calls only — `amp1q, del1p, del13q,
del17p, hyperdiploid` (`cohort.CNV_SUBTYPES`). The three translocation labels
`t_4_14, t_11_14, t_14_16` are **RNA-expression surrogates thresholded on
full-cohort quantiles** (`build_omics.py`), a mild label leak, so they are
**excluded from primary** analysis and kept only as a labeled sensitivity check.

## Legacy / diagnostic
`omics.csv` (precomputed full-cohort PCs) is **legacy/diagnostic only** — retained
purely to quantify the leak delta, never as primary evidence.

## Result (5 patient-disjoint folds, N=726, 152 events; primary k=16)
- Honest C-index: clinical **0.688**, clinical+omics(in-fold) **0.754**,
  clinical+cyto+omics(in-fold) **0.747**; IBS clinical 0.140 -> +omics 0.126.
- **Leak optimism is negligible**: +0.0014 C at k=16, and it *reverses*
  (in-fold better) at k=32/64. The omics increment survives the leak fix.
- Pre-registered width sweep k∈{8,16,32,64}: k=8–16 optimal; k=64 overfits.

## Artifacts (`outputs/rebaseline_open_gdc_os/`)
`leakproof_leaderboard.csv`, `leakproof_paired_delta_cindex.csv`,
`leakproof_calibration.csv`, `leakproof_ipcw_ibs.csv`,
`leakproof_leakage_audit.json`, `pca_fit_manifest.csv`,
`leak_delta_summary.md`, `stageA_claim_card.md`.
