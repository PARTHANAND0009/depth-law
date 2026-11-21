# P2 confirmatory fits for one model x outcome (prereg/P2_prompt_vs_fact.md). Called by p2_analysis.py.
# Usage: Rscript p2_analysis.R <long.csv> <out.json> y=D1 boot=param|twoway n_boot=1000 seed=20261121 cores=3 cov=1
#   long.csv: one row per (fact, template_id, carrier) with columns relation, frame, fact, subject, y columns
#   and fact-level covariates n_answer_tokens, n_subject_tokens, log_cooc_proxy, answer_prior (z-scored upstream).
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
source("analysis/p2/p2_model.R")
a <- commandArgs(trailingOnly = TRUE); csv <- a[1]; out <- a[2]
kv <- list(y = "D1", boot = "param", n_boot = "1000", seed = "20261121", cores = "3", cov = "1", nc = "3")
for (x in a[-(1:2)]) { p <- strsplit(x, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
d <- read.csv(csv, stringsAsFactors = FALSE); d$y <- d[[kv$y]]; d <- d[!is.na(d$y), ]
d$fact <- d$fact_id; d <- p2_prep(d); nc <- as.integer(kv$nc)
COV <- if (kv$cov == "1") c("n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior") else character(0)
COV <- COV[sapply(COV, function(v) v %in% names(d) && sd(d[[v]]) > 0)]
subj <- length(unique(d$subject)) < length(unique(d$fact))  # subject term only if subjects recur
r <- p2_fit(d, "y", COV, subject = subj)
s <- p2_shares(r$vc, nc)
stat <- function(m) { v <- as.data.frame(VarCorr(m)); v <- setNames(v$vcov, v$grp); q <- p2_shares(v, nc)
  c(icc1 = q$icc1, diff = q$diff, wording = q$wording, tf_minus_resid = q$template_plus_frame_minus_residual,
    nprime_G = ifelse(is.na(q$nprime_G), 31, q$nprime_G)) }
nb <- as.integer(kv$n_boot); seed <- as.integer(kv$seed)
if (kv$boot == "param") {
  set.seed(seed)
  bt <- bootMer(r$model, stat, nsim = nb, type = "parametric", use.u = FALSE,
                parallel = "multicore", ncpus = as.integer(kv$cores))$t
} else {
  source("analysis/p2/p2_bootsim_fns.R")
  bt <- twoway_boot(d, nb, seed, COV, subj, stat, as.integer(kv$cores))
}
ci <- apply(bt, 2, function(x) as.numeric(quantile(x, c(0.025, 0.975), na.rm = TRUE)))
res <- list(y = kv$y, n_rows = nrow(d), n_facts = length(unique(d$fact)), n_relations = length(unique(d$relation)),
            covariates = COV, subject_term = subj, vc = as.list(r$vc), singular = r$singular, warnings = r$warnings,
            point = list(icc1 = s$icc1, diff = s$diff, wording = s$wording, tf_minus_resid = s$template_plus_frame_minus_residual,
                         nprime_G = s$nprime_G, nprime_Phi = s$nprime_Phi, G_k = s$G_k, Phi_k = s$Phi_k, share_total = s$share_total),
            boot = list(method = kv$boot, n_boot = nb, n_failed = sum(is.na(bt[, 1])),
                        ci = setNames(lapply(seq_len(ncol(ci)), function(j) ci[, j]), colnames(bt))))
writeLines(toJSON(res, auto_unbox = TRUE, digits = NA, na = "null"), out)
