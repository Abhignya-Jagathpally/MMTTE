# v12 → v20 Critical Audit

## v12-audit-reports / ResistanceMap

**Usable assets**
- Good reproducibility posture: README, paper tables, evaluation governance, baseline comparison, actionability matrix, and explicit failure modes.
- Real cell-line data path: CCLE proteomics, epigenomics, STRING PPI, and GDSC IC50 are suitable for drug-screening/ranking experiments.
- Strong negative-control value: the branch explicitly states that it is not patient-level treatment-response, relapse, or time-to-resistance prediction.

**Not usable for this TTE objective without redesign**
- Cell-line IC50 labels are not right-censored patient events.
- No patient-level time, censoring, or relapse/progression event table is wired into the running objective.
- No repeated molecular snapshots exist in the training tuples, so first-hitting-time trajectory claims would be unsupported.
- Attention/pathway modules are not enough unless their predictions are persisted and externally validated against perturbational or target evidence.

## v20 / ResistanceMap

**Usable assets**
- Medallion/lakehouse design: raw → cleansed → curated → confirmed is the correct data-governance direction.
- Patient-disjoint splits and explicit censoring guardrails are necessary for TTE modeling.
- TT2L survival proxy and z64 patient latents make the branch much closer to a real survival pipeline than v12.
- v20 already frames incompatible tasks separately: survival-proxy prediction, short-term response classification, cell-state trajectory forecasting, and pathway evidence.

**Remaining blockers**
- TT2L is a treatment-transition proxy, not direct relapse/resistance.
- The reported RSF C-index near 0.96 should be treated as a leakage/split/proxy-audit trigger until independently reproduced under frozen patient-disjoint splits.
- Longitudinal molecular trajectory prediction remains blocked unless controlled-access CoMMpass/dbGaP or MMRF VLab longitudinal molecular snapshots are joined.
- Survival baselines need a clean, comparable experiment surface: clinical-only Cox, subtype-only, Cox on molecular PCs, MOFA/mmSYGNAL factors + Cox, RSF, AFT, FHT, and neural OPSD variants.

## Direction taken in this clean repo

This repo narrows the claim to: **cytogenetic subtype-aware TTE risk modeling in MM**, with CoxPH, log-normal AFT, inverse-Gaussian first-hitting-time models, and on-policy self-distillation. It does not claim true resistance-state trajectory prediction unless repeated pre-event molecular states are present.
