# Direction-2 — regularization probe (pooled neural vs pooled penalised Cox)

Small subtypes: ['del17p', 'del1p']

Mean small-subtype IPCW-IBS (lower=better):
  - independent_cox: 0.1615
  - pooled_cox: 0.1584
  - pooled_neural: 0.1722

pooled_cox - pooled_neural = -0.0138 (margin 0.01; +ve favours neural).

## VERDICT: NULL (use penalised Cox)
NULL: pooled_neural ~ pooled_cox on small-subtype IBS -> penalised Cox is the honest answer; no neural advantage (regularization angle does not survive).

- Endpoint = OS technical validation. NO relapse/PFS claim; NO clinical-use claim.
