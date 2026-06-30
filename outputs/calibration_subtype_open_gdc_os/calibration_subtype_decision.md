# Subtype-conditioned calibration — pre-registered one-shot (OS technical validation)

Small subtypes: ['del17p', 'del1p']

Mean small-subtype IPCW-IBS by baseline scheme (lower=better):
  - pooled: 0.1701
  - real: 0.1584
  - scramble: 0.1744

pooled-real = +0.0118, scramble-real = +0.0161 (margin 0.01; +ve favours real subtype stratification).

## VERDICT (promotable=False)
CHARACTERIZATION ONLY — internal calibration signal present: subtype-stratified baseline beats BOTH pooled and scramble on small-subtype IBS (del17p-driven). This is NOT a null. But the pre-registered external-replication requirement is UNMEETABLE on open data (no survival in GSE19784), so it CANNOT be promoted to a claim; reported as an unverifiable internal positive, hypothesis-generating only.

- D-calibration p per subtype/scheme in calibration_subtype_summary.csv (higher p = better-calibrated).
- Endpoint = OS technical validation. NO relapse/PFS claim; NO clinical-use claim.
