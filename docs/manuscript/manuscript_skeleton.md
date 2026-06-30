# Manuscript skeleton (Experiment 0, v0.7)

**Working title:** Clinically Anchored Molecular Residual-Risk Modeling in Multiple
Myeloma: An Endpoint-Gated Open-Data Benchmark
*(alt: Endpoint-Gated Molecular Residual-Risk Modeling for Multiple Myeloma Survival
Stratification)*

**Claim discipline:** OS technical-validation + hypothesis-generating only. No
relapse/PFS or clinical-use claims. mmSYGNAL is an off-endpoint comparator.

---
## Abstract (structured, ~250 words)
- **Background:** molecular features may add progression-risk information beyond
  clinical disease burden in MM, but open data carries OS (not PFS/relapse), and
  modality comparisons are often unmatched and over-claimed.
- **Methods:** open GDC MMRF-CoMMpass; matched cohort (N=726, all modalities);
  clinical + CNV-derived cytogenetics + RNA-seq (PCA omics and official
  miner3/mmSYGNAL 141-program activity). Residual-risk decomposition (clinical Cox +
  molecular-residual Cox; total = clinical + residual). Endpoint-gated claim engine.
- **Results:** clinical+omics best on OS (held-out C 0.783; improves in 94% of 50
  splits; NRI 0.40); molecular residual re-stratifies within clinical strata
  (clinical-low/molecular-high OS event-rate 0.14 vs 0.04). mmSYGNAL, scored via
  official miner3 program activity, transfers weakly to OS (C 0.59–0.62) — expected
  for a relapse/PFS model.
- **Conclusions:** a reproducible, endpoint-gated framework; molecular residual signal
  is hypothesis-generating on OS and motivates endpoint-correct PFS/relapse validation.

## 1. Introduction
- MM risk: ISS/R-ISS, cytogenetics (del17p, t(4;14), amp1q), GEP70/SKY92; molecular
  programs (mmSYGNAL/MINER).
- Gap 1: open data = OS, not relapse/PFS → overclaiming risk.
- Gap 2: unmatched modality comparisons are unfair.
- Gap 3: external risk models (mmSYGNAL) compared off-endpoint without flagging.
- Contribution: endpoint-gated, matched-cohort, residual-risk framework + honest
  mmSYGNAL off-endpoint integration; fully reproducible on open data.

## 2. Methods
- **Data:** GDC MMRF-CoMMpass (DR45). Clinical/OS via GDC API (N=995, 191 deaths);
  CNV-derived cytogenetics from WGS segments (genome-median-recentred arm log2;
  frequencies match literature); RNA STAR counts → log2-TPM → PCA (omics) and
  official miner3 141-program activity (see §2.4).
- **Matched cohort & split:** intersection of all modalities (N=726); stratified-by-
  event train/test; train-only impute/scale/PCA/residualization (leakage audit).
- **Residual-risk model:** clinical Cox → clinical_risk; molecular features
  orthogonalized vs clinical → residual Cox → molecular_residual_risk; total =
  clinical + residual (exactly additive; clinical coef ≈ 1).
- **2.4 mmSYGNAL program activity (official miner3):** `correct_batch_effects`
  (preProcessTPM + z-score) + `generateRegulonActivity` on program gene-sets
  (union of member-regulon genes) → {-1,0,1} per program/sample; method-reproduced,
  not bit-validated (distribution mean 0.20 matches upstream example 0.24).
- **mmSYGNAL scoring:** caret/glmnet RDS models, `predict(type="prob")$high`,
  grade-based subtype selection; pretrained, no refitting.
- **Evaluation:** Harrell C; paired ΔC bootstrap (same patients); 50 repeated splits;
  calibration/Brier; decision-curve net benefit; NRI/IDI; subtype event-gated evidence;
  reclassification outcomes (KM, log-rank, HR).
- **Endpoint claim gate:** registry maps endpoint→allowed claims; OS cannot license
  relapse/PFS or primary biological claims; CI guardrail forbids relapse/clinical-use
  language on OS runs.

## 3. Results
- **3.1 Cohort & data quality:** N=726 matched, 152 events; cytogenetic frequencies
  vs literature; program-activity validation (S3).
- **3.2 Matched OS ablation (Fig 4, Table 1):** clinical 0.723, +cyto 0.735, +omics
  **0.783**, +cyto+omics 0.781. Paired ΔC(omics vs clinical) +0.047 (CI overlaps 0);
  repeated-split mean +omics 0.730 vs clinical 0.661, improves 94% of splits.
  Calibration (omics best Brier), DCA, NRI 0.40.
- **3.3 mmSYGNAL off-endpoint comparator:** agnostic 0.618, selected 0.586; adds little
  over clinical (0.723→0.725/0.738). Off-endpoint; not a same-task ranking.
- **3.4 Molecular residual-risk reclassification (Fig 5):** 300/726 reclassified;
  clinical-low/molecular-high OS event-rate 0.14 vs 0.04; clinical-high/molecular-high
  HR 3.37 (p<1e-4). Subtype gains hypothesis-generating (event counts small).

## 4. Discussion
- Clinical burden dominates OS; molecular adds a robust-but-CI-unconfirmed increment
  and re-stratifies within clinical strata.
- mmSYGNAL result is **off-endpoint transfer**, not a superiority claim; supports the
  need for endpoint-matched PFS/relapse validation.
- **Limitations:** OS not PFS/relapse; small test events; single cohort (no external
  validation); RNA-surrogate translocations; mmSYGNAL program activity method-reproduced
  not bit-validated; RNA-PC drivers not direct causal genes.
- **Future:** controlled CoMMpass PFS/TTNT/early-progression; external validation;
  Experiment 1 (program vs PCA) and E3 (PFS) per agenda.yaml.

## Required-framing sentence (use verbatim where superiority is implied)
> We included mmSYGNAL as a public-weight, externally-trained risk comparator. Because
> mmSYGNAL is a relapse/PFS-oriented model and Experiment 0 uses OS, the comparison is
> interpreted only as off-endpoint transfer. Under this OS technical-validation setting,
> the proposed clinical+omics residual-risk model achieved higher discrimination, while
> mmSYGNAL added little beyond clinical risk. This supports the need for endpoint-matched
> PFS/relapse validation rather than a direct claim of superiority over mmSYGNAL.
