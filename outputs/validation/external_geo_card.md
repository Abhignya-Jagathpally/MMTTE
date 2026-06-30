# External subtype-label validation (open GEO)

Real FISH ground truth exists on open data only for del(13) and hyperdiploidy
(GSE6477); translocations are validated against the published expression
*cluster* (GSE19784), which is concordance, NOT raw FISH. del(17p)/amp(1q)/
del(1p) have no open FISH and rely on docs/literature_cnv_fish_concordance.md.

## Real-FISH validation (GSE6477)
| dataset | subtype | gold | n | n_pos | auc | sens | spec | ppv | kappa |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GSE6477 | del13q | FISH | 162 | 61 | 0.846 | 0.770 | 0.861 | 0.770 | 0.632 |
| GSE6477 | hyperdiploid | FISH | 162 | 70 | 0.730 | 0.657 | 0.739 | 0.657 | 0.396 |

## Expression-cluster concordance (GSE19784, NOT FISH)
| dataset | subtype | gold | n | n_pos | auc | sens | spec | ppv | kappa |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| GSE19784 | t_11_14 | molecular_cluster | 328 | 47 | 0.942 | 0.745 | 0.957 | 0.745 | 0.702 |
| GSE19784 | t_4_14 | molecular_cluster | 328 | 33 | 0.991 | 0.788 | 0.976 | 0.788 | 0.764 |
| GSE19784 | t_14_16 | molecular_cluster | 328 | 32 | 0.489 | 0.219 | 0.916 | 0.219 | 0.134 |
