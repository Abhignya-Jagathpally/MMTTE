# Experiment 0 framing & proposal language

## Experiment 0: open-GDC OS technical validation and residual-risk pilot
Do **not** discard the OS result; label it as Experiment 0. It proves:
- the pipeline works end-to-end on real patient-level data;
- clinical disease-burden variables (ISS, β2M, albumin, age) are strong predictors;
- matched-cohort comparison is necessary (unmatched comparisons are unfair);
- omics may contain residual signal beyond clinical;
- **OS is not sufficient for relapse/PFS claims.**

## Headline (use this language)
> In a matched open-GDC OS cohort, omics features increased the held-out C-index
> from 0.736 to 0.782 when added to clinical variables (improving in 94% of 50
> repeated stratified splits; NRI ≈ 0.40). However, the paired ΔC-index confidence
> interval overlaps zero and the endpoint is OS rather than PFS/relapse. Therefore
> the result is **hypothesis-generating evidence of molecular residual signal, not
> confirmatory evidence of clinical utility.**

## Proposal language (revised)
- **Not:** "The model predicts relapse/resistance trajectories."
  **Instead:** "The model evaluates whether molecular program activity provides
  residual progression-risk information beyond clinical disease-burden markers,
  especially within cytogenetic subtypes."
- **Not:** "Omics improves prediction."
  **Instead:** "Matched open-GDC OS analysis suggests molecular residual signal,
  motivating endpoint-correct validation on PFS, relapse, TTNT, or
  early-progression endpoints."

## Updated data-usability note
The earlier *unmatched* OS result suggested omics did not help. After enforcing
matched-cohort comparison across all modalities, clinical+omics improved the
point-estimate C-index from 0.736 to 0.782. Confidence intervals overlap and the
endpoint remains OS, so the finding supports a hypothesis of molecular residual
signal but does not yet confirm omics utility for relapse/PFS prediction.

## Evidence-level vocabulary (auto-assigned by the code)
- `confirmatory` — paired ΔC CI lower bound > 0 AND external validation available.
- `hypothesis_generating` — point ΔC > 0 but CI includes 0.
- `technical_validation_only` — endpoint is OS while the proposal targets relapse/PFS.
- `unsupported` — no positive effect.
