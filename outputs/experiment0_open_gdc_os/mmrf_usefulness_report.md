# MMRF usefulness report

- Patients reclassified by omics: **276** (up 135 / down 141)
- Clinically standard-risk but molecularly HIGH: **161**
- Cytogenetic high-risk but molecularly LOWER: **120/364**

## Did reclassified groups have different outcomes?

| Group | n | events | event-rate@horizon | median OS | log-rank p | HR vs rest |
|---|---|---|---|---|---|---|
| clinical_low__molecular_low | 175 | 7 | 0.0223 | not_reached | 0.0 | 0.134 |
| clinical_low__molecular_high | 188 | 24 | 0.1188 | not_reached | 0.0178 | 0.593 |
| clinical_high__molecular_low | 188 | 42 | 0.17 | 57.6 | 0.7222 | 0.937 |
| clinical_high__molecular_high | 175 | 79 | 0.4025 | 32.3 | 0.0 | 4.2 |
| cyto_high__molecular_low | 107 | 19 | 0.1507 | not_reached | 0.282 | 0.768 |
| cyto_low__molecular_high | 106 | 23 | 0.247 | not_reached | 0.3307 | 1.246 |

## Which cytogenetic subtypes showed possible gain (event-gated)?

| Subtype | n | events | Δ C-index | evidence_level |
|---|---|---|---|---|
| amp1q | 67 | 19 | +0.193 | hypothesis_generating |
| del1p | 25 | 3 | — | unstable_descriptive_only |
| del13q | 94 | 23 | +0.122 | hypothesis_generating |
| del17p | 20 | 7 | +0.442 | unstable_descriptive_only |
| t_4_14 | 28 | 7 | +0.172 | unstable_descriptive_only |
| t_11_14 | 25 | 4 | — | unstable_descriptive_only |
| t_14_16 | 14 | 4 | — | unstable_descriptive_only |
| hyperdiploid | 114 | 23 | +0.079 | hypothesis_generating |

## What can / cannot be claimed?
- technical validation: **YES**; relapse/PFS: **NO**; omics increment: **SUGGESTIVE_NOT_CONFIRMED**.
- Subtype results suggest possible omics benefit (notably amp1q, t(4;14)) but event counts are too small for confirmatory subtype claims.
