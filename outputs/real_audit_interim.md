# Data Usability Audit

## Gate summary
- **min_patients_50**: True
- **min_events_20**: True
- **one_row_per_patient_required**: True
- **publication_grade_subtype_modeling**: True
- **longitudinal_first_hitting_claim**: blocked unless repeated time-stamped molecular/clinical states exist before event/censoring

## Usable for
- **survival_tte**: True
- **cytogenetic_subtype_tte**: True
- **multiomic_tte**: False

## Tables
### clinical
- path: data/real/clinical_survival.csv
- n_rows: 995
- n_patients: 995
- columns: 23 columns
- duplicate_patient_rows: 0
- events: 191
- median_time: 25.6263
- missing_time: 0
- missing_event: 0
### cytogenetics
- path: data/real/cytogenetics.csv
- n_rows: 908
- n_patients: 908
- patient_overlap_with_clinical: 908
- subtype_cols: ['amp1q', 'del1p', 'del13q', 'del17p', 't_4_14', 't_11_14', 't_14_16', 'hyperdiploid']
- subtype_counts: {'amp1q': {'n': 319, 'events': 87}, 'del1p': {'n': 158, 'events': 43}, 'del13q': {'n': 452, 'events': 97}, 'del17p': {'n': 100, 'events': 30}, 't_4_14': {'n': 0, 'events': 0}, 't_11_14': {'n': 0, 'events': 0}, 't_14_16': {'n': 0, 'events': 0}, 'hyperdiploid': {'n': 562, 'events': 109}}
