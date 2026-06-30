# MM-TTE-OPSD — Real-Data Run Summary

Moved from demo scaffold to a real patient-level pipeline using **GDC
MMRF-CoMMpass open-access data** (Data Release 45.0). No synthetic values are
used anywhere; every cell traces to a downloaded GDC record.

## Data provenance (Steps 1–3)

| Table | N | Source | Script |
|---|---|---|---|
| `clinical_survival.csv` | 995 pts, 191 deaths | GDC clinical API (`cases` endpoint) | `scripts/realdata/fetch_clinical.py` |
| `cytogenetics.csv` | 908 pts | GDC open Copy Number Segment (WGS, GRCh38) + RNA surrogates | `fetch_cnv.py`, `call_cytogenetics.py`, `build_omics.py` |
| `omics.csv` | 787 pts × 128 PCs | GDC STAR gene-counts → log2(TPM+1) → PCA (80.9% var) | `fetch_rna.py`, `build_omics.py` |

### Honest data caveats
- **Endpoint = overall survival (OS).** PFS/progression dates are **not**
  distributed in GDC open clinical, so `pfs_time`/`pfs_event` are intentionally
  empty (and `riss` is blank — R-ISS needs an LDH ULN + FISH translocations not
  reliably available open-access).
- **Cytogenetics:** amp1q / del1p / del13q / del17p / hyperdiploid are
  CNV-derived (per-sample genome-median-recentred, length-weighted arm log2
  ratios). Population frequencies match MM literature (del13q 50%, amp1q 35%,
  del17p 11%, del1p 17%, hyperdiploid 62%).
- **Translocations** t(4;14)/t(11;14)/t(14;16) are **expression surrogates**
  (NSD2/FGFR3, CCND1, MAF over-expression), thresholded to literature
  prevalence (13% / 16% / 5%) — NOT gold-standard FISH.
- Baseline serial labs (β2M, albumin, LDH, Hb, creatinine, calcium) are real
  GDC `molecular_tests` values — these are also the longitudinal repeated
  measures needed for Step 8.

## Audit (Step 4) — `outputs/real_audit.json`
`survival_tte: true · cytogenetic_subtype_tte: true · multiomic_tte: true`,
publication-grade subtype gate **passes** (N≥200, events≥60).

## Benchmark (Step 6) — `outputs/real_run/benchmark_table.md`
Same OS endpoint, same patient-disjoint hash split (seed 42), same Harrell C +
500× test bootstrap CI. Held-out test = 148 patients / 19 events.

| Model | Test C-index | 95% CI |
|---|---|---|
| Cox: clinical | **0.850** | 0.764–0.923 |
| Cox: clinical+cyto | 0.816 | 0.713–0.898 |
| Cox: clinical+cyto+omics | 0.812 | 0.725–0.893 |
| Weibull-AFT: full | 0.810 | 0.723–0.893 |
| Neural AFT / FHT / Cox (repo) | 0.78 | ~0.66–0.89 |
| Cox: omics(PCs) only | 0.667 | 0.556–0.785 |
| Subtype-only (mmSYGNAL-style) | 0.499 | 0.340–0.657 |
| OPSD-AFT / OPSD-FHT / subtype-rate | ~0.47–0.49 | — |

**Key honest finding:** clinical covariates (ISS, β2M, albumin, age) carry
essentially all the prognostic signal on this split/endpoint. Adding
cytogenetics or 128-PC omics does **not** improve held-out OS discrimination,
and self-distillation (OPSD-AFT/FHT) *hurts* here. No SOTA claim is made — CIs
are wide (19 test events) and overlap. MyeVAE-style not reproduced (needs
published weights); omics-PC Cox is the closest open analog.

## Interpretation (Step 7)
- **Permutation importance** (`permutation_importance.csv`): top = ISS-III, β2M,
  age, albumin — canonical MM prognostics; the model learned real biology.
- **KM by predicted-risk tertile** (`figures/km_risk_groups.png`): log-rank
  **p = 1.2e-4**, high-risk OS → 0.57 vs low/mid ~0.9.
- **Calibration** (`figures/calibration.png`), **subtype-specific drivers**
  (`subtype_feature_importance.csv`), and **PC→gene drivers**
  (`pc_gene_drivers.csv`, a transparent stand-in for pathway enrichment — feed
  to gseapy/Enrichr next).

## Reproduce
```bash
bash scripts/realdata/run_all_real.sh      # Steps 1–7 end to end
```

## Experiment 0 — residual-risk, matched ablation, endpoint-gated claims
`python -m mm_tte_survival.cli residual-report --config configs/real_training.yaml`
→ `residual_and_usefulness_report.md`, `endpoint_gate_report.md` (+ CSVs/JSON).
One matched cohort (**N=726**, all modalities), stratified-event split, train-only
preprocessing (`leakage_audit.json`). See `docs/experiment0_framing.md`.

**Headline (correct language):** in a matched open-GDC **OS** cohort, omics moved
held-out C-index from 0.736 (clinical) to 0.782 (clinical+cyto+omics), improving in
**94% of 50 repeated splits** (NRI ≈ 0.40, better Brier, higher decision-curve net
benefit). The paired ΔC CI overlaps 0 and the endpoint is OS ⇒
**hypothesis-generating evidence of molecular residual signal, not confirmatory
evidence of clinical utility.**

**Endpoint-gated claim report** (`claim_report.json`, separated & corrected):
technical_validation **YES** · primary_biological **NO** · relapse_or_pfs **NO** ·
omics_increment_confirmed **NO** (SUGGESTIVE_NOT_CONFIRMED) · external_validation
**NO** · evidence_level **technical_validation_only**. An OS endpoint can never
license a relapse/PFS claim (`configs/endpoints.yaml`).

**Paired ΔC-index** (`paired_delta_cindex.csv`, same test patients): clinical+omics
vs clinical ΔC=+0.047 (CI −0.038…+0.137, p=0.15); residual-total vs clinical
+0.040. All "hypothesis_generating_improvement".

**Residual decomposition** (`residual_risk_decomposition.csv`, exactly additive,
clin coef 1.025≈1): clinical 0.735 · molecular-residual-alone 0.650 · total 0.775.
Coefs in `clinical_risk_coefficients.csv` / `molecular_residual_coefficients.csv`;
drivers (provenance-flagged, RNA = PC-loading-derived NOT direct genes) in
`molecular_residual_top_drivers.csv` — proliferation PCs (MCM6/MCM3/TFDP1), CCND2, MAF.

**Repeated-split / calibration / DCA / NRI-IDI**: `repeated_split_leaderboard.csv`
(clinical 0.661 → +omics 0.730 mean), `calibration_metrics.csv` (omics best Brier
0.132, slope≈1.0), `decision_curve_analysis.csv`, `reclassification_metrics.csv`.

**Program-activity path** (`build_programs.py` → `program_activity.csv`): 10 curated
MM signatures as a biologically-interpretable alternative to PCA; adds +0.028
(less than PCA's +0.047) — auto-included as ablation arms when present.

**Subtype evidence (event-gated)** (`mmrf_subtype_gain_fail.csv`): amp1q/del13q/
hyperdiploid = *hypothesis_generating*; t(4;14)/t(11;14) = *unstable_descriptive_only*
(<10 events). Possible omics benefit across strata (notably amp1q, t(4;14)) but
event counts too small for confirmatory subtype claims.

**Reclassification OUTCOME validation** (`mmrf_reclassification_outcomes.csv`) — the
key check that reclassification matters: *clinical-low/molecular-high* event rate
0.14 vs *clinical-low/molecular-low* 0.04; *clinical-high/molecular-high* HR 3.37
(log-rank p<1e-4, median OS 37.8 mo). 158 clinically-standard pts flagged
molecularly HIGH; 109/351 cyto-high re-scored molecularly LOWER. Cytogenetics
provenance in `cytogenetics_provenance.csv` (CNV calls vs RNA surrogates).

## Step 8 (longitudinal — not yet done)
The longitudinal resistance-trajectory claim stays out of scope until repeated
pre-event molecular snapshots are joined. The real serial labs already in
`clinical_survival.csv`'s source (GDC molecular_tests) are the first substrate
for that extension; scRNA disease-state and treatment-line transitions require
controlled-access MMRF data.
