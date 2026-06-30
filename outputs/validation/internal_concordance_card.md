# Internal cross-modality concordance (CoMMpass) — NOT FISH

Copy-number subtype calls vs the orthogonal RNA dosage signal they should
track. Corroborates that the CNV caller follows biology; does NOT establish
FISH-grade accuracy. AUC = how well the expression signature ranks the CNV
call; pointbiserial_r = correlation of call with signature.

| subtype | markers | direction | n | n_pos | auc | pointbiserial_r | kappa |
| --- | --- | --- | --- | --- | --- | --- | --- |
| del17p | TP53 | down | 726 | 86 | 0.557 | 0.071 | 0.077 |
| amp1q | CKS1B+MCL1+ANP32E+ILF2+PDZK1IP1 | up | 726 | 254 | 0.771 | 0.454 | 0.407 |
| del13q | RB1+DIS3 | down | 726 | 367 | 0.753 | 0.432 | 0.377 |
| del1p | CDKN2C+FAF1 | down | 726 | 131 | 0.447 | -0.058 | 0.003 |
| hyperdiploid | tri(3,5,7,9,11,15,19,21) | up | 726 | 448 | 0.536 | 0.067 | 0.038 |
