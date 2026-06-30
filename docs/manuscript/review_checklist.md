# Internal review loop (5 reviewers) — pre-submission checklist

Run before finalizing. Each reviewer signs off or files blocking issues.

## Reviewer 1 — Clinical relevance
- [ ] Is OS-vs-PFS/relapse distinction explicit throughout?
- [ ] Are reclassification groups clinically meaningful (clinical-low/molecular-high)?
- [ ] Are limitations of CNV-derived cytogenetics & RNA-surrogate translocations stated?

## Reviewer 2 — Statistical validity
- [ ] Same patients / same split for fitted comparators? (matched cohort)
- [ ] Paired ΔC (not separate-CI overlap) used for omics-vs-clinical?
- [ ] Repeated-split stability + CIs reported, not a single lucky split?
- [ ] Calibration/Brier, DCA, NRI/IDI reported; small-event caveat stated?
- [ ] No OS C-index ranked against PFS/risk metrics without warning?

## Reviewer 3 — Computational reproducibility
- [ ] Pipeline runs via `main.py`; data fetchable from GDC scripts?
- [ ] leakage_audit.json: train-only impute/scale/residualize, no test leakage?
- [ ] mmSYGNAL provenance + SHA256 manifest; weights not vendored (GPL-3.0)?
- [ ] Figures regenerate from CSVs (`make figures`)?

## Reviewer 4 — Biological interpretation
- [ ] Residual-risk drivers labelled as PC-loading-derived (not direct causal genes)?
- [ ] mmSYGNAL program activity = method-reproduced, NOT bit-validated — stated?
- [ ] Subtype "gains" framed as hypothesis-generating (event counts too small)?

## Reviewer 5 — Claim discipline (BLOCKING)
- [ ] No "beats SOTA" / superiority-over-mmSYGNAL language anywhere?
- [ ] Required-framing sentence present where superiority is implied?
- [ ] Claim card: technical_validation YES, relapse/PFS NO, clinical-use NO?
- [ ] CI language guardrail passes (no relapse/PFS/clinical-decision terms on OS run)?
- [ ] Evidence ladder shows endpoint-correct + external validation as PENDING?

## Revision actions
- Move unsupported biology to Limitations.
- Tighten Discussion; remove any overstatement.
- Finalize figures + reproducibility supplement (data + model manifests).
- Prepare preprint/conference version (framework + technical-validation paper).
