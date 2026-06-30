# Subtype-label validation (methods + results)

**Question.** Are the sequencing-inferred cytogenetic subtype labels trustworthy?
This is the precondition for *any* subtype-conditioned result (positive or null).
No FISH exists for the open CoMMpass cohort — MMRF seqFISH is controlled-access — so
trust is established with a layered, strictly-open-data stack. **Nothing here is
synthetic; every number derives from real public data.**

Run it all: `mm-tte validate-subtypes`
(outputs in `outputs/validation/`, consolidated `subtype_validation_summary.md`).

## Label provenance (what is being validated)

- **CNV subtypes** `amp1q, del1p, del13q, del17p, hyperdiploid` — GDC copy-number
  segments, length-weighted arm log2 vs per-sample baseline (gain +0.10 / loss −0.25,
  ≥30% coverage). Confidence: *moderate*.
- **Translocations** `t_4_14, t_11_14, t_14_16` — RNA-expression surrogates (max
  marker z over the cohort, thresholded at literature prevalence;
  `validation/surrogate_caller.py`, shared with the production build). Confidence:
  *exploratory*, explicitly **NOT FISH**.

## Layer 1 — External real FISH (GSE6477, Affymetrix U133A)

Genuine interphase FISH for **del(13)** and **hyperdiploidy** (the only two cytogenetic
calls available per-sample in open GEO). We build an expression dosage signature
(−chr13 mean for del(13); trisomy-chromosome mean for hyperdiploidy) and score it
against FISH. Cross-platform caveat: this validates an *expression* detector on a
*different array* than CoMMpass, not the CoMMpass CNV caller itself.

| subtype | n | AUC | sens | spec | κ |
|---|---|---|---|---|---|
| del(13) | 162 | 0.85 | 0.77 | 0.86 | 0.63 |
| hyperdiploid | 162 | 0.73 | 0.66 | 0.74 | 0.40 |

## Layer 2 — External cluster concordance (GSE19784, U133 Plus 2.0; NOT FISH)

The HOVON-65 cohort exposes the published **molecular cluster** (transcriptome-derived):
MS = t(4;14), MF = t(14;16), CD-1/CD-2 = t(11;14). We run the **exact deployed
surrogate caller** and measure concordance with the cluster. This is concordance, not
FISH (the gold standard is itself expression-derived), but it tests whether our minimal
1–3-gene caller recovers the established full-transcriptome classification.

| translocation | AUC | κ | verdict |
|---|---|---|---|
| t(11;14) (CCND1) | 0.94 | 0.70 | recovers cluster well |
| t(4;14) (NSD2/FGFR3) | 0.99 | 0.76 | recovers cluster well |
| t(14;16) (MAF) | **0.49** | 0.13 | **fails** — single-MAF caller misses the MAFB-inclusive MF cluster |

## Layer 3 — Internal cross-modality concordance (CoMMpass; NOT FISH)

CoMMpass CNV calls vs the orthogonal RNA dosage they should track
(`gene_matrix.npz`): del(17p)↔TP53↓, amp(1q)↔CKS1B/MCL1↑, del(13q)↔RB1/DIS3↓,
del(1p)↔CDKN2C/FAF1↓, hyperdiploid↔trisomy-chromosome mean.

| subtype | AUC | point-biserial r | reading |
|---|---|---|---|
| amp(1q) | 0.77 | 0.45 | strong corroboration |
| del(13q) | 0.75 | 0.43 | strong corroboration |
| del(17p) | 0.56 | 0.07 | weak — *expected*: hemizygous 17p loss barely lowers TP53 mRNA |
| del(1p) | 0.45 | −0.06 | weakest — most uncertain label |
| hyperdiploid | 0.54 | 0.07 | weak internally (better externally, AUC 0.73) |

## Layer 4 — Label-noise robustness (the "your labels might be wrong" rebuttal)

Flip each CNV subtype at its published sequencing-vs-FISH discordance rate (del17p
0.11, amp1q/del13q/del1p 0.29–0.30, hyperdiploid 0.10) over many draws and re-run the
pooled-vs-subtype-specific comparison. **Result: in 95% of draws pooled penalised Cox
remains no worse than subtype-specific modelling** → the subtype-aware NULL is not an
artifact of imperfect labels. (`mm-tte label-noise`.)

## Layer 5 — Literature concordance + FISH-ready harness

del(17p)/amp(1q)/del(1p) have no open FISH; their accuracy rests on
`docs/literature_cnv_fish_concordance.md` (custom-capture NGS vs FISH >99%/>99% for
gains/losses; del(17p) sensitivity variable due to subclonality). A FISH-ready harness
(`validation/fish_ready.py`) computes genuine per-subtype sens/spec/κ the instant a
controlled-access CoMMpass FISH file is supplied (`paths.fish`).

## Bottom line

The labels carry **real biology** (external FISH + cluster + internal all positive for
the well-powered lesions), so the Stage-D subtype-aware null is a **genuine null**, and
it is **robust to realistic label noise**. Claims are scoped accordingly: del(13)
best-supported, del(17p) trust FISH-literature not expression, **del(1p) and t(14;16)
most uncertain**. Residual limitation stated plainly: *CoMMpass calls are not validated
against CoMMpass FISH.* Framing: `docs/FRAMING_SUBTYPE_AWARE_NULL.md`.

_Endpoint = OS technical validation only. No relapse/PFS or clinical-use claims._
