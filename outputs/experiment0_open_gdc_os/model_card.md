# Model card — residual-risk TTE (open_gdc_os)

## Intended use
Research-only residual-risk estimation. Not validated for clinical deployment, patient management, or treatment selection.

## Architecture
- Production model: ResidualRiskModel = clinical Cox + molecular-residual Cox (molecular orthogonalised vs clinical; total = clinical + residual, exact).
- Parallel experimental: MultiHeadSurvivalModel (encoder + Cox/AFT/FHT); OPSD optional & claim-gated.

## Performance (held-out, matched cohort)
- clinical C=0.723; clinical+cyto+omics C=0.781
- residual decomposition: clinical 0.723 / molecular_residual 0.655 / total 0.784

## Limitations
- Endpoint is OS, not PFS/relapse; wide CIs (small test); single cohort (no external validation).
- RNA-derived drivers are PC-loading-derived, not direct gene-level causal features.
