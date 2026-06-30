# Benchmark status

Endpoint for all rows: **open-GDC overall survival (OS)**. Comparators with a
different intended endpoint (relapse/PFS) are flagged — OS results are never a
relapse/PFS claim.

| Comparator | Status | Endpoint match | Notes |
|---|---|---|---|
| **Proposed residual-risk model** | **runnable** | OS (native) | clinical + molecular-residual decomposition; primary model of this repo |
| Clinical / +cyto / +omics Cox | runnable | OS (native) | matched-cohort ablation |
| **mmSYGNAL weights** | **runnable on valid 141-program input** | relapse/PFS (native) | caret/glmnet models; validated on upstream 3-patient example |
| **mmSYGNAL same-cohort comparison** | **completed (method-reproduced)** | OS (off-endpoint) | program activity built via official miner3; mmSYGNAL OS C≈0.59–0.62 vs clinical 0.72 / clinical+omics 0.78 |
| MyeVAE | literature / reproducibility comparator | OS/PFS (paper) | published VAE survival model; not reproduced here (no open weights); cite, do not fabricate |
| Ferle progression model | endpoint-different literature comparator | PFS/relapse (paper) | PH-free log-rank progression model; OS comparison not endpoint-matched |

## mmSYGNAL same-cohort comparison — current state
Program activity generated via the **official miner3 pipeline** (`miner.correct_batch_effects`
+ `generateRegulonActivity`, exactly as `bin/miner3-survival`); output distribution
(mean 0.20, balanced {-1,0,1}) matches the upstream 3-patient example (mean 0.24). It is
**method-reproduced, not bit-validated** against the upstream IA12 reference, so the
comparison is an **OS-discrimination research benchmark only** — mmSYGNAL targets relapse/PFS,
gets no home-field advantage, and this is not a relapse/PFS claim for either model.

Result (same 182 OS test patients, mmSYGNAL pretrained, no refit):

| Model | OS C-index |
|---|---|
| clinical | 0.723 |
| clinical+cytogenetics | 0.735 |
| clinical+omics | **0.783** |
| clinical+cytogenetics+omics | 0.781 |
| mmSYGNAL agnostic | 0.618 |
| mmSYGNAL selected subtype | 0.586 |
| clinical + mmSYGNAL selected | 0.725 |
| clinical+cytogenetics + mmSYGNAL selected | 0.738 |

On OS, mmSYGNAL's relapse signal transfers weakly (C≈0.59–0.62) and adds ~nothing over
clinical; the proposed clinical+omics is strongest. This is **expected off-endpoint behaviour**
and is NOT evidence about mmSYGNAL's intended PFS/relapse performance. The builder fails
closed on a degenerate matrix (would revert this row to BLOCKED).

## Rules (enforced)
- Same patients, same OS endpoint, same train/test split for fitted comparators.
- mmSYGNAL pretrained scores used with no refitting.
- No relapse/PFS or clinical-use claim on OS data.
- Off-endpoint comparators (mmSYGNAL, Ferle) labelled; OS C-index not ranked against
  PFS/relapse metrics without warning.
