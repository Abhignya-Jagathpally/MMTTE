# Experiment 0 — frozen scientific milestone (v0.2)

Tag: `v0.2-experiment0-os-residual-risk`

This records the **honest baseline state** before architecture polishing.

| Field | Value |
|---|---|
| Endpoint | `open_gdc_os` (overall survival) |
| Role | technical validation |
| Matched cohort | 726 patients (all modalities), 152 events total |
| Held-out test | 182 patients / 38 events (stratified-event split) |
| Clinical-only baseline | strong (single-split C 0.736; repeated-split mean 0.661) |
| Clinical + omics | hypothesis-generating improvement (single-split 0.782; repeated-split mean 0.730; improves 94% of 50 splits; paired ΔC CI overlaps 0) |
| Molecular residual alone | held-out C 0.650 (incremental signal beyond clinical) |
| Reclassification | clinical-low/molecular-high event rate 0.14 vs 0.04; clinical-high/molecular-high HR 3.37 (p<1e-4) |
| Primary biological claim | NOT allowed (endpoint is OS) |
| Relapse/PFS claim | NOT allowed (endpoint is OS) |
| Omics increment | SUGGESTIVE, NOT CONFIRMED |
| External validation | not yet available |
| Evidence level | technical_validation_only |

## What this milestone proves
- The pipeline runs end-to-end on real GDC MMRF-CoMMpass data.
- Clinical disease-burden markers (ISS, β2M, albumin, age) are strong predictors.
- Matched-cohort comparison is necessary; molecular features carry residual signal.
- OS is insufficient for relapse/PFS claims — confirmation needs a relapse-type
  endpoint + external validation.

## Reproduce this state
```bash
bash scripts/realdata/run_all_real.sh
python -m mm_tte_survival.cli residual-report --config configs/real_training.yaml
```
