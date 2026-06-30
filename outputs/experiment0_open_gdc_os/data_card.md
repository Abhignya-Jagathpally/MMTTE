# Data card — open_gdc_os

- Matched cohort: **726** patients (all modalities), test events 38
- Endpoint: overall_survival (OS — progression/PFS not in open GDC clinical)
- Clinical features: 7 · cytogenetics: 8 (SEQUENCING-INFERRED, NOT FISH; see cytogenetics_provenance.csv) · omics PCs: 16 · programs: 10
- Provenance (all sequencing-inferred, NOT FISH): amp1q/del1p/del13q/del17p/hyperdiploid = GDC copy-number segments; t(4;14)/t(11;14)/t(14;16) = RNA expression surrogates. Externally FISH-validated only for del13/hyperdiploid (GSE6477); see docs/subtype_label_validation.md.
- Preprocessing: train-only impute/scale; omics PCA unsupervised on full RNA cohort.
- Splits: stratified-by-event, patient-disjoint.
