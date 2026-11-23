# P2 fact-share null (prereg/P2_prompt_vs_fact.md section 4). Called by p2_analysis.py on the primary set (correct
# cells), outcome D1. Parametric bootstrap from the primary model without (1|fact): see p2_null_fns.R.
# (Replaced the shuffled-fact null on 2026-11-23, human decision on stats-reviewer round 3, finding B1.)
# Usage: Rscript p2_null.R <long.csv> <out.json> y=D1 n_perm=1000 seed=20261121 cores=3 nc=3
#   n_perm is the number of simulated datasets (name kept for the caller's interface).
suppressPackageStartupMessages({library(lme4); library(jsonlite)})
source("analysis/p2/p2_model.R"); source("analysis/p2/p2_null_fns.R")
a <- commandArgs(trailingOnly = TRUE); csv <- a[1]; out <- a[2]
kv <- list(y = "D1", n_perm = "1000", seed = "20261121", cores = "3", nc = "3")
for (x in a[-(1:2)]) { p <- strsplit(x, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
d0 <- read.csv(csv, stringsAsFactors = FALSE); d0$y <- d0[[kv$y]]; d0 <- d0[!is.na(d0$y), ]
d0$fact <- d0$fact_id
COV <- c("n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior")
COV <- COV[sapply(COV, function(v) v %in% names(d0) && sd(d0[[v]]) > 0)]
subj <- length(unique(d0$subject)) < length(unique(d0$fact))
r <- p2_null_test(d0, as.integer(kv$nc), COV, subj, nsim = as.integer(kv$n_perm), seed = as.integer(kv$seed),
                  cores = as.integer(kv$cores))
res <- c(list(y = kv$y, n_rows = nrow(d0), n_facts = length(unique(d0$fact)), nc = as.integer(kv$nc)), r)
writeLines(toJSON(res, auto_unbox = TRUE, digits = NA, na = "null"), out)
