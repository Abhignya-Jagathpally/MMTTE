# Sequencing-vs-FISH concordance for MM copy-number calls (literature)

Our CoMMpass subtype labels are **sequencing-inferred**: CNV calls come from GDC
copy-number segments, not interphase FISH. del(17p), amp(1q) and del(1p) have no
open-data FISH for direct validation (GSE6477 covers only del(13)+hyperdiploidy;
GSE19784 covers translocation *clusters*). This table records the field-measured
accuracy of sequencing-derived CNV calls against FISH so the CoMMpass calls can be
contextualized honestly and the label-noise robustness flip-rates
(`experiments_label_noise.FLIP_RATE`) are grounded in real numbers rather than
guesses.

> Attribution: the primary head-to-head figures below are from PubMed-indexed
> literature; the anchor study is cited with its DOI.

## Anchor study (custom-capture NGS vs FISH + SNP array, MM)

According to PubMed — Yellapantula V, Hultcrantz M, Rustad EH, … Zhang Y,
Landgren O. *Comprehensive detection of recurring genomic abnormalities: a
targeted sequencing approach for multiple myeloma.* Blood Cancer J. 2019;9(12):101.
[DOI](https://doi.org/10.1038/s41408-019-0264-y) (PMID 31827071).

- Custom-capture NGS panel, **154 plasma-cell-disorder patients**, head-to-head vs
  clinical **FISH** and **SNP microarray**.
- **>99% sensitivity and >99% specificity** for IGH translocations and the relevant
  chromosomal gains and losses.
- Additionally captured bi-allelic TP53 events not seen by FISH — i.e. sequencing
  can *exceed* FISH for some lesions.

## Reported concordance varies by lesion and platform

The key honest point: concordance is **high for gains/large losses** but **lower and
more variable for del(17p)**, because del(17p) is frequently **subclonal** and
sequencing sensitivity depends on clonal fraction and depth. Across panel/NGS-vs-FISH
studies, reported figures span roughly:

| Lesion | Reported sequencing-vs-FISH behaviour | Implication for our labels |
|---|---|---|
| gain/amp(1q) | high sens & spec (≈0.90–0.99 in capture panels) | amp1q calls trustworthy; corroborated internally (AUC 0.77) |
| del(13)/monosomy 13 | high sens & spec (≈0.90–0.99) | best-supported; external FISH AUC 0.85 + internal AUC 0.75 |
| t(4;14), t(11;14) | high (IGH-translocation detection ≈0.99 in anchor study) | surrogate recovers clusters well (AUC 0.94/0.99) |
| del(17p) | **specificity high, sensitivity variable / often under-called** (subclonal) | trust FISH-literature, NOT expression; scope firm claims here but flag under-call |
| del(1p) | less frequently benchmarked | weakest open support (internal AUC 0.45); most exploratory |

Cross-malignancy context (CLL targeted sequencing vs FISH) reports del(17p) ≈0.99
and del(13q) ≈0.90 concordance, consistent with the MM picture that focal/large CNVs
are well captured: [PMC11240685](https://pmc.ncbi.nlm.nih.gov/articles/PMC11240685/).

## How this feeds the validation stack

- **Flip rates** (`FLIP_RATE`): del(17p) 0.11 (under-call dominated), amp(1q)/del(13)
  0.29–0.30 (to stress-test even the well-concordant lesions hard), hyperdiploid 0.10,
  del(1p) 0.30 (most uncertain). The label-noise experiment shows the subtype-aware
  **NULL survives** these perturbations (`outputs/validation/label_noise/`).
- **Claim scoping**: firm statements are anchored to del(13) (external FISH + internal)
  and del(17p) (literature specificity), translocations kept exploratory, del(1p)
  flagged most uncertain. See `docs/FRAMING_SUBTYPE_AWARE_NULL.md`.

_Endpoint = OS technical validation only. No relapse/PFS or clinical-use claims._
