# MMRF usefulness report

- Patients reclassified by omics: **300** (up 140 / down 160)
- Clinically standard-risk but molecularly HIGH: **158**
- Cytogenetic high-risk but molecularly LOWER: **109/351**

## Did reclassified groups have different outcomes?

| Group | n | events | event-rate@horizon | median OS | log-rank p | HR vs rest |
|---|---|---|---|---|---|---|
| clinical_low__molecular_low | 186 | 10 | 0.0414 | not_reached | 0.0 | 0.197 |
| clinical_low__molecular_high | 177 | 26 | 0.1414 | not_reached | 0.0612 | 0.67 |
| clinical_high__molecular_low | 177 | 42 | 0.1775 | not_reached | 0.9392 | 0.986 |
| clinical_high__molecular_high | 186 | 74 | 0.3498 | 37.8 | 0.0 | 3.369 |
| cyto_high__molecular_low | 101 | 18 | 0.1409 | not_reached | 0.2638 | 0.756 |
| cyto_low__molecular_high | 113 | 23 | 0.1993 | not_reached | 0.9152 | 1.024 |

## Which cytogenetic subtypes showed possible gain (event-gated)?

| Subtype | n | events | Δ C-index | evidence_level |
|---|---|---|---|---|
| amp1q | 63 | 17 | +0.191 | hypothesis_generating |
| del1p | 42 | 10 | +0.055 | hypothesis_generating |
| del13q | 96 | 21 | +0.041 | hypothesis_generating |
| del17p | 22 | 10 | +0.013 | hypothesis_generating |
| t_4_14 | 24 | 6 | +0.189 | unstable_descriptive_only |
| t_11_14 | 29 | 7 | +0.098 | unstable_descriptive_only |
| hyperdiploid | 111 | 24 | +0.095 | hypothesis_generating |

## What can / cannot be claimed?
- technical validation: **YES**; relapse/PFS: **NO**; omics increment: **SUGGESTIVE_NOT_CONFIRMED**.
- Subtype results suggest possible omics benefit (notably amp1q, t(4;14)) but event counts are too small for confirmatory subtype claims.
