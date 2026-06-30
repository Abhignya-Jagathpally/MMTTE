# mmSYGNAL third-party model provenance

Source repository: https://github.com/baliga-lab/mmSYGNAL-risk-prediction-models
License: GPL-3.0
Commit: 6017dd8d4210ef65433208dadca80afb6cad8e98
Use in this project: research benchmarking only.
Model artifacts are NOT vendored in this repository by default.
Users must clone the upstream repository themselves or provide a local path.

## Artifacts used
- data/agnostic_risk_model.Rds
- data/amp(1q)_risk_model.Rds
- data/del(13)_risk_model.Rds
- data/del(1p)_risk_model.Rds
- data/t(4;14)_risk_model.Rds
- data/FGFR3_risk_model.Rds

Model type: caret `train` objects (glmnet), scored via
`predict(model, newdata, type="prob")$high`. Input = 141 mmSYGNAL program
activities labelled 0..140 (one row per patient). Risk grades for subtype
selection: t(4;14)=A, FGFR3=A, amp(1q)/del(13)/del(1p)=B, agnostic=C.
Risk thresholds: <0.5 low, [0.5,0.6) high, >=0.6 extreme.

## Claim policy
- mmSYGNAL scores may be used as an external comparator only.
- Results must be endpoint-matched (same patients, same OS endpoint).
- Open-GDC OS comparisons CANNOT be described as relapse/PFS validation.
- Clinical-use claims are not permitted.

## Redistribution
- Not vendored by default (avoids carrying GPL-3.0 obligations into this repo's
  distribution). Reproducibility is provided via the SHA256 manifest at
  outputs/benchmarks/mmSYGNAL/model_artifact_manifest.csv.

## IMPORTANT — program-activity prerequisite
mmSYGNAL requires the 141-program activity matrix produced by the mmSYGNAL/MINER
inference pipeline (Wall et al., Precision Oncology 2021) applied to the patient
RNA. This repository's `data/real/program_activity.csv` contains 10 curated MM
signatures (a different, interpretable feature set) and MUST NOT be fed to the
mmSYGNAL models. Generic RNA PCs MUST NOT be fed either. Scoring the GDC cohort
therefore requires first generating mmSYGNAL program activity (0..140) upstream;
that step is not reproduced here. The wrapper is validated on the upstream
3-patient example (`data/patient_program_activity.csv`).
