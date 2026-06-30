#!/usr/bin/env bash
set -euo pipefail
# Template for controlled WGS/WXS genotype QC. PLINK is appropriate for SNP-like
# genotype matrices; cytogenetic events such as del17p/t(4;14)/amp1q usually come
# from clinical FISH/CNV/fusion calls and should be merged as patient-level features.
# Replace paths with controlled-access data locations after dbGaP/GDC authorization.

BED_PREFIX=${1:-data/controlled/mmrf_genotypes}
OUT_PREFIX=${2:-data/processed/plink_qc/mmrf}
mkdir -p "$(dirname "$OUT_PREFIX")"
plink \
  --bfile "$BED_PREFIX" \
  --geno 0.05 \
  --mind 0.10 \
  --maf 0.01 \
  --hwe 1e-6 \
  --make-bed \
  --out "$OUT_PREFIX"
