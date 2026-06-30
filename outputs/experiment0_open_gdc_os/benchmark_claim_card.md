# Benchmark claim card — mmSYGNAL vs proposed model

- Source: github.com/baliga-lab/mmSYGNAL-risk-prediction-models (GPL-3.0), external dependency, not vendored.
- Endpoint: **open_gdc_os (overall survival)**.
- **mmSYGNAL is a relapse/PFS-risk model.** Evaluating it on OS measures OS discrimination only; it is NOT an endpoint-matched test of mmSYGNAL's intended PFS performance and gives mmSYGNAL no home-field advantage.
- Rules enforced: same patients, same OS endpoint, same train/test split for fitted comparators; mmSYGNAL pretrained scores used with **no refitting**.
- **direct relapse/PFS claim allowed: NO** · clinical-use claim: NO · research benchmark: YES.
- Do NOT rank OS C-index against PFS/risk metrics without this warning.
