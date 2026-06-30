# Experiment 0 — open_gdc_os (overall_survival): matched-cohort technical-validation & residual-risk pilot

analysis_type **scientific_matched_cohort** · matched N=726 · test events=38.

> Headline: omics moved held-out C from 0.723 (clinical) to 0.781 (clinical+cyto+omics). Paired ΔC CI overlaps 0 and the endpoint is OS ⇒ **hypothesis-generating evidence of molecular residual signal, not confirmatory.**

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
| clinical | 7 | 0.723 | 0.632–0.814 |
| clinical+cytogenetics | 15 | 0.735 | 0.657–0.808 |
| clinical+omics | 23 | 0.783 | 0.712–0.844 |
| clinical+cytogenetics+omics | 31 | 0.781 | 0.714–0.836 |
| clinical+programs | 17 | 0.770 | 0.682–0.845 |
| clinical+cytogenetics+programs | 25 | 0.766 | 0.680–0.840 |

## [2] Paired ΔC-index (same test patients)

| Comparison | ΔC | ΔCI low | ΔCI high | p_boot | claim |
|---|---|---|---|---|---|
| clinical+omics_vs_clinical | +0.060 | -0.010 | +0.136 | 0.0555 | hypothesis_generating_improvement |
| clinical+cyto+omics_vs_clinical | +0.058 | -0.022 | +0.142 | 0.0785 | hypothesis_generating_improvement |
| clinical+cyto+omics_vs_clinical+cyto | +0.046 | -0.013 | +0.105 | 0.0625 | hypothesis_generating_improvement |
| clinical+programs_vs_clinical | +0.047 | -0.034 | +0.133 | 0.1375 | hypothesis_generating_improvement |
| clinical+cyto+programs_vs_clinical+cyto | +0.031 | -0.037 | +0.097 | 0.186 | hypothesis_generating_improvement |
| residual_total_vs_clinical | +0.061 | -0.019 | +0.146 | 0.067 | hypothesis_generating_improvement |

Residual decomposition held-out C — clinical **0.723**, molecular_residual **0.655**, total **0.784** (clinical coef in joint 0.885 ≈ 1 ⇒ clean offset).

## Repeated stratified-split validation

| Feature set | splits | mean C | sd | 95% CI |
|---|---|---|---|---|
| clinical+omics | 50 | 0.733 | 0.038 | 0.666–0.802 |
| clinical+cytogenetics+omics | 50 | 0.730 | 0.037 | 0.661–0.794 |
| clinical+cytogenetics | 50 | 0.697 | 0.034 | 0.623–0.748 |
| clinical | 50 | 0.673 | 0.042 | 0.587–0.737 |

| Δ comparison | mean Δ | 95% CI | frac improved |
|---|---|---|---|
| clinical+omics_vs_clinical | +0.059 | -0.027–+0.136 | 0.94 |
| clinical+cyto+omics_vs_clinical | +0.057 | -0.036–+0.134 | 0.92 |

## [7] Reclassification OUTCOME validation

| Group | n | events | event-rate@h | median OS | log-rank p | HR vs rest |
|---|---|---|---|---|---|---|
| clinical_low__molecular_low | 183 | 8 | 0.03 | not_reached | 0.0 | 0.151 |
| clinical_low__molecular_high | 180 | 24 | 0.12 | not_reached | 0.0174 | 0.592 |
| clinical_high__molecular_low | 180 | 44 | 0.198 | 57.6 | 0.5465 | 1.114 |
| clinical_high__molecular_high | 183 | 76 | 0.3553 | 37.8 | 0.0 | 3.523 |
| cyto_high__molecular_low | 116 | 21 | 0.1548 | not_reached | 0.4008 | 0.821 |
| cyto_low__molecular_high | 115 | 22 | 0.1791 | not_reached | 0.8884 | 0.968 |

## Top molecular-residual drivers (provenance-flagged)

| feature | coef | direction | kind | mapped_genes |
|---|---|---|---|---|
| PC1 | +0.295 | higher_risk | rna_pca_loading_derived | MCM6;TUBB;TFDP1;MCM3;TMPO |
| PC6 | -0.195 | lower_risk | rna_pca_loading_derived | TMEM37;RAPGEF2;ANKRD28;TGFA;FAAH2 |
| PC3 | +0.168 | higher_risk | rna_pca_loading_derived | CCND2;GNG11;KIF21B;STAP1;SPN |
| PC14 | +0.138 | higher_risk | rna_pca_loading_derived | FOSB;DUSP1;PTGS2;NR4A2;RGS2 |
| PC4 | +0.122 | higher_risk | rna_pca_loading_derived | HCK;LST1;P2RY13;HK3;MNDA |
| PC8 | +0.117 | higher_risk | rna_pca_loading_derived | HERC6;MAF;STXBP6;STAT4;TACC1 |
| PC11 | +0.109 | higher_risk | rna_pca_loading_derived | FRMD6;PLEKHO1;RAMP2;WNT10A;PLEK |
| PC10 | -0.087 | lower_risk | rna_pca_loading_derived | CITED2;SLC17A9;QPRT;CERCAM;RBP1 |
| PC7 | -0.087 | lower_risk | rna_pca_loading_derived | CD200;BTLA;NRG3;MGLL;LYPD6B |
| amp1q | +0.084 | higher_risk | cytogenetic_call |  |

_RNA drivers are PC-loading-derived, NOT direct gene-level causal features._
