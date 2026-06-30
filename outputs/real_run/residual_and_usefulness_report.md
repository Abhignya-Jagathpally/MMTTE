# Experiment 0 — open_gdc_os (overall_survival): matched-cohort technical-validation & residual-risk pilot

analysis_type **scientific_matched_cohort** · matched N=726 · test events=38.

> Headline: omics moved held-out C from 0.736 (clinical) to 0.776 (clinical+cyto+omics). Paired ΔC CI overlaps 0 and the endpoint is OS ⇒ **hypothesis-generating evidence of molecular residual signal, not confirmatory.**

## [1] Endpoint-gated claim report

- technical_validation_claim_allowed: **YES**
- primary_biological_claim_allowed: **NO**
- relapse_or_pfs_claim_allowed: **NO**
- omics_increment_confirmed: **NO** (SUGGESTIVE_NOT_CONFIRMED)
- external_validation_available: **NO**
- evidence_level: **technical_validation_only**

## [3] Matched-cohort ablation

| Feature set | #feat | Test C | 95% CI |
|---|---|---|---|
| clinical | 5 | 0.736 | 0.648–0.821 |
| clinical+cytogenetics | 12 | 0.729 | 0.663–0.796 |
| clinical+omics | 21 | 0.782 | 0.714–0.842 |
| clinical+cytogenetics+omics | 28 | 0.776 | 0.713–0.834 |
| clinical+programs | 15 | 0.764 | 0.665–0.836 |
| clinical+cytogenetics+programs | 22 | 0.757 | 0.669–0.829 |

## [2] Paired ΔC-index (same test patients)

| Comparison | ΔC | ΔCI low | ΔCI high | p_boot | claim |
|---|---|---|---|---|---|
| clinical+omics_vs_clinical | +0.047 | -0.038 | +0.137 | 0.1485 | hypothesis_generating_improvement |
| clinical+cyto+omics_vs_clinical | +0.040 | -0.052 | +0.132 | 0.207 | hypothesis_generating_improvement |
| clinical+cyto+omics_vs_clinical+cyto | +0.047 | -0.017 | +0.115 | 0.075 | hypothesis_generating_improvement |
| clinical+programs_vs_clinical | +0.028 | -0.074 | +0.132 | 0.301 | hypothesis_generating_improvement |
| clinical+cyto+programs_vs_clinical+cyto | +0.029 | -0.048 | +0.101 | 0.2295 | hypothesis_generating_improvement |
| residual_total_vs_clinical | +0.040 | -0.054 | +0.133 | 0.213 | hypothesis_generating_improvement |

Residual decomposition held-out C — clinical **0.735**, molecular_residual **0.650**, total **0.775** (clinical coef in joint 1.025 ≈ 1 ⇒ clean offset).

## Repeated stratified-split validation

| Feature set | splits | mean C | sd | 95% CI |
|---|---|---|---|---|
| clinical+omics | 50 | 0.730 | 0.038 | 0.670–0.790 |
| clinical+cytogenetics+omics | 50 | 0.724 | 0.039 | 0.653–0.791 |
| clinical+cytogenetics | 50 | 0.684 | 0.033 | 0.609–0.733 |
| clinical | 50 | 0.661 | 0.039 | 0.597–0.730 |

| Δ comparison | mean Δ | 95% CI | frac improved |
|---|---|---|---|
| clinical+omics_vs_clinical | +0.069 | -0.015–+0.152 | 0.94 |
| clinical+cyto+omics_vs_clinical | +0.063 | -0.024–+0.146 | 0.94 |

## [7] Reclassification OUTCOME validation

| Group | n | events | event-rate@h | median OS | log-rank p | HR vs rest |
|---|---|---|---|---|---|---|
| clinical_low__molecular_low | 186 | 10 | 0.0414 | not_reached | 0.0 | 0.197 |
| clinical_low__molecular_high | 177 | 26 | 0.1414 | not_reached | 0.0612 | 0.67 |
| clinical_high__molecular_low | 177 | 42 | 0.1775 | not_reached | 0.9392 | 0.986 |
| clinical_high__molecular_high | 186 | 74 | 0.3498 | 37.8 | 0.0 | 3.369 |
| cyto_high__molecular_low | 101 | 18 | 0.1409 | not_reached | 0.2638 | 0.756 |
| cyto_low__molecular_high | 113 | 23 | 0.1993 | not_reached | 0.9152 | 1.024 |

## Top molecular-residual drivers (provenance-flagged)

| feature | coef | direction | kind | mapped_genes |
|---|---|---|---|---|
| PC1 | +0.282 | higher_risk | rna_pca_loading_derived | MCM6;TUBB;TFDP1;MCM3;TMPO |
| PC6 | -0.203 | lower_risk | rna_pca_loading_derived | TMEM37;RAPGEF2;ANKRD28;TGFA;FAAH2 |
| PC3 | +0.202 | higher_risk | rna_pca_loading_derived | CCND2;GNG11;KIF21B;STAP1;SPN |
| PC4 | +0.139 | higher_risk | rna_pca_loading_derived | HCK;LST1;P2RY13;HK3;MNDA |
| PC14 | +0.136 | higher_risk | rna_pca_loading_derived | FOSB;DUSP1;PTGS2;NR4A2;RGS2 |
| PC8 | +0.127 | higher_risk | rna_pca_loading_derived | HERC6;MAF;STXBP6;STAT4;TACC1 |
| amp1q | +0.106 | higher_risk | cytogenetic_call |  |
| PC10 | -0.102 | lower_risk | rna_pca_loading_derived | CITED2;SLC17A9;QPRT;CERCAM;RBP1 |
| PC7 | -0.095 | lower_risk | rna_pca_loading_derived | CD200;BTLA;NRG3;MGLL;LYPD6B |
| PC11 | +0.087 | higher_risk | rna_pca_loading_derived | FRMD6;PLEKHO1;RAMP2;WNT10A;PLEK |

_RNA drivers are PC-loading-derived, NOT direct gene-level causal features._
