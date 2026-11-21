# EXPLORATORY (post hoc, not preregistered) — Part 0a: leave-one-relation-out jackknife of the B3 model.
# For each model x outcome (D1, D4), set (i) correct cells: refit depth ~ 1 + (1|relation) + (1|relation:template)
# + (1|subject) + (1|fact) by REML on all relations and with each relation dropped in turn; report the difference
# (template-main + residual) - (fact+subject) (shares of total incl. relation), ICC(1) = fs/(fs+rt+e), the
# within-relation fact share, and singular flags. Convergence checks are ON here (default lmerControl).
# Usage: Rscript <this> <tables_dir> <out.json>
suppressPackageStartupMessages({library(lme4); library(jsonlite)})
a <- commandArgs(trailingOnly = TRUE); tdir <- a[1]; out <- a[2]
P <- "EXPLORATORY_post-hoc_not-preregistered__"
MODELS <- c("pythia-1.4b", "pythia-2.8b", "OLMo-2-1124-7B")
one <- function(d, y) {
  d$rt <- factor(paste(d$relation, d$template_id, sep = ":"))
  for (v in c("relation", "subject", "fact_id")) d[[v]] <- factor(d[[v]])
  w <- character(0)
  m <- withCallingHandlers(
    lmer(as.formula(paste(y, "~ 1 + (1|relation) + (1|rt) + (1|subject) + (1|fact_id)")), data = d, REML = TRUE),
    warning = function(x) { w <<- c(w, conditionMessage(x)); invokeRestart("muffleWarning") })
  v <- as.data.frame(VarCorr(m)); v <- setNames(v$vcov, v$grp); tot <- sum(v)
  fs <- unname(v["fact_id"] + v["subject"]); rt <- unname(v["rt"]); e <- unname(v["Residual"])
  list(diff = (rt + e - fs) / tot, share_fact_subject = fs / tot, share_template_main = rt / tot, share_residual = e / tot,
       share_relation = unname(v["relation"]) / tot, icc1 = fs / (fs + rt + e),
       n_cells = nrow(d), singular = isSingular(m), warnings = w)
}
res <- list()
for (mn in MODELS) {
  d0 <- read.csv(file.path(tdir, paste0(P, "cells_", mn, ".csv")), stringsAsFactors = FALSE)
  d0 <- d0[d0$correct == 1, ]
  for (y in c("D1", "D4")) {
    full <- one(d0, y)
    loo <- lapply(sort(unique(d0$relation)), function(r) c(list(dropped = r), one(d0[d0$relation != r, ], y)))
    res[[paste(mn, y, sep = "|")]] <- list(full = full, loo = loo)
  }
}
writeLines(toJSON(res, auto_unbox = TRUE, digits = NA, na = "null"), out)
