# Debug note: why the agent result does not falsify the multi-omic TTE proposal

## Observed agent result

The real-data run tested open-access GDC MMRF-CoMMpass **overall survival (OS)**.
The agent reported:

- Clinical Cox: C-index ≈ 0.850
- Clinical + cytogenetics: C-index ≈ 0.816
- Clinical + cytogenetics + omics: C-index ≈ 0.812
- Omics-only: C-index ≈ 0.667
- Subtype-only: C-index ≈ 0.499
- OPSD variants: ≈ 0.48

That is an honest negative result for the *specific endpoint/feature setup*, not a failure of the research idea.

## Main debugging diagnosis

### 1. Endpoint mismatch

The proposal is about relapse/progression/TTE. The agent used open GDC OS because open GDC clinical does not provide PFS/progression labels. OS is heavily explained by clinical disease burden and baseline labs, so it is not surprising that ISS, beta-2 microglobulin, albumin, and age dominate.

**Fix:** all reports must label this endpoint as `open_gdc_os`, not relapse/PFS. Do not make relapse claims from this run.

### 2. Representation mismatch

The agent built `omics.csv` as RNA-seq PCA features, then the original data loader PCA-transformed the omics table again. If the input is already PC features, MINER/mmSYGNAL program scores, or pathway activities, a second PCA is not appropriate.

**Fix:** `features.omics_transform: auto` now detects precomputed PC/program features and passes them through. Use `pca` only for raw high-dimensional expression matrices.

### 3. Underpowered held-out event count

The reported test split had only 19 deaths. A single split with 19 events is too small for strong conclusions about small incremental C-index improvements.

**Fix:** use event-stratified splitting by default and require a minimum test-event gate before accepting comparison claims. For final results, use repeated cross-validation or bootstrap optimism correction.

### 4. Unfair ablation risk

If clinical-only, clinical+cyto, and clinical+omics models are not evaluated on exactly the same patient intersection, differences may reflect sample composition rather than feature value.

**Fix:** for strict ablation studies, set:

```yaml
cohort:
  require_omics: true
  require_cytogenetics: true
```

For deployment-style models, keep them false and use missingness indicators.

### 5. OPSD collapse

The initial OPSD implementation began distilling too early from a near-random EMA teacher. On small censored datasets this can anchor an uninformative ranking and collapse C-index.

**Fix:** OPSD now uses warm-up + ramped distillation:

```yaml
training:
  distill_weight: 0.05
  distill_start_epoch: 40
  distill_ramp_epochs: 20
```

OPSD should be reported only if it improves validation performance over the non-distilled base model.

## Correct interpretation

The agent result supports this revised claim:

> On open-access GDC OS labels, clinical burden variables dominate prediction; RNA PCA and CNV-derived cytogenetics do not improve held-out OS C-index in the current underpowered single-split experiment. This does not test whether curated gene-program activity or multi-omics improves PFS, relapse, or treatment-response prediction.

## Required next experiment

1. Use PFS/progression/relapse labels from controlled MMRF/CoMMpass access, MMRF Researcher Gateway, or another cohort with relapse/progression labels.
2. Replace RNA PCA with MINER/mmSYGNAL program activity features or pathway scores.
3. Run matched-cohort ablations:
   - clinical only
   - cytogenetics only
   - omics/program only
   - clinical + cytogenetics
   - clinical + omics
   - clinical + cytogenetics + omics
4. Evaluate with repeated event-stratified splits or nested cross-validation.
5. Report delta C-index, time-dependent AUC, Brier/calibration, and likelihood-ratio tests where appropriate.
