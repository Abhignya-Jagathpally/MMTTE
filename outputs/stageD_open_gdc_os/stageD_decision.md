# Stage D — negative-control decision (open_gdc_os, OS technical validation)

Small (least-prevalent CNV) subtypes: ['del17p', 'del1p']

Mean small-subtype IBS improvement (independent - HSS; +ve = HSS better):
  - real: +0.0118
  - permuted: +0.0170
  - random: +0.0392
  - lambda0: +0.0115
  - lambda_huge: +0.0131

real - max(permuted, random) = -0.0274 (pre-registered margin 0.01).

## VERDICT: STOP
REGULARIZATION/NULL: real ~ permuted/random -> benefit is not subtype biology. STOP the subtype-aware novelty claim per pre-registration.

- lambda0 vs real isolates the distillation's contribution; lambda_huge is the collapse-to-agnostic control.
- Endpoint = OS technical validation. NO relapse/PFS claim; NO clinical-use claim.
