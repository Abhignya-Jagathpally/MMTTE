#!/usr/bin/env Rscript
# Seurat pseudobulk template for MM single-cell data.
# Input must include metadata columns linking cells to patient_id and, when available,
# sample_time_months / treatment_line / response_status. Without patient-level TTE labels,
# this output is feature-only and cannot support survival modeling.

suppressPackageStartupMessages({
  library(Seurat)
  library(Matrix)
  library(optparse)
})

option_list <- list(
  make_option(c("--input_rds"), type="character", help="Seurat object RDS"),
  make_option(c("--out_csv"), type="character", default="data/processed/sc_pseudobulk.csv"),
  make_option(c("--patient_col"), type="character", default="patient_id"),
  make_option(c("--time_col"), type="character", default="sample_time_months"),
  make_option(c("--min_cells"), type="integer", default=30)
)
opt <- parse_args(OptionParser(option_list=option_list))

obj <- readRDS(opt$input_rds)
stopifnot(opt$patient_col %in% colnames(obj@meta.data))
if (!"percent.mt" %in% colnames(obj@meta.data)) {
  obj[["percent.mt"]] <- PercentageFeatureSet(obj, pattern = "^MT-")
}
obj <- subset(obj, subset = nFeature_RNA >= 200 & nFeature_RNA <= 8000 & percent.mt <= 20)
obj <- NormalizeData(obj)
obj <- FindVariableFeatures(obj, nfeatures = 3000)
obj <- ScaleData(obj, features = VariableFeatures(obj))
obj <- RunPCA(obj, features = VariableFeatures(obj), npcs = 50)

meta <- obj@meta.data
meta$.__sample_id <- if (opt$time_col %in% colnames(meta)) {
  paste(meta[[opt$patient_col]], meta[[opt$time_col]], sep = "__")
} else {
  as.character(meta[[opt$patient_col]])
}
keep <- names(which(table(meta$.__sample_id) >= opt$min_cells))
obj <- subset(obj, cells = rownames(meta)[meta$.__sample_id %in% keep])
meta <- obj@meta.data
counts <- GetAssayData(obj, assay="RNA", slot="counts")
features <- VariableFeatures(obj)
counts <- counts[features, , drop=FALSE]

samples <- unique(meta$.__sample_id)
out <- lapply(samples, function(sid) {
  cells <- rownames(meta)[meta$.__sample_id == sid]
  pb <- Matrix::rowSums(counts[, cells, drop=FALSE])
  data.frame(sample_id=sid, gene=names(pb), count=as.numeric(pb))
})
out <- do.call(rbind, out)
dir.create(dirname(opt$out_csv), recursive=TRUE, showWarnings=FALSE)
write.csv(out, opt$out_csv, row.names=FALSE)
message("Wrote pseudobulk long table: ", opt$out_csv)
