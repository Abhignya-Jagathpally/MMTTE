# MM-TTE-OPSD

Clean repo for **cytogenetic subtype-aware time-to-event modeling in multiple myeloma**.

The repo implements:

- Cox proportional hazards neural baseline.
- Log-normal accelerated failure time model.
- Inverse-Gaussian first-hitting-time model.
- On-policy self-distillation (OPSD) variants for Cox, AFT, and FHT.
- Cytogenetic subtype-aware evaluation: `amp1q`, `del1p`, `del13q`, `del17p`, `t_4_14`, `t_11_14`, `hyperdiploid` by default.
- Data audit gates to decide whether a dataset is usable for survival/TTE, subtype TTE, or multi-omic TTE.
- Seurat pseudobulk and PLINK QC templates for real-data extension.

## Why this repo is intentionally narrower than ResistanceMap

The v12 branch is scientifically honest that it supports cell-line IC50 screening, not patient-level relapse/TTE forecasting. The v20/v19 line adds a better patient-survival-proxy pathway, but true longitudinal resistance-state modeling remains blocked unless real pre-event molecular follow-up snapshots are joined. This repo therefore claims only **TTE risk modeling** unless the data audit proves longitudinal molecular states exist.

## Quick start

```bash
cd mm_tte_opisd
python -m venv .venv
source .venv/bin/activate
pip install -e .

python -m mm_tte_survival.cli make-demo-data --out data/demo
python -m mm_tte_survival.cli audit-data \
  --clinical data/demo/clinical.csv \
  --cytogenetics data/demo/cytogenetics.csv \
  --omics data/demo/omics.csv \
  --out outputs/demo_audit.json
python -m mm_tte_survival.cli run-experiments --config configs/default.yaml
```

Or:

```bash
bash scripts/run_all.sh
```

## Configs

- `configs/default.yaml`: fast smoke-test configuration.
- `configs/real_training.yaml`: heavier real-data configuration; update paths after data access and audit.

## Expected outputs

- `outputs/demo_audit.json` and `.md`: data usability gates.
- `outputs/demo_run/leaderboard.csv`: model comparison on the same split.
- `outputs/demo_run/per_subtype_metrics.csv`: cytogenetic subgroup results.
- `outputs/demo_run/test_predictions.csv`: patient-level held-out predictions.
- `outputs/demo_run/model_*.pt`: trained PyTorch checkpoints.
- `outputs/demo_run/run_manifest.json`: split/event/feature manifest.

## Required real-data schema

Clinical survival table:

```text
patient_id,time_months,event,split,age,sex_M,iss_2,iss_3,riss_2,riss_3,line_of_therapy
```

Cytogenetic table:

```text
patient_id,amp1q,del1p,del13q,del17p,t_4_14,t_11_14,hyperdiploid
```

Omics/program table:

```text
patient_id,feature_1,feature_2,...
```

For mmSYGNAL/MINER, use program activities as the omics table, e.g. `program_0` through `program_140`.

## Scientific guardrails

1. **Do not call TT2L direct relapse**. It is a proxy endpoint unless independently validated against relapse/progression labels.
2. **Do not call first-hitting-time models molecular trajectory models** unless repeated molecular states exist before event/censoring.
3. **Do not claim SOTA from a demo run**. Use external validation, fixed splits, bootstrap CIs, leakage audit, and same-endpoint comparisons.
4. **Do not compare incompatible metrics**. C-index, F1, MMD, enrichment p-values, and PFS hazard ratios answer different questions.

## Real-data extension plan

1. Pull CoMMpass/GDC open RNA + clinical tables where allowed.
2. Add MMRF VLab/dbGaP controlled longitudinal molecular snapshots when authorized.
3. Generate mmSYGNAL program activity or MOFA factors.
4. Export single-cell pseudobulk features with `scripts/seurat/pseudobulk_mm.R` only after patient/time/event linkage is confirmed.
5. Run this repo’s audit and then experiments.
6. Promote a claim only if it passes patient-disjoint external validation.
