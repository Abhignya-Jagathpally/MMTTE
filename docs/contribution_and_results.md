# Contribution and Results

## 1. Summary

The durable contribution of this project is a **leak-proof, endpoint-gated benchmark
methodology** for multiple-myeloma overall-survival (OS) modeling on open data — not a
new neural model. The neural "Hierarchical Subtype Survival" (HSS) model (a shared
trunk with per-cytogenetic-subtype heads and survival-curve distillation) was
**falsified by its own pre-registered negative controls**: it improves rare-subtype
calibration just as much under scrambled subtype labels, so the apparent benefit is
generic shared-trunk regularization, not subtype biology. We report this null honestly;
the controls firing as designed is the methodology working.

## 2. The contribution: a leak-proof, endpoint-gated benchmark

The methodological contributions are concrete and independently reusable:

- **Patient-disjoint, event-stratified splits.** Five folds with one row per patient,
  split so that no patient appears in more than one fold and events are stratified
  across folds (`patient_disjoint_stratified_split`).
- **In-fold PCA with a fit manifest.** Top-variable-gene selection, scaling, and PCA
  are all fit on train rows only (`OmicsInFoldPCA`). A per-fold `pca_fit_manifest.csv`
  records `test_rows_in_fit=0` and `train_test_patient_overlap=0`, providing an audit
  trail that the transform never saw held-out patients.
- **Executable leakage audit that fails loud.** `leakproof_leakage_audit.json`
  records enforced checks (`one_row_per_patient`, `patient_disjoint_per_fold`,
  `no_endpoint_or_id_in_features`, `pca_fit_train_only_zero_test_rows`); the run
  aborts rather than silently producing optimistic numbers.
- **IPCW-IBS, not a proxy.** The primary calibration metric is the IPCW integrated
  Brier score (sksurv), replacing a prior `risk_event_proxy` that had been
  mislabelled as IBS.
- **CNV-only, leak-free subtype labels.** Primary subtype membership uses CNV-derived
  calls only (`amp1q, del1p, del13q, del17p, hyperdiploid`). The three translocation
  labels (`t_4_14, t_11_14, t_14_16`) are RNA-expression surrogates thresholded on
  full-cohort quantiles — a mild label leak — so they are **excluded from the primary
  analysis** and retained only as a labeled sensitivity check.
- **Endpoint claim gating.** The open GDC cohort carries OS only; there is no
  relapse/PFS information. The pipeline treats this as a hard gate: OS results cannot
  license any PFS or relapse claim.
- **Pre-registration plus negative controls.** The HSS hypothesis, comparators,
  primary metric, and falsification rule were written down before the full run
  (`docs/preregistration_hss.md`), and the promotion decision is adjudicated against
  pre-registered negative controls (Stage D).

## 3. Honest re-baseline results (Stage A)

Open GDC MMRF-CoMMpass, OS endpoint only, N=726 matched patients, 152 events, 5
patient-disjoint folds. Omics PCA fit in-fold; primary width k=16.

| Feature set | C-index | IBS |
|---|---|---|
| Clinical | 0.688 | 0.140 |
| Clinical + omics (in-fold) | 0.754 | 0.126 |
| Clinical + cyto + omics (in-fold) | 0.747 | — |

The PCA leak optimism is **negligible**: the legacy precomputed full-cohort PCA
overstates the omics C-index by only +0.0014 at k=16, and the sign *reverses*
(in-fold is better) at k=32 and k=64. The omics increment therefore survives the leak
fix and is not an artifact of full-cohort PCA. The pre-registered width sweep
k ∈ {8, 16, 32, 64} shows k=8–16 optimal and k=64 overfitting. Adding cytogenetic
features on top of omics does not improve discrimination (0.747 vs 0.754). These are
**OS technical-validation** numbers only.

## 4. The negative result (Stage D)

**What was tested.** Whether HSS's shared trunk plus survival-curve distillation
improves calibration on the least-prevalent CNV subtypes (`del17p`, `del1p`) relative
to independent-per-subtype models, and whether any such improvement is attributable to
real subtype biology. Mean small-subtype IBS improvement is reported as
(independent − HSS), so a positive value means HSS is better.

| Condition | Mean small-subtype IBS improvement | What it isolates |
|---|---|---|
| real | +0.0118 | actual subtype labels |
| permuted | +0.0170 | subtype labels shuffled across patients |
| random | +0.0392 | random subtype assignments |
| lambda0 | +0.0115 | distillation off (independent heads) |
| lambda_huge | +0.0131 | distillation collapsed to agnostic |

**STOP verdict.** HSS improves rare-subtype calibration *at least as much* with
scrambled labels (permuted +0.0170, random +0.0392) as with real labels (+0.0118):
`real − max(permuted, random) = −0.0274`, well below the pre-registered +0.01 margin.
The benefit is therefore generic shared-trunk **regularization**, not subtype biology.
Separately, `lambda0` (+0.0115) ≈ `real` (+0.0118), so the survival-curve distillation
— the model's headline mechanism — adds essentially nothing. Per the pre-registered
decision rule, the subtype-aware novelty claim is **STOPPED**. This is the controls
doing their job: a falsifiable design returning an honest null, not a failure to be
hidden.

## 4b. The honest model is penalised Cox (Direction-2 probe)

Stage D compared HSS to *independent-per-subtype* Cox — a weak, unstable baseline. The
fair test of whether any neural regularization is useful is against the **strong** simple
baseline: a pooled penalised Cox. We computed per-subtype IPCW-IBS for three models with
a common subtype-calibrated Breslow baseline (so only the risk-ranking differs):
independent Cox, pooled penalised Cox, and a pooled neural Cox (shared-trunk MLP).

Mean IPCW-IBS on the small CNV subtypes (`del17p`, `del1p`; lower is better):

| Model | Small-subtype IBS |
|---|---|
| Pooled penalised Cox | **0.158** |
| Independent-per-subtype Cox | 0.162 |
| Pooled neural (MLP-Cox) | 0.172 |

`pooled_cox − pooled_neural = −0.0138`, i.e. the neural model is **worse** than penalised
Cox by more than the +0.01 margin. Across all five CNV subtypes, pooled penalised Cox was
the best or near-best on both IBS and C-index, and the pooled neural was consistently the
**worst** on both. **VERDICT: NULL** — there is no neural advantage at this sample size and
event count; the only useful regularization is the L2 penalty + pooling of a standard Cox.
This is consistent with the original review's prediction that penalised Cox, not an MLP,
is the right model here. (Notably, pooled penalised Cox also beats independent-per-subtype
Cox on the smallest subtype — so the rare-subtype benefit is real, but it comes from
*penalised Cox pooling*, not a neural net.)

## 4c. The subtype labels are validated to the extent open data allows

No FISH ground truth exists for the open CoMMpass cohort (MMRF seqFISH is
controlled-access), so the **sequencing-inferred** subtype labels are validated with
a layered open-data stack rather than asserted (`mm-tte validate-subtypes`; full
narrative in `docs/subtype_label_validation.md`):

| Layer | Result |
|---|---|
| External **real FISH** (GSE6477) | del(13) AUC 0.85 / κ 0.63; hyperdiploid AUC 0.73 / κ 0.40 |
| External **cluster concordance** (GSE19784, not FISH) | t(11;14) AUC 0.94, t(4;14) AUC 0.99, **t(14;16) AUC 0.49 (fails)** |
| Internal cross-modality (CoMMpass, not FISH) | amp(1q) AUC 0.77, del(13) 0.75 strong; del(17p) 0.56 (biology: hemizygous loss barely lowers mRNA); del(1p) 0.45 weakest |
| Literature CNV-vs-FISH concordance | >99%/>99% for IGH translocations + gains/losses in custom-capture NGS; del(17p) sensitivity variable (subclonal) — `docs/literature_cnv_fish_concordance.md` |
| **Label-noise robustness** | flipping labels at published FISH-discordance rates leaves pooled penalised Cox no-worse-than subtype-specific in 95% of draws → the subtype-aware **NULL is not a label-noise artifact** |

These results both (a) establish the labels carry genuine biology — so the Stage-D
null is a real null, not noise — and (b) scope claims honestly: del(13) best-supported,
del(17p) trust FISH-literature not expression, del(1p) and t(14;16) most uncertain.
A FISH-ready harness computes genuine sensitivity/specificity the moment a
controlled-access CoMMpass FISH file is supplied. Full framing:
`docs/FRAMING_SUBTYPE_AWARE_NULL.md`.

## 5. Explicit non-claims

- **No relapse / PFS claim.** The open cohort has OS only; nothing here speaks to
  progression or relapse.
- **No clinical-use claim.** This is technical validation, not a clinical tool.
- **No state-of-the-art claim.** No comparison here establishes SOTA OS prediction.
- **No subtype-aware-biology claim.** Stage D shows the subtype heads capture
  regularization, not cytogenetic biology; the label-noise control shows this null is
  not a label-accuracy artifact.
- **No neural-novelty claim.** HSS was falsified by its own controls; the contribution
  is the benchmark methodology, not the model.
- **No FISH-subtype claim.** Labels are *sequencing-inferred* (CNV segments + RNA
  surrogates), validated externally on FISH only for del(13)/hyperdiploid; CoMMpass
  calls are not validated against CoMMpass FISH. Translocations are exploratory;
  t(14;16) fails its concordance check.

## 6. Reproducibility

- Stage A leak-proof re-baseline: `mm-tte rebaseline`
- Stage D negative controls: `mm-tte stage-d`
- Direction-2 regularization probe: `mm-tte regularization`
- Subtype-label validation stack (external FISH + concordance + label-noise): `mm-tte validate-subtypes`
- Label-noise robustness alone: `mm-tte label-noise`
- Pre-registered calibration one-shot (characterization only): `mm-tte subtype-calibration`
- Git tags:
  - `v1.0-stageA-leakproof-rebaseline` — the honest re-baseline
  - `v1.1-stageD-negative-control` — the negative-control STOP verdict

Artifacts: `outputs/rebaseline_open_gdc_os/` (leaderboard, paired deltas, calibration,
IPCW-IBS, leakage audit, PCA fit manifest, leak-delta summary, claim card),
`outputs/stageD_open_gdc_os/` (negative-control table and decision), and
`outputs/regularization_open_gdc_os/` (per-subtype model comparison and decision).
