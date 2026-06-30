# Figure specifications & captions

Define the claim each figure makes BEFORE drawing. Visual style guide:
clinical = blue, cytogenetics = purple, RNA/omics/programs = green,
model/eval = gray, claim-gate/caution = orange, blocked/not-claimed = red outline,
confirmed = green ✓, hypothesis-generating = yellow ▲. Consistent labels:
Technical validation · Hypothesis-generating · Endpoint-correct validation ·
External validation · Clinical use not claimed.

---
## Fig 1 — Study overview & claim-gated design  (BioRender)
**Claim:** the project is endpoint-aware and prevents overclaiming.
Panels: (A) data sources — clinical, cytogenetics, RNA-seq, miner3/mmSYGNAL programs;
(B) matched-cohort construction; (C) residual-risk model; (D) evaluation suite;
(E) claim gate OS ≠ PFS/relapse.
**Caption:** *Endpoint-gated framework for testing molecular residual risk beyond
clinical disease burden in multiple myeloma.*

## Fig 2 — Model architecture  (FigureLabs / SVG, editable vector)
**Claim:** the model in computational terms.
Clinical encoder → clinical risk; Molecular encoder → residualized omics/cyto risk;
Total risk = clinical risk + molecular residual risk; optional neural heads
(Cox/AFT/FHT); optional OPSD stabilization (claim-gated).
**Caption:** *Clinically-anchored residual-risk decomposition: molecular features are
orthogonalized against clinical risk so the molecular term is incremental.*

## Fig 3 — Data & mmSYGNAL benchmark flow  (BioRender + vector)
**Claim:** mmSYGNAL was integrated ethically and endpoint-honestly.
RNA TPM → official miner3 preprocessing → 141 program activities → mmSYGNAL public
RDS models → mmSYGNAL OS transfer benchmark → endpoint claim card. Annotate:
mmSYGNAL native endpoint = relapse/PFS; benchmark endpoint = OS; interpretation =
off-endpoint transfer only.
**Caption:** *Reproducible, endpoint-flagged integration of the public mmSYGNAL
relapse-risk models as an off-endpoint OS comparator.*

## Fig 4 — Main OS benchmark result  (Python, scripts/figures/fig4_os_benchmark.py) ✓ generated
Horizontal bar chart of same-cohort OS C-index. Off-endpoint mmSYGNAL bars orange.
**Caption:** *Same-cohort open-GDC OS discrimination (N_test=182, 38 events).
clinical+omics is strongest; mmSYGNAL (relapse/PFS model) transfers weakly to OS.
Off-endpoint comparators are not a same-task ranking.*

## Fig 5 — Molecular residual-risk reclassification  (Python) ✓ generated
A clinical×residual tertile heatmap; B up/down counts; C KM clinical-low/molecular-high
vs -low; D reclassification-group HRs.
**Caption:** *Molecular residual risk re-stratifies patients within clinical strata
(hypothesis-generating on OS); clinical-low/molecular-high patients show worse OS.*

## Fig 6 — Claim-gated evidence ladder  (FigureLabs / BioRender)
Technical validation ✓ (current OS run) · Hypothesis-generating ✓ (molecular residual
signal) · Endpoint-correct validation ⏳ (controlled PFS/relapse) · External validation
⏳ · Clinical deployment ❌ (not claimed).
**Caption:** *Evidence ladder. The current open-GDC OS study supports technical
validation and a hypothesis; biological/clinical claims await endpoint-correct data.*

---
## S1 — Cohort construction (CONSORT-style)
Open-GDC patients → with OS → with cytogenetics → with RNA → matched cohort → split.
## S2 — Leakage audit
train-only imputation/scaling/residualization; no test outcome used for fitting.
## S3 — mmSYGNAL program-activity validation  (Python) ✓ generated
{-1,0,1} distribution ours vs example; per-program mean; subtype-selection counts.
## S4 — Repeated-split stability  (Python) ✓ generated
50-split C-index distribution; paired ΔC; fraction of splits improved.
