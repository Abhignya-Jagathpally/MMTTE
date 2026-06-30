#!/usr/bin/env Rscript
# Main Figure 5 (publication) — molecular residual-risk reclassification WITHIN
# clinical-risk strata. Built in R/ggplot2 + survival (survminer not required).
#
# Replaces the misleading "HR vs rest" panel with within-stratum contrasts:
#   clinical-low : molecular-high vs molecular-low
#   clinical-high: molecular-high vs molecular-low
#
# Outputs: figures/final/fig5_within_stratum_km.pdf
#          figures/final/fig5_within_stratum_forest.pdf

suppressPackageStartupMessages({ library(readr); library(dplyr); library(ggplot2); library(survival) })

root <- normalizePath(file.path(dirname(sub("--file=", "", grep("--file=", commandArgs(FALSE), value=TRUE))), "..", ".."))
D <- file.path(root, "outputs", "experiment0_open_gdc_os")
outdir <- file.path(root, "figures", "final"); dir.create(outdir, showWarnings=FALSE, recursive=TRUE)

# style guide colours
col_low  <- "#2e8b57"   # molecular-low  (green)
col_high <- "#e08214"   # molecular-high (orange/caution)

dec <- read_csv(file.path(D, "residual_risk_decomposition.csv"), show_col_types=FALSE)
tcol <- if ("time_months" %in% names(dec)) "time_months" else names(dec)[3]
dec$t <- as.numeric(dec[[tcol]]); dec$e <- as.integer(dec$event)
dec$clinical <- ifelse(rank(dec$clinical_risk)/nrow(dec) > 0.5, "clinical-high", "clinical-low")
dec$molecular <- ifelse(rank(dec$molecular_residual_risk)/nrow(dec) > 0.5, "molecular-high", "molecular-low")

# ---- KM curves, faceted by clinical stratum ----
km_df <- function(sub, stratum) {
  fit <- survfit(Surv(t, e) ~ molecular, data = sub)
  st <- summary(fit)
  grp <- rep(names(fit$strata), fit$strata)
  data.frame(time = st$time, surv = st$surv,
             molecular = sub("molecular=", "", grp[match(st$time, st$time)]),
             stratum = stratum)
}
# build step data robustly per group
mk <- function(sub, stratum) {
  do.call(rbind, lapply(split(sub, sub$molecular), function(g) {
    f <- survfit(Surv(t, e) ~ 1, data = g)
    rbind(data.frame(time=0, surv=1, molecular=g$molecular[1], stratum=stratum),
          data.frame(time=f$time, surv=f$surv, molecular=g$molecular[1], stratum=stratum))
  }))
}
kmdat <- rbind(mk(filter(dec, clinical=="clinical-low"), "clinical-low"),
               mk(filter(dec, clinical=="clinical-high"), "clinical-high"))
kmdat$stratum <- factor(kmdat$stratum, levels=c("clinical-low","clinical-high"))

lr <- read_csv(file.path(D, "reclassification_within_stratum_logrank.csv"), show_col_types=FALSE)
lab <- function(s) { r <- lr[lr$stratum==gsub("-","_",s),]; sprintf("%s (log-rank p=%.3g)", s, r$logrank_p[1]) }
kmdat$facet <- factor(ifelse(kmdat$stratum=="clinical-low", lab("clinical-low"), lab("clinical-high")),
                      levels=c(lab("clinical-low"), lab("clinical-high")))

p_km <- ggplot(kmdat, aes(time, surv, colour=molecular)) +
  geom_step(linewidth=0.9) +
  facet_wrap(~facet) +
  scale_colour_manual(values=c("molecular-low"=col_low, "molecular-high"=col_high)) +
  coord_cartesian(ylim=c(0.55,1)) +
  labs(x="months", y="OS probability", colour=NULL,
       title="Molecular residual risk separates OS WITHIN clinical-risk strata",
       subtitle="Open-GDC OS, hypothesis-generating") +
  theme_bw(base_size=12) + theme(legend.position="top", strip.background=element_rect(fill="grey92"))
ggsave(file.path(outdir, "fig5_within_stratum_km.pdf"), p_km, width=9, height=4.2)
ggsave(file.path(outdir, "fig5_within_stratum_km.png"), p_km, width=9, height=4.2, dpi=200)

# ---- within-stratum forest plot ----
hr <- read_csv(file.path(D, "reclassification_within_stratum_hr.csv"), show_col_types=FALSE)
fh <- hr %>% filter(analysis=="within_stratum") %>%
  mutate(label = sprintf("%s: molecular-high vs low (n=%d, ev=%d)", stratum, n, events))
p_forest <- ggplot(fh, aes(x=HR, y=label)) +
  geom_vline(xintercept=1, linetype="dotted", colour="grey50") +
  geom_pointrange(aes(xmin=ci_low, xmax=ci_high), colour="#5a5a5a", linewidth=0.8, size=0.6) +
  geom_text(aes(label=sprintf("HR %.2f (%.2f-%.2f), p=%.3g", HR, ci_low, ci_high, p)),
            vjust=-1.1, size=3.2) +
  scale_x_log10() +
  labs(x="hazard ratio (log scale), molecular-high vs molecular-low", y=NULL,
       title="Within-stratum hazard ratios (OS)") +
  theme_bw(base_size=12)
ggsave(file.path(outdir, "fig5_within_stratum_forest.pdf"), p_forest, width=8, height=2.8)
ggsave(file.path(outdir, "fig5_within_stratum_forest.png"), p_forest, width=8, height=2.8, dpi=200)

cat("wrote fig5_within_stratum_km.{pdf,png} and fig5_within_stratum_forest.{pdf,png}\n")
