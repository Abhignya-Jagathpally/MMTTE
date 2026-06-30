# What this result means for MMRF / the MM community

This pipeline is an **endpoint-gated, reproducible** way to ask whether molecular
program activity adds progression-risk information beyond clinical disease-burden
markers — without overclaiming. On the open-GDC **overall-survival** pilot
(Experiment 0, matched cohort N=726) it already produces community-relevant
outputs:

1. **Flags clinically standard-risk patients with molecular high-risk patterns.**
   158 patients in the matched cohort sit in low/mid clinical-risk tertiles but
   top molecular-residual tertile. Outcome validation shows these
   *clinical-low / molecular-high* patients have a markedly higher event rate
   (~0.14 by 24 mo) than *clinical-low / molecular-low* patients (~0.04) — i.e.
   the molecular residual identifies occult risk the clinical staging misses.

2. **Identifies cytogenetic high-risk patients whose molecular profile suggests
   lower relative risk.** 109/351 cytogenetic high-risk patients fall below the
   median total risk — candidates for de-escalation hypotheses (to be tested on a
   relapse/PFS endpoint, not OS).

3. **Supports closer-monitoring and trial-referral hypotheses**, with explicit
   per-group event rates, KM curves, log-rank p, and hazard ratios
   (`mmrf_reclassification_outcomes.csv`) so reclassification is only ever claimed
   when outcomes actually differ.

4. **Avoids overclaiming OS as relapse biology.** The endpoint registry hard-gates
   claims: an OS run can never license a relapse/PFS or primary biological claim
   (`claim_report.json`, `endpoint_gate_report.md`).

5. **Creates a reproducible, endpoint-correct substrate for future controlled
   MMRF data.** Swap the endpoint to `controlled_commpass_pfs` and re-run; the
   same matched-cohort, paired-ΔC, calibration, DCA and NRI/IDI machinery applies
   and the claim gates open only when the endpoint and external validation justify
   it.

## Current honest status
Hypothesis-generating evidence of molecular residual signal on OS (improves in
94% of 50 repeated splits; NRI ≈ 0.40; better Brier and decision-curve net
benefit), **not** confirmatory evidence of clinical utility. Confirmation requires
a relapse/PFS/TTNT endpoint and external validation.
