# mmSYGNAL program-activity: method reproduction record

## What was reproduced
The 141-program activity matrix (`data/real/mmsygnal_program_activity_0_140.csv`,
787 patients × programs 0..140) consumed by the mmSYGNAL glmnet risk models, built
with the **official baliga-lab/miner3 package** (not a JSON-only approximation).

## Exact pipeline (mirrors `external/miner3/bin/miner3-survival`)
1. Raw STAR `tpm_unstranded` per gene (ENSEMBL, version-stripped) × patient.
2. `raw = miner.remove_null_rows(raw)`.
3. `exp_data = miner.correct_batch_effects(raw, do_preprocess_tpm=True)`
   — per-sample median-scale to 1023 (`preProcessTPM`) + per-gene z-score.
4. Program gene-set = union of genes across the program's member regulons
   (`transcriptional_programs.json` → regulon ids → `regulons.json` → ENSEMBL).
5. `activity = miner.generateRegulonActivity(genesets, exp_data, p=0.05)`
   → {-1,0,1} per program/sample (tercile-binarized `background_df` + binomial
   membership test, all miner3-internal).
6. Transpose → patients × 141, columns `0..140`.

Script: `scripts/benchmarks/build_mmsygnal_program_activity_exact.py` (fail-closed
on degenerate output).

## Validation evidence
- Output distribution: **mean 0.20, balanced {-1,0,1}** (frac −1/0/+1 = 0.10/0.61/0.30),
  matching the upstream 3-patient example (`data/patient_program_activity.csv`,
  mean 0.24). The earlier degenerate results (all-+1 without `preProcessTPM`, all-0
  with naïve z-score) were resolved once the **complete official preprocessing** was
  applied — `preProcessTPM` was the decisive missing step.
- Mean program gene coverage in our RNA: 0.965.
- Schema-valid (passes `validate_mmsygnal_program_activity`).
- mmSYGNAL risk scores span 0.13–0.72 (not degenerate); 474/787 patients receive a
  subtype model, 313 the agnostic model.

## Honesty boundary
**Method-reproduced, NOT bit-validated** against the upstream IA12 training reference
(that requires the original training expression, which is not distributed). The
mmSYGNAL comparison is therefore reported as an **OS-discrimination research benchmark
only**; mmSYGNAL's native endpoint is relapse/PFS. To fully validate, run miner3 in
its pinned environment against a cohort with published mmSYGNAL program activity
(e.g. the repo's `GSE19784/GSE24080 minernorm_program.csv`) and confirm bit-agreement.

## Provenance / licensing
miner3 and mmSYGNAL are GPL-3.0, cloned to `external/` and **not vendored** (gitignored).
The network-derived program-activity matrix is also gitignored (not redistributed).
See `docs/third_party/mmSYGNAL_provenance.md` and the SHA256 manifest.
