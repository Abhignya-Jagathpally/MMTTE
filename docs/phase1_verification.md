# Phase 1 — production-refactor verification

Audit confirming no old monolithic logic remains in active use.

| Check | Result |
|---|---|
| Full pipeline runs through `main.py` only | ✅ `python -m mm_tte_survival.main --config configs/experiments/experiment0_open_gdc_os.yaml` → EXIT 0 |
| `residual.py` is a shim only | ✅ 30 lines, no analysis logic (re-exports `run_residual_report` → evaluate + write) |
| All reports come from `reports/run_reports.py` | ✅ only `reports/run_reports.py` + `reports/cards.py` write report files; `evaluation/external.py` writes its own `external_*` reports |
| `evaluate.py` is compute-only | ✅ no `.to_csv`/`.write_text` in `evaluation/evaluate.py` |
| `run_reports.py` is write-only | ✅ no metric computation (no `fast_c_index`/`paired_delta_cindex`/`CoxPHFitter`) |
| All metrics come from `evaluation/` | ✅ C-index in `metrics.py`; paired ΔC / calibration / DCA / NRI-IDI in `evaluation/stats.py` |
| All data checks come from `data/contracts.py` | ✅ `validate_all_inputs` defined once, called by `main.py` |
| No stale imports of removed top-level modules | ✅ no `mm_tte_survival.{losses,stats,train}` imports remain |
| `model_card.md`, `claim_card.md`, `data_card.md` generated | ✅ all present in `outputs/experiment0_open_gdc_os/` |
| CI / tests pass | ✅ 8 passed |

Pipeline data flow (single path):
`load_modalities → validate_all_inputs (contracts) → build_matched_cohort →
evaluate_model_suite (ResidualRiskModel + metrics, compute-only) →
write_all_reports (write-only + cards)`.

Note: `scripts/realdata/benchmark.py` and `interpret.py` (Steps 6–7) remain as
standalone exploratory analyses writing to `outputs/real_run/`; they are NOT part
of the `main.py` production path and can be retired once their outputs are folded
into the report layer. They are reachable via `make exploratory` (kept callable,
explicitly outside the canonical `make all`). See `scripts/README.md` for the full
role register of every script (which may fit a model for the record, which is
plot-only).

Fragility-1 update: Figure S4 previously refit 200 Cox models inside the figure
script. That compute now lives in `scripts/analysis/repeated_split_detail.py`
(CSV out); `scripts/figures/sfig4_repeated_split.py` is plot-only. Canonical
reproduction is now a single command: `make all` (= run → analysis → figures).
