PY ?= python
CONFIG ?= configs/experiments/experiment0_open_gdc_os.yaml

.PHONY: setup fetch-open-gdc build-features audit experiment0 residual-report run \
        analysis figures all exploratory validation test package clean

# ---------------------------------------------------------------------------
# Canonical execution path (Fragility 1: one auditable path to the manuscript).
#   make all  ==  run -> analysis -> figures
# `run` fits every model (compute-only, src/ pipeline). `analysis` refits the
# repeated-split / ablation / reclassification numbers to CSV. `figures` is
# PLOT-ONLY (reads CSVs, fits nothing). Nothing outside this path produces a
# manuscript artifact; exploratory scripts live under the `exploratory` target.
# ---------------------------------------------------------------------------
all: run analysis figures
	@echo "== canonical reproduction complete: model run + analysis CSVs + figures =="

setup:
	pip install -e ".[dev]"

fetch-open-gdc:
	$(PY) scripts/realdata/fetch_clinical.py
	$(PY) scripts/realdata/fetch_cnv.py
	$(PY) scripts/realdata/fetch_rna.py

build-features:
	$(PY) scripts/realdata/call_cytogenetics.py
	$(PY) scripts/realdata/build_omics.py
	$(PY) scripts/realdata/build_programs.py

audit:
	$(PY) -m mm_tte_survival.cli audit-data \
		--clinical data/real/clinical_survival.csv \
		--cytogenetics data/real/cytogenetics.csv \
		--omics data/real/omics.csv \
		--out outputs/real_audit.json

experiment0:
	$(PY) -m mm_tte_survival.main --config $(CONFIG)

run:
	$(PY) -m mm_tte_survival.main --config $(CONFIG)

residual-report:
	$(PY) -m mm_tte_survival.cli residual-report --config configs/real_training.yaml

RSCRIPT ?= /home/aj0486@students.ad.unt.edu/micromamba/envs/rsygnal/bin/Rscript

# Analysis = compute-only. Refits models and writes CSVs the figures consume.
# This is the ONLY layer (besides `run`) allowed to fit a model for the record.
analysis:
	$(PY) scripts/analysis/within_stratum_reclassification.py
	$(PY) scripts/analysis/program_vs_pca_ablation.py
	$(PY) scripts/analysis/repeated_split_detail.py

# Figures = plot-only. Every script here reads outputs/*.csv and fits nothing.
figures: analysis
	$(PY) scripts/figures/fig4_os_benchmark.py
	$(RSCRIPT) scripts/figures/fig5_within_stratum.R
	$(PY) scripts/figures/fig5_reclassification.py
	$(PY) scripts/figures/sfig3_mmsygnal_program_validation.py
	$(PY) scripts/figures/sfig4_repeated_split.py

# Exploratory = NOT part of the canonical record. Neural ablation + standalone
# real-data benchmark/interpretation that write to outputs/real_run/. Kept
# callable (no orphan scripts) but explicitly outside `make all`.
exploratory:
	$(PY) -m mm_tte_survival.cli run-experiments --config configs/real_training.yaml
	$(PY) scripts/realdata/benchmark.py
	$(PY) scripts/realdata/interpret.py

# Validation = subtype-label trustworthiness (external real-FISH on GEO + cluster
# concordance + internal cross-modality + label-noise robustness) and the
# pre-registered calibration one-shot. Supports the subtype-aware NULL framing
# (docs/FRAMING_SUBTYPE_AWARE_NULL.md); not a manuscript model-record itself.
validation:
	$(PY) -m mm_tte_survival.cli validate-subtypes
	$(PY) -m mm_tte_survival.cli subtype-calibration

test:
	pytest -q

package:
	$(PY) -m build

clean:
	rm -rf outputs/demo_experiment outputs/*/__pycache__ .pytest_cache
