# Leak delta — precomputed full-cohort PCA vs in-fold PCA

Positive optimism = the legacy precomputed PCA overstates the omics C-index.

- k=8 clinical+omics: C precomp=0.7577 vs in-fold=0.7544 -> optimism +0.0033
- k=8 clinical+cyto+omics: C precomp=0.756 vs in-fold=0.7523 -> optimism +0.0037
- k=16 clinical+omics: C precomp=0.7557 vs in-fold=0.7543 -> optimism +0.0014
- k=16 clinical+cyto+omics: C precomp=0.7489 vs in-fold=0.7471 -> optimism +0.0018
- k=32 clinical+omics: C precomp=0.744 vs in-fold=0.7471 -> optimism -0.0031
- k=32 clinical+cyto+omics: C precomp=0.7396 vs in-fold=0.7426 -> optimism -0.003
- k=64 clinical+omics: C precomp=0.714 vs in-fold=0.7368 -> optimism -0.0228
- k=64 clinical+cyto+omics: C precomp=0.7166 vs in-fold=0.7389 -> optimism -0.0223
