# mmSYGNAL benchmark — unblock plan

## The only missing artifact
`data/real/mmsygnal_program_activity_0_140.csv` — the 141-program activity matrix
(columns `0..140`, one row per patient) that the mmSYGNAL glmnet risk models
consume. Everything else is in place and validated:
- model weights load and score (validated on the upstream 3-patient example),
- scoring wrapper (`run_mmsygnal.R`), schema validator, claim guardrails, comparison code.

## Exact upstream method (located)
The canonical recipe is `external/miner3/bin/miner3-survival` (official Baliga-lab
miner3):
1. `exp_data = miner.correct_batch_effects(miner.remove_null_rows(raw_tpm), True)`
   (z-score per gene; conditional `preProcessTPM`).
2. program gene-set = union of genes across the program's member regulons
   (`transcriptional_programs.json` → regulon ids → `regulons.json` → ENSG genes).
3. `miner.generateRegulonActivity(programs, exp_data, p=0.05)` → {-1,0,1} per
   program/sample, via miner's own tercile-binarized `background_df` +
   binomial-membership test. (`background_df` terciles per sample → invariant to
   monotonic per-sample transforms, so log2(TPM+1) vs "minernorm" give the same
   membership.)

Implemented in `scripts/benchmarks/build_mmsygnal_program_activity_exact.py`
using the **official miner3 functions** (not a JSON-only approximation).

## Validation status & honesty gate
- The builder **fails closed** on a degenerate matrix (all-+1 or all-0), which
  indicates a preprocessing/version mismatch.
- A non-degenerate matrix means the official method ran, but it is **not
  bit-validated** against the upstream IA12 training reference (that needs the
  original training expression, which is not distributed). Therefore the mmSYGNAL
  comparison is reported as **method-reproduced research benchmark only**.
- mmSYGNAL targets **relapse/PFS**; the GDC endpoint is **OS**. The comparison is
  OS-discrimination only — never a relapse/PFS claim for either model.

## To fully validate (future)
Run miner3 in its pinned environment on a cohort with published mmSYGNAL program
activity (e.g., the GSE19784/GSE24080 `minernorm_program.csv` validation files
shipped in the repo) and confirm bit-agreement, then lift the "not bit-validated"
caveat.
