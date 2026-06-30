# Process / Reporting Compliance Matrix

This is a code-facing process checklist for transparent clinical/statistical ML. It is not a manuscript.

| Requirement | How reflected in code |
|---|---|
| Define endpoint before modeling | Config separates `time_col` and `event_col`; docs prohibit mixing PFS/OS/TT2L. |
| Patient-disjoint validation | Hash-based split by `patient_id`; accepts external frozen split column. |
| Avoid preprocessing leakage | PCA, imputation, and scaling are fit on train rows only. |
| Report censoring and events | Audit and manifest report patient/event counts by split. |
| Baselines before novelty | Subtype-only, Cox, AFT, FHT, and OPSD variants run from same interface. |
| Subgroup transparency | Per-cytogenetic-subtype metrics are output with sparsity flags. |
| Reproducibility | Config, random seed, model checkpoints, predictions, history, leaderboard, and audit files are persisted. |
| No overclaiming | v12/v20 audit and model docs distinguish TT2L proxy, true relapse, and longitudinal trajectory claims. |
