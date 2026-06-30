# Experiment 1 — RNA PCA vs official miner3/mmSYGNAL program activity (OS)

**Question:** are biologically-structured miner3/mmSYGNAL programs better than generic
RNA PCs in the residual-risk framework, on OS?

**Design:** same matched cohort, same stratified split, same OS endpoint; feature-count
matched — **16 RNA PCs vs 16 top-variance miner3 programs**. Script:
`scripts/analysis/program_vs_pca_ablation.py`. Outputs: `program_vs_pca_ablation.csv`,
`program_vs_pca_paired_delta.csv`, `program_vs_pca_calibration.csv`,
`program_vs_pca_claim_card.md`.

## Result (held-out OS, N_test=182 / 38 events)
| Feature set | #feat | OS C-index |
|---|---|---|
| clinical | 7 | 0.723 |
| clinical+RNA_PCA | 23 | **0.783** |
| clinical+miner3_programs | 23 | 0.694 |
| clinical+cyto+RNA_PCA | 31 | 0.781 |
| clinical+cyto+miner3_programs | 31 | 0.709 |
| clinical+cyto+RNA_PCA+miner3_programs | 47 | 0.751 |

**Paired ΔC (same patients):**
- miner3 programs vs RNA PCA: ΔC **−0.089** (CI −0.143…−0.037) — RNA PCA significantly better.
- +cyto variant: ΔC −0.072 (CI −0.122…−0.020) — same direction, CI-separated.
- adding PCA on top of programs: +0.043 (CI +0.001…+0.086) — confirmed.

## Interpretation (honest)
On **OS**, generic continuous RNA PCs outperform the 16 top-variance miner3 programs in
this framework (CI-separated). Two caveats: (1) miner3 program activity is {-1,0,1}
(3-level, lower information than continuous PCs); (2) miner3/mmSYGNAL programs are
optimized for **relapse/PFS**, so this is an **off-endpoint** disadvantage for programs —
the result does NOT imply programs are worse for their native endpoint. The endpoint-correct
test (PFS/relapse) is the fair comparison and remains pending (E3).

**Claim scope:** OS technical validation. No relapse/PFS or clinical-use claim.
