# Experiment 0 — open-GDC OS benchmark (frozen, v0.7)

Tag: `v0.7-mmsygnal-comparison`. Matched cohort N=726 (all modalities), held-out
test 182 patients / 38 events, stratified-by-event split, train-only preprocessing.

## Exact interpretation (the only claims this run licenses)
- The proposed **clinical+omics residual-risk model is strongest on open-GDC OS**.
- **mmSYGNAL was successfully scored** using official miner3-derived 141-program
  activity (method-reproduced; see `mmSYGNAL_method_reproduction.md`).
- **mmSYGNAL underperforms on OS** (C≈0.59–0.62), which is **expected because it is
  a relapse/PFS-oriented model** — this is an off-endpoint transfer check.
- This is **NOT evidence against mmSYGNAL's intended endpoint** (relapse/PFS).
- This is **NOT a relapse/PFS claim** for the proposed model. OS ≠ PFS/relapse.

## Same-cohort OS results (`sota_comparison.csv`)
| Model | Type | OS C-index |
|---|---|---|
| clinical | fitted | 0.723 |
| clinical+cytogenetics | fitted | 0.735 |
| **clinical+omics** | fitted | **0.783** |
| clinical+cytogenetics+omics | fitted | 0.781 |
| mmSYGNAL agnostic | pretrained, no refit | 0.618 |
| mmSYGNAL selected subtype | pretrained, no refit | 0.586 |
| clinical + mmSYGNAL selected | fitted | 0.725 |
| clinical+cytogenetics + mmSYGNAL selected | fitted | 0.738 |

Same 182 test patients, same OS endpoint, mmSYGNAL pretrained (no refitting).

## Publishable framing (use this; do NOT say "beat SOTA")
> We included mmSYGNAL as a public-weight, externally-trained risk comparator.
> Because mmSYGNAL is a relapse/PFS-oriented model and Experiment 0 uses OS, the
> comparison is interpreted only as **off-endpoint transfer**. Under this OS
> technical-validation setting, the proposed clinical+omics residual-risk model
> achieved higher discrimination, while mmSYGNAL added little beyond clinical risk.
> This supports the need for **endpoint-matched PFS/relapse validation** rather than
> a direct claim of superiority over mmSYGNAL.

## Claim card (`benchmark_claim_card.md`)
technical_validation: YES · primary_biological: NO · relapse/PFS: NO ·
clinical-use: NO · research benchmark: YES · evidence_level: technical_validation_only.
