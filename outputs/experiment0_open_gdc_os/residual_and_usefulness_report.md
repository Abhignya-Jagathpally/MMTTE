# Experiment 0 — open_gdc_os (overall_survival): matched-cohort technical-validation & residual-risk pilot

analysis_type **scientific_matched_cohort** · matched N=726 · test events=38.

> Headline: omics moved held-out C from 0.658 (clinical) to 0.727 (clinical+cyto+omics). Paired ΔC CI overlaps 0 and the endpoint is OS ⇒ **hypothesis-generating evidence of molecular residual signal, not confirmatory.**

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
| clinical | 7 | 0.658 | 0.569–0.759 |
| clinical+cytogenetics | 15 | 0.692 | 0.610–0.781 |
| clinical+omics | 23 | 0.734 | 0.642–0.825 |
| clinical+cytogenetics+omics | 31 | 0.727 | 0.629–0.821 |
| clinical+programs | 17 | 0.722 | 0.633–0.815 |
| clinical+cytogenetics+programs | 25 | 0.723 | 0.631–0.819 |

## [2] Paired ΔC-index (same test patients)

| Comparison | ΔC | ΔCI low | ΔCI high | p_boot | claim |
|---|---|---|---|---|---|
| clinical+omics_vs_clinical | +0.076 | -0.020 | +0.164 | 0.061 | hypothesis_generating_improvement |
| clinical+cyto+omics_vs_clinical | +0.069 | -0.033 | +0.165 | 0.0885 | hypothesis_generating_improvement |
| clinical+cyto+omics_vs_clinical+cyto | +0.035 | -0.027 | +0.096 | 0.1245 | hypothesis_generating_improvement |
| clinical+programs_vs_clinical | +0.064 | -0.027 | +0.155 | 0.097 | hypothesis_generating_improvement |
| clinical+cyto+programs_vs_clinical+cyto | +0.031 | -0.024 | +0.087 | 0.1475 | hypothesis_generating_improvement |
| residual_total_vs_clinical | +0.079 | -0.025 | +0.178 | 0.068 | hypothesis_generating_improvement |

Residual decomposition held-out C — clinical **0.659**, molecular_residual **0.638**, total **0.737** (clinical coef in joint 1.000 ≈ 1 ⇒ clean offset).

## Repeated stratified-split validation

| Feature set | splits | mean C | sd | 95% CI |
|---|---|---|---|---|
| clinical+omics | 50 | 0.744 | 0.035 | 0.686–0.814 |
| clinical+cytogenetics+omics | 50 | 0.739 | 0.034 | 0.686–0.806 |
| clinical+cytogenetics | 50 | 0.705 | 0.035 | 0.653–0.768 |
| clinical | 50 | 0.689 | 0.039 | 0.627–0.765 |

| Δ comparison | mean Δ | 95% CI | frac improved |
|---|---|---|---|
| clinical+omics_vs_clinical | +0.055 | -0.021–+0.117 | 0.96 |
| clinical+cyto+omics_vs_clinical | +0.050 | -0.037–+0.115 | 0.90 |

## [7] Reclassification OUTCOME validation

| Group | n | events | event-rate@h | median OS | log-rank p | HR vs rest |
|---|---|---|---|---|---|---|
| clinical_low__molecular_low | 175 | 7 | 0.0223 | not_reached | 0.0 | 0.134 |
| clinical_low__molecular_high | 188 | 24 | 0.1188 | not_reached | 0.0178 | 0.593 |
| clinical_high__molecular_low | 188 | 42 | 0.17 | 57.6 | 0.7222 | 0.937 |
| clinical_high__molecular_high | 175 | 79 | 0.4025 | 32.3 | 0.0 | 4.2 |
| cyto_high__molecular_low | 107 | 19 | 0.1507 | not_reached | 0.282 | 0.768 |
| cyto_low__molecular_high | 106 | 23 | 0.247 | not_reached | 0.3307 | 1.246 |

## Top molecular-residual drivers (provenance-flagged)

| feature | coef | direction | kind | mapped_genes |
|---|---|---|---|---|
| PC1 | +0.278 | higher_risk | rna_pca_loading_derived | MCM6;TUBB;TFDP1;MCM3;TMPO |
| PC6 | -0.208 | lower_risk | rna_pca_loading_derived | TMEM37;RAPGEF2;ANKRD28;TGFA;FAAH2 |
| PC3 | +0.186 | higher_risk | rna_pca_loading_derived | CCND2;GNG11;KIF21B;STAP1;SPN |
| PC7 | -0.124 | lower_risk | rna_pca_loading_derived | CD200;BTLA;NRG3;MGLL;LYPD6B |
| PC12 | -0.115 | lower_risk | rna_pca_loading_derived | XAF1;IFIT3;IFI6;SDC3;FABP5 |
| PC8 | +0.108 | higher_risk | rna_pca_loading_derived | HERC6;MAF;STXBP6;STAT4;TACC1 |
| PC15 | +0.098 | higher_risk | rna_pca_loading_derived | RASA3;F12;DUSP4;TNFRSF18;NEIL1 |
| del1p | +0.090 | higher_risk | cytogenetic_call |  |
| PC13 | +0.089 | higher_risk | rna_pca_loading_derived | PARP9;AXL;CCL8;PLA2G7;SIGLEC1 |
| amp1q | +0.088 | higher_risk | cytogenetic_call |  |

_RNA drivers are PC-loading-derived, NOT direct gene-level causal features._
