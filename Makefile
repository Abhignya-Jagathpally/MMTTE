PY ?= python
CONFIG ?= configs/experiments/experiment0_open_gdc_os.yaml

.PHONY: setup fetch-open-gdc build-features audit experiment0 residual-report run test package clean

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

test:
	pytest -q

package:
	$(PY) -m build

clean:
	rm -rf outputs/demo_experiment outputs/*/__pycache__ .pytest_cache
