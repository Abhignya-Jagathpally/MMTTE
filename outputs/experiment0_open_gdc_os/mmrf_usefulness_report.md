# MMRF usefulness report

- Patients reclassified by omics: **284** (up 135 / down 149)
- Clinically standard-risk but molecularly HIGH: **156**
- Cytogenetic high-risk but molecularly LOWER: **122/364**

## Did reclassified groups have different outcomes?

| Group | n | events | event-rate@horizon | median OS | log-rank p | HR vs rest |
|---|---|---|---|---|---|---|
| clinical_low__molecular_low | 183 | 8 | 0.03 | not_reached | 0.0 | 0.151 |
| clinical_low__molecular_high | 180 | 24 | 0.12 | not_reached | 0.0174 | 0.592 |
| clinical_high__molecular_low | 180 | 44 | 0.198 | 57.6 | 0.5465 | 1.114 |
| clinical_high__molecular_high | 183 | 76 | 0.3553 | 37.8 | 0.0 | 3.523 |
| cyto_high__molecular_low | 116 | 21 | 0.1548 | not_reached | 0.4008 | 0.821 |
| cyto_low__molecular_high | 115 | 22 | 0.1791 | not_reached | 0.8884 | 0.968 |

## Which cytogenetic subtypes showed possible gain (event-gated)?

| Subtype | n | events | Δ C-index | evidence_level |
|---|---|---|---|---|
| amp1q | 63 | 17 | +0.156 | hypothesis_generating |
| del1p | 42 | 10 | +0.090 | hypothesis_generating |
| del13q | 96 | 21 | +0.082 | hypothesis_generating |
| del17p | 22 | 10 | +0.052 | hypothesis_generating |
| t_4_14 | 24 | 6 | +0.230 | unstable_descriptive_only |
| t_11_14 | 29 | 7 | +0.098 | unstable_descriptive_only |
| t_14_16 | 8 | 2 | — | unstable_descriptive_only |
| hyperdiploid | 111 | 24 | +0.112 | hypothesis_generating |

## What can / cannot be claimed?
- technical validation: **YES**; relapse/PFS: **NO**; omics increment: **SUGGESTIVE_NOT_CONFIRMED**.
- Subtype results suggest possible omics benefit (notably amp1q, t(4;14)) but event counts are too small for confirmatory subtype claims.
