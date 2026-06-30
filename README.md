# MM-TTE — a leak-proof, endpoint-gated survival benchmark for open MMRF-CoMMpass

A **reference-validated time-to-event framework** for multiple-myeloma **overall
survival (OS)** on open data, plus a **pre-registered cross-axis ceiling result**:
neither omics-PCA conditioning nor cytogenetic-**subtype** conditioning beats a
pooled penalised model. The durable contribution is the *methodology and the honest
negative*, not a subtype-aware model.

> **Endpoint scope (binding).** The open GDC MMRF-CoMMpass cohort carries **OS only**
> — there is no relapse/PFS. OS results **cannot** license any PFS/relapse claim
> (enforced in the claim gate). This is **technical validation**, not a clinical tool.
>
> **Cytogenetics are sequencing-inferred, NOT FISH.** CNV subtypes (`amp1q, del1p,
> del13q, del17p, hyperdiploid`) come from GDC copy-number segments; translocations
> (`t_4_14, t_11_14, t_14_16`) are RNA-expression **surrogates**. No FISH exists for
> the open cohort (MMRF seqFISH is controlled-access). See label validation below.

## What this repo actually shows

1. **Reference-validated survival losses.** Cox (Breslow), log-normal AFT, and
   inverse-Gaussian first-hitting-time NLLs match scipy closed forms to ~1e-15 and
   stay numerically live in the censored / overflow regimes
   (`training/losses.py`, `tests/test_losses.py`, SFig loss-correctness).
2. **A leak-proof, endpoint-gated benchmark.** Patient-disjoint event-stratified
   splits, in-fold PCA with a fit manifest, an **executable leakage audit that fails
   loud**, IPCW integrated Brier score, CNV-only primary labels, claim gating,
   pre-registration + negative controls.
3. **The honest model is pooled penalised Cox.** `clinical + omics(in-fold)`,
   C≈0.74 (50 patient-disjoint splits); everything lands in/near the honest
   open-data ceiling (~0.62–0.65 for MM-OS). Fig 1.
4. **Subtype-awareness is a pre-registered NULL.** A neural subtype-conditioned model
   improves rare-subtype calibration **no more than scrambled labels** (Stage D), and
   a pooled neural model does **not** beat penalised Cox (Direction-2). Figs 2–3.
5. **The labels are validated to the extent open data allows.** External real FISH
   (GSE6477: del13, hyperdiploid), expression-cluster concordance (GSE19784:
   translocations), internal cross-modality concordance, literature CNV-vs-FISH
   concordance, and **robustness to realistic label noise** — so the null is not a
   label-accuracy artifact. Fig 4. See `docs/subtype_label_validation.md`.

Full narrative: **`docs/contribution_and_results.md`** and the framing decision in
**`docs/FRAMING_SUBTYPE_AWARE_NULL.md`**.

## Reproduce (canonical, corrected, leak-proof)

```bash
pip install -e ".[dev]"
pytest -q                                   # 48 tests, incl. loss-correctness reference checks

# canonical model record (claim-gated):
mm-tte run         --config configs/experiments/experiment0_open_gdc_os.yaml
mm-tte rebaseline  --config configs/experiments/rebaseline_open_gdc_os.yaml   # leak-proof C/IBS

# the pre-registered negative controls (the headline negative):
mm-tte stage-d         # subtype biology vs regularization  -> NULL
mm-tte regularization  # pooled neural vs penalised Cox      -> NULL

# subtype-label validation (external real-FISH + concordance + label-noise):
mm-tte validate-subtypes
mm-tte label-noise
mm-tte subtype-calibration   # characterization only (external survival replication unmeetable)

# figures (300 dpi, plot-only) -> figures/final/:
python scripts/figures/fig_ceiling_forest.py     # Fig 1 — discrimination ceiling
python scripts/figures/fig_calibration.py        # Fig 2 — calibration (real S(τ), not sigmoid)
python scripts/figures/fig_subtype_null.py       # Fig 3 — subtype-aware NULL
python scripts/figures/fig_label_validation.py   # Fig 4 — label validation
python scripts/figures/sfig_loss_correctness.py  # SFig — loss reference-equivalence
python scripts/figures/sfig4_repeated_split.py   # SFig — repeated-split stability
```

`make all` runs the canonical path (`run → analysis → figures`); `make validation`
runs the subtype-label validation stack. The raw GDC data is real and on disk; the
build scripts (`scripts/realdata/`) regenerate it where access allows.

## Layered package

```
src/mm_tte_survival/
  main.py                 # canonical orchestrator (load->validate->preprocess->fit->evaluate->report)
  config/ data/ preprocessing/ features/
  models/                 # residual_risk (1st-class, pooled penalised Cox), heads, hierarchical (NULL arm)
  training/               # losses (reference-validated), trainers
  evaluation/             # cindex/stats, paired_delta, calibration, dca, nri, claim_gate, leakage audit
  validation/             # external_geo, internal_concordance, label-noise, fish_ready (subtype-label trust)
  reports/                # endpoint-gated model/claim/data cards
experiments_{stageD,regularization,label_noise,calibration_subtype}.py   # pre-registered controls
```

## Scientific guardrails (enforced)

1. **OS cannot license PFS/relapse claims** — claim gate, in code + CI.
2. **No SOTA claim** — no comparison here establishes SOTA OS prediction.
3. **No subtype-aware-biology claim** — Stage D + label-noise control show the
   subtype heads capture regularization, not cytogenetic biology.
4. **No FISH-subtype claim** — labels are sequencing-inferred; validated against FISH
   only externally for del13/hyperdiploid; del1p and t(14;16) are most uncertain.
5. **No synthetic data** — every value derives from real public data.

## License

MIT — see [LICENSE](LICENSE).
