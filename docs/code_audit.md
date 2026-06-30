# Code-quality audit (v0.9)

## 1. Functions > 60 lines (active `src/`, excluding legacy)
| Lines | Location | Verdict |
|---|---|---|
| 121 | `data/dataset.py:prepare_dataset` | **legacy** — used only by `run-experiments` (neural), NOT the `main.py` path. Candidate to split if that path is kept. |
| 72 | `audit.py:audit_inputs` | acceptable — linear gate report builder |
| 71 | `cli.py:main` | acceptable — argparse subcommand dispatch |
| 69 | `benchmarks/mmsygnal.py:run_mmsygnal_benchmark` | acceptable — orchestration; fail-closed guard + ablation |

No active function is doing hidden heavy logic; the long ones are dispatch/orchestration.

## 2. TODO / FIXME / NotImplemented / scaffold / bare-pass in active `src/`
**None.** (The intentional fail-closed `build_mmsygnal_program_activity*.R` "scaffold/stop"
lives in `scripts/`, not `src/`.)

## 3. Duplicate metric implementations
Two C-index functions exist **by design**: `metrics.harrell_c_index` (reference, O(n²)
Python) and `metrics.fast_c_index` (vectorised numpy, used in bootstrap/repeated-split
hot paths). `tests/test_metric_consistency.py` asserts they agree to 1e-9. No other
duplicate metric logic; calibration/DCA/NRI/paired-ΔC live only in `evaluation/stats.py`.

## 4. Duplicate plotting logic
All figure scripts share `scripts/figures/_style.py` (colours, save, color_for). One
script per final figure. No duplicated plotting helpers. KM/forest survival figure is in
R (`fig5_within_stratum.R`); bar/box/QC in matplotlib.

## 5. Single active execution path
`main.run_pipeline`: `load_modalities → validate_all_inputs → build_matched_cohort →
evaluate_model_suite (compute-only) → write_all_reports (write-only)`. Confirmed in
`docs/phase1_verification.md`. `run-experiments` (legacy neural) and `benchmark-mmsygnal`
are separate, explicitly-invoked CLI commands — not part of the production path.

## 6. Report-number provenance
All report tables/JSON are written by `reports/run_reports.py` from the dict returned by
`evaluation.evaluate.evaluate_model_suite`; `evaluate.py` performs no file writes. Every
number traces to a computed array → CSV/JSON.

## 7. Figure-number provenance
| Figure | Source |
|---|---|
| Fig 4 | `outputs/.../sota_comparison.csv` |
| Fig 5 (R KM+forest) | `residual_risk_decomposition.csv`, `reclassification_within_stratum_{hr,logrank}.csv` |
| Fig 5 (composite) | same + `mmrf_reclassification_outcomes.csv` |
| S3 | `data/real/mmsygnal_program_activity_0_140.csv`, `mmsygnal_scores.csv`, `cytogenetics.csv` |
| S4 | recomputed per-split (build_matched_cohort + `_fit_cox`), deterministic seed |
| program-vs-PCA | `program_vs_pca_*.csv` |

No figure hard-codes results; all read CSVs or recompute deterministically.

## Recommended follow-ups (non-blocking)
- Decide whether to keep the legacy `run-experiments`/`prepare_dataset` path; if yes, split
  `prepare_dataset` into load/encode/split helpers.
- Consider folding `scripts/benchmarks/run_mmsygnal.R` selection logic into a tested helper.
