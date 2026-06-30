# Pre-registration — Hierarchical Subtype Survival (HSS)

Written before the full run. Carries the project invariants: patient-disjoint
splits, honest negatives are results, no fabrication, OS technical-validation only
(no relapse/PFS or clinical-use claims).

## Hypothesis
Subtype-aware self-distillation improves small-n cytogenetic-subtype **calibration**
over independent-per-subtype and pooled survival models, by letting rare subtypes
borrow strength through a shared trunk + agnostic mixture component, while the
distillation transfers the agnostic teacher's calibrated **survival curve** (not a
risk ranking) to the subtype heads.

## Model
Shared trunk f_theta: x → z. Agnostic head g_0 + per-subtype heads {g_s} over the
cytogenetic set S = {amp1q, del1p, del13q, del17p, t_4_14, t_11_14, t_14_16,
hyperdiploid}. Multi-label membership mixture: w_i = softmax(gate / temperature)
over {agnostic} ∪ {s: m_is = 1}; eta_i = Σ_k w_ik g_k(z_i). Pure-agnostic fallback
when no abnormality is called.

## Objective
L = Σ_head NLL(head's patients) + λ · Σ_s curve_distill(S_s, sg[S_0])  on subtype-s
patients, where curve_distill is the squared difference of predicted S(τ) over a
train-event-time grid. λ endpoints: λ→0 = independent heads; λ→∞ = collapse to
agnostic. The claim requires an **interior** optimum (λ swept in the full run).

## Comparators (identical patient-disjoint folds, bootstrap CIs)
independent-per-subtype · pooled/agnostic · **HSS (ours)** · old pooled-EMA "OPSD"
(the mechanism being replaced) · mmSYGNAL (external, OS-disclaimed off-endpoint).
All baselines reuse the SAME model class (n_subtypes=0) — capacity-matched.

## Metrics
- **Primary:** small-subtype IPCW integrated Brier score (IBS) / D-calibration.
- **Secondary:** C-index (global C ~0.62-ceilinged — NOT headlined).

## Decision rule / falsification
Promote HSS only if it beats BOTH independent and pooled on small-subtype IBS across
≥2 TTE heads. If HSS ≤ both on small-subtype calibration, **report the honest null.**
Do not tune to a target; the fold-0 smoke gate
(`scripts/experiments/hss_fold0_smoke.py`) is run before the full sweep.

## External validation
GEO projection (GSE24080 / GSE9782) when wired; reported as off-cohort transfer.

## Status (2026-06-30)
Fold-0 Cox smoke: directional PASS (smallest evaluable subtype del17p IBS 0.270→0.131).

5-fold Cox run (`mm-tte hss`, Stage 1) — REGIME-DEPENDENT, honest:
- HSS beats independent on the small-but-trainable subtypes: t_4_14 (100% folds),
  t_11_14 (100%), del17p (60%, clear mean win). 3/7 subtypes with ≥4 folds.
- Neutral/slightly worse at large n (del1p, amp1q, del13q, hyperdiploid) — expected
  (independent already has enough data; no borrow-strength benefit).
- Literal smallest t_14_16 (n=37): evaluable in only 2/5 folds, IBS unstable (one fold
  0.106, one fold 1.02). NOT beaten → the pre-registered promotion bar is NOT met for
  the smallest subtype. Reported as a null/characterization result, not tuned away.

Interpretation: this is the "when does cross-subtype self-distillation help vs hurt"
characterization (helps small-but-trainable, neutral at large n, too unstable at very
small n on few folds) — a defensible methods result, NOT a clean SOTA headline.
Stage-2 needed before any promotion claim: λ sweep, pooled-baseline column, bootstrap
CIs, AFT/FHT heads, PCA-in-fold, more folds so t_14_16 is evaluable.
