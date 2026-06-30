# Framing: subtype-awareness is a pre-registered NULL

**Decision (this project):** subtype-aware survival modelling is reported as a
**pre-registered negative result**, not a contribution. The neural Hierarchical
Subtype Survival (HSS) model is **not promoted** to the canonical/main path, and no
subtype-aware headline claim is made. This document is the standing framing the
rest of the manuscript and claim register defer to.

## 1. Thesis

The contribution is a **reference-validated, leak-proof, endpoint-gated time-to-event
framework** for multiple-myeloma overall survival on open data, together with a
**cross-axis ceiling result**: neither molecular-PCA conditioning nor
cytogenetic-subtype conditioning beats a pooled penalised model. Subtype-awareness
is one falsified axis of that ceiling, reported honestly.

Concretely the durable claims are:

1. **Reference-validated survival losses.** Cox (Breslow), log-normal AFT, and
   inverse-Gaussian first-hitting-time NLLs are numerically correct against scipy
   references and stable in the censored / overflow regimes (`training/losses.py`,
   `tests/test_losses.py`).
2. **Leak-proof, endpoint-gated benchmark.** Patient-disjoint event-stratified
   splits, in-fold PCA with a fit manifest, an executable leakage audit that fails
   loud, IPCW-IBS, CNV-only primary labels, claim gating (OS cannot license
   PFS/relapse), pre-registration + negative controls.
3. **Honest model = pooled penalised Cox.** `clinical + omics(in-fold)` penalised
   Cox, C≈0.754; subtype-specific and neural variants do not beat it.
4. **Subtype-awareness is NULL** (this document).
5. **The subtype labels are validated to the extent open data allows** — external
   real FISH (GSE6477), cluster concordance (GSE19784), internal cross-modality,
   literature concordance, and demonstrated robustness to realistic label noise.

## 2. What was tested and why it is NULL

| Evidence | Result | Reference |
|---|---|---|
| Stage D negative controls (discrimination) | real ≈ permuted ≈ random → benefit is shared-trunk regularization, not subtype biology | `experiments_stageD.py`, tag `v1.1` |
| λ=0 vs λ>0 | distillation adds ~nothing | Stage D |
| Direction-2 (pooled neural vs pooled penalised Cox) | neural ≤ penalised Cox on small-subtype IBS → no neural advantage | `experiments_regularization.py` |
| **Label-noise robustness** | pooled Cox stays no-worse-than subtype-specific under realistic FISH-discordance flips (95% of draws) → **the NULL is not a label-noise artifact** | `experiments_label_noise.py` |

The label-noise result is the key addition: a reviewer can no longer dismiss the null
as "your labels are too noisy to see an effect." Even corrupting labels at published
sequencing-vs-FISH discordance rates, subtype-conditioning still fails to help.

## 3. Terminology and claim scoping (binding)

- **Call them "sequencing-inferred subtypes,"** never "FISH subtypes." CNV calls are
  copy-number-segment derived; translocations are RNA-expression surrogates.
- **Translocations stay exploratory.** t(14;16) in particular **fails** its cluster
  check (AUC 0.49) and must not anchor any claim.
- **Scope firm statements to the best-supported lesions:** del(13) (external FISH AUC
  0.85 + internal 0.75), then del(17p) (literature FISH specificity high; note
  expression does NOT corroborate it — hemizygous loss barely changes mRNA), then
  amp(1q) (internal AUC 0.77). **del(1p) is the most uncertain** (internal AUC 0.45,
  no external FISH) and is flagged as such wherever it appears.

## 4. Optional pre-registered calibration one-shot (hard stop)

A single, pre-registered test is permitted (see `mm-tte subtype-calibration`):
does subtype conditioning improve **calibration** (IPCW-IBS / D-calibration) —
distinct from the **discrimination** Stage D tested? We hold the pooled risk model
fixed and only let the **baseline hazard** be subtype-stratified. Promotion to any
claim requires BOTH: (a) beating the scramble (permuted-label) control by the
pre-registered margin, AND (b) external replication on a FISH cohort with survival.
Because **GSE19784 carries no survival in the open record**, requirement (b) cannot be
met on open data — therefore this test can only ever be **characterization, never a
promotable claim**, whatever the internal result. No new architecture is built for it.

**Result (run 2026-06-30, `outputs/calibration_subtype_open_gdc_os/`):** an internal
calibration signal IS present — subtype-stratified baseline beats BOTH pooled and
scramble on small-subtype IBS (real 0.158 vs pooled 0.170 vs scramble 0.174), and it
is **del(17p)-driven** (del17p IBS 0.150 real vs 0.175 pooled vs 0.180 scramble;
del(1p) is flat). This is **not** a null. But per (b) it is **unpromotable** and is
recorded as a hypothesis-generating, externally-unverifiable internal positive. It is
biologically coherent that the one lesion with a calibration signal is del(17p), the
highest-FISH-specificity call. It does **not** change the headline: discrimination
(Stage D / Direction-2) remains null and the canonical model stays pooled penalised
Cox.

## 5. Claim register delta

- ❌ removed: "subtype-aware OPSD/HSS model" as a contribution or headline.
- ❌ removed: any implication that the subtype heads capture cytogenetic biology.
- ✅ added: "cross-axis ceiling — subtype-conditioning is null vs pooled penalised Cox."
- ✅ added: "sequencing-inferred subtype labels validated on open data (external FISH
  for del(13)+hyperdiploid; cluster concordance for translocations; robust to
  published label-noise rates); residual limitation: not validated vs CoMMpass FISH."
- ✅ unchanged: OS-only endpoint gate; no relapse/PFS/clinical-use claims.

_Endpoint = OS technical validation only._
