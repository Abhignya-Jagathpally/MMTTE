# Benchmark — MMRF-CoMMpass OS (real GDC open data)

Endpoint: overall survival (months). Patient-disjoint hash split (seed 42). Same Harrell C-index + 500x test bootstrap CI for all rows.

| Model | Test C-index | 95% CI | N test | Events |
|---|---|---|---|---|
| Cox: clinical | 0.850 | 0.764–0.923 | 148 | 19 |
| Cox: clinical+cyto | 0.816 | 0.713–0.898 | 148 | 19 |
| Cox: clinical+cyto+omics | 0.812 | 0.725–0.893 | 148 | 19 |
| Weibull-AFT: full (classical) | 0.810 | 0.723–0.893 | 148 | 19 |
| Neural aft (repo, full features) | 0.782 | 0.658–0.885 | 148 | 19 |
| Neural fht (repo, full features) | 0.780 | 0.657–0.892 | 148 | 19 |
| Neural cox (repo, full features) | 0.774 | 0.660–0.884 | 148 | 19 |
| Neural opsd_cox (repo, full features) | 0.772 | 0.648–0.884 | 148 | 19 |
| Cox: omics(PCs) | 0.666 | 0.556–0.785 | 148 | 19 |
| Subtype-only Cox (mmSYGNAL-style) | 0.499 | 0.340–0.657 | 148 | 19 |
| Neural opsd_fht (repo, full features) | 0.494 | 0.369–0.624 | 148 | 19 |
| Neural opsd_aft (repo, full features) | 0.478 | 0.355–0.589 | 148 | 19 |
| Neural subtype_event_rate (repo, full features) | 0.473 | 0.309–0.635 | 148 | 19 |

Notes:
- OS only; PFS not in GDC open clinical so it is not benchmarked here.
- Cytogenetics are CNV-derived (amp1q/del1p/del13q/del17p/hyperdiploid); translocations are expression surrogates, not FISH.
- 'mmSYGNAL-style' = cytogenetic subtype-only model, NOT the published mmSYGNAL regulon programs (not available open-access).
- MyeVAE-style not reproduced (requires published architecture/weights); omics(PCs) Cox is the closest open analog.
- Wide CIs reflect the small held-out test set; no SOTA claim is made.
