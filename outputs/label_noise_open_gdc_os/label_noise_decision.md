# Label-noise robustness (OS technical validation)

CNV subtype labels flipped at published sequencing-vs-FISH discordance rates (del17p 0.11, amp1q 0.29, del13q/del1p 0.30, hyperdiploid 0.10).

Per subtype: pooled penalised-Cox IPCW-IBS under real vs flipped labels, and the fraction of noise draws in which pooled Cox is NOT worse than subtype-specific Cox.

| subtype | real_ibs_pooled | flip_ibs_pooled_mean | flip_ibs_pooled_sd | frac_draws_pooled_not_worse |
| --- | --- | --- | --- | --- |
| amp1q | 0.1432 | 0.1349 | 0.0256 | 0.96 |
| del1p | 0.1663 | 0.1347 | 0.0257 | 0.96 |
| del13q | 0.1429 | 0.1329 | 0.0202 | 1.0 |
| del17p | 0.1504 | 0.1365 | 0.0324 | 0.84 |
| hyperdiploid | 0.1283 | 0.1294 | 0.0173 | 1.0 |

Mean fraction pooled-not-worse across subtypes = 0.952 (robust threshold 0.80).

## VERDICT: ROBUST
ROBUST: under realistic label noise, pooled penalised Cox remains no worse than subtype-specific modelling -> the subtype-aware NULL is not a label-noise artifact.

- Endpoint = OS technical validation. NO relapse/PFS claim; NO clinical-use claim.
