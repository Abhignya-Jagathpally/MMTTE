# Data contract report

Endpoint: `open_gdc_os` (overall_survival) · N=995 · all_passed=True

| Check | Passed | Detail |
|---|---|---|
| clinical_present | ✅ |  |
| patient_id_present | ✅ |  |
| patient_id_unique | ✅ | 0 duplicates |
| patient_id_nonnull | ✅ |  |
| time_positive | ✅ | 0 non-positive / NaN times |
| event_binary | ✅ | values=[np.int64(0), np.int64(1)] |
| endpoint_declared | ✅ |  |
| endpoint_type_valid | ✅ | overall_survival |
| cytogenetics_provenance_present | ✅ |  |
| omics_features_numeric | ✅ |  |
| no_outcome_leak_into_features | ✅ | leaking: [] |
