# Stage-A leak-proof OS re-baseline (open_gdc_os — OS technical validation)

- 5 patient-disjoint folds; N=726, events=152. Omics PCA fit IN-FOLD (train-only gene selection + scaling + PCA, proven in pca_fit_manifest.csv). IPCW-IBS via sksurv. Leakage audit: leakproof_leakage_audit.json.
- Honest C-index (primary k=16): clinical=0.688, clinical+omics(in-fold)=0.754, clinical+cyto+omics(in-fold)=0.747.

## Leak optimism (precomputed full-cohort PCA = legacy/diagnostic only):
  - k=8 clinical+omics: optimism +0.0033 (precomp 0.7577 vs in-fold 0.7544)
  - k=8 clinical+cyto+omics: optimism +0.0037 (precomp 0.756 vs in-fold 0.7523)
  - k=16 clinical+omics: optimism +0.0014 (precomp 0.7557 vs in-fold 0.7543)
  - k=16 clinical+cyto+omics: optimism +0.0018 (precomp 0.7489 vs in-fold 0.7471)
  - k=32 clinical+omics: optimism -0.0031 (precomp 0.744 vs in-fold 0.7471)
  - k=32 clinical+cyto+omics: optimism -0.003 (precomp 0.7396 vs in-fold 0.7426)
  - k=64 clinical+omics: optimism -0.0228 (precomp 0.714 vs in-fold 0.7368)
  - k=64 clinical+cyto+omics: optimism -0.0223 (precomp 0.7166 vs in-fold 0.7389)

- The IN-FOLD numbers are the honest baseline; precomputed full-cohort PCA is retained only as a labeled legacy/diagnostic comparison (leakage-risk).
- Subtypes: CNV-derived only (leak-free). RNA-surrogate translocations excluded from primary.
- Endpoint = OS technical validation. NO relapse/PFS claim; NO clinical-use claim.
