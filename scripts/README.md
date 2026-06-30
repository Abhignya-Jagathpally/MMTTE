# scripts/ — role register (Fragility 1 governance)

Every script here has exactly one role. Only two roles may fit a model whose
output reaches the manuscript: the `src/` pipeline (`make run`) and the
**analysis** layer (`make analysis`). Figure scripts are **plot-only**.
Nothing else produces a manuscript artifact.

**Canonical reproduction is a single command:** `make all` (= `run → analysis → figures`).

| Dir / file | Role | Fits a model? | In `make all`? | Writes record artifact? |
|---|---|---|---|---|
| `src/.../main.py` (via `make run`) | model pipeline (load→validate→preprocess→fit→evaluate→report) | yes (compute-only, src/) | yes | yes (outputs/, reports, cards) |
| `analysis/within_stratum_reclassification.py` | reclassification stats → CSV | yes | yes (`make analysis`) | yes (CSV) |
| `analysis/program_vs_pca_ablation.py` | RNA-PCA vs miner3 ablation → CSV | yes | yes (`make analysis`) | yes (CSV) |
| `analysis/repeated_split_detail.py` | repeated-split stability → CSV (source of Fig S4) | yes | yes (`make analysis`) | yes (CSV) |
| `figures/fig4_*.py`, `figures/fig5_*.{py,R}`, `figures/sfig3_*.py`, `figures/sfig4_*.py` | **plot-only** (read outputs/*.csv) | **no** | yes (`make figures`) | figures only (no numbers) |
| `figures/_style.py` | shared style helper | no | n/a | no |
| `realdata/fetch_*.py`, `call_cytogenetics.py`, `build_omics.py`, `build_programs.py` | ETL: GDC fetch → feature build | no | no (`make fetch-open-gdc` / `build-features`) | data/ inputs only |
| `realdata/benchmark.py`, `realdata/interpret.py` | **exploratory** real-data benchmark/interpretation | yes | **no** (`make exploratory`) | outputs/real_run/ — exploratory, not cited |
| `benchmarks/*.{py,R}` | external mmSYGNAL program build / scoring (off-endpoint) | external (no refit) | no (`make benchmark-mmsygnal` via CLI) | off-endpoint comparator only |
| `diagnostics/diagnose_agent_result.py` | read-only diagnostic | no | no | **none** (prints only) |
| `run_all.sh` | demo/smoke orchestrator (synthetic demo data) | yes (demo only) | no | demo only — never the record |
| `realdata/run_all_real.sh` | full real-data shell orchestrator (fetch→build→experiments→exploratory) | yes | no | superset; `make all` is the canonical subset |
| `plink/`, `seurat/` | templates for external genotype/scRNA tooling | n/a | no | not wired |

## Rules
1. A **figure script** must read `outputs/*.csv` and fit nothing. If you need a new
   number, add it to an `analysis/` script (CSV out), then plot it.
2. A new analysis that produces a manuscript number goes in `analysis/` and is added
   to the `analysis` Makefile target — never run ad hoc.
3. `exploratory` outputs (outputs/real_run/) are not citable until folded into the
   `src/` report layer (see docs/phase1_verification.md).
4. The endpoint is OS technical-validation only — no relapse/PFS or clinical-use claims
   (enforced in code + CI; see configs/reports/claim_language_guardrails.yaml).
