# Subtype-label validation — consolidated claim card

**Question:** are the sequencing-inferred subtype labels trustworthy? No FISH
exists for the open CoMMpass cohort (MMRF seqFISH is controlled-access), so trust
is established with a layered open-data stack. Nothing here is synthetic.

## 1. External real-FISH (GSE6477)
del(13) and hyperdiploidy validated against genuine interphase FISH (expression-only array; cross-platform caveat).
| subtype | auc | sens | spec | kappa |
| --- | --- | --- | --- | --- |
| del13q | 0.846 | 0.770 | 0.861 | 0.632 |
| hyperdiploid | 0.730 | 0.657 | 0.739 | 0.396 |

## 2. External cluster concordance (GSE19784, NOT FISH)
translocation surrogates vs the published expression cluster.
| subtype | auc | kappa |
| --- | --- | --- |
| t_11_14 | 0.942 | 0.702 |
| t_4_14 | 0.991 | 0.764 |
| t_14_16 | 0.489 | 0.134 |

## 3. Internal cross-modality concordance (CoMMpass, NOT FISH)
CNV calls vs orthogonal RNA dosage.
| subtype | auc | pointbiserial_r | kappa |
| --- | --- | --- | --- |
| del17p | 0.557 | 0.071 | 0.077 |
| amp1q | 0.771 | 0.454 | 0.407 |
| del13q | 0.753 | 0.432 | 0.377 |
| del1p | 0.447 | -0.058 | 0.003 |
| hyperdiploid | 0.536 | 0.067 | 0.038 |

## 4. Label-noise robustness
ROBUST: under realistic label noise, pooled penalised Cox remains no worse than subtype-specific modelling -> the subtype-aware NULL is not a label-noise artifact.

## 5. FISH-ready harness
INERT — no CoMMpass FISH file supplied. Drop a controlled-access MMRF seqFISH file into paths.fish to compute genuine sens/spec/kappa.

## Residual limitation (stated plainly)
CoMMpass calls are NOT validated against CoMMpass FISH. del(17p)/amp(1q)/del(1p)
have no open FISH and rest on the literature concordance table
(docs/literature_cnv_fish_concordance.md). Strongest support: del(13) (external
FISH + internal); weakest: del(1p), and t(14;16) (surrogate fails the cluster
check). Claims are scoped accordingly; translocations remain exploratory.
