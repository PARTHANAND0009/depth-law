# P2 shuffled-fact null (prereg/P2_prompt_vs_fact.md section 4). Called by p2_analysis.py on the primary set (correct
# cells), outcome D1.
# Usage: Rscript p2_null.R <long.csv> <out.json> y=D1 n_perm=1000 seed=20261121 cores=3 nc=3
# Statistic: REML ICC(1) = fact / den (p2_shares), same model as the primary fit (covariates, carrier fixed effect).
# Permutation: within each relation x paraphrase (template_id) cell, the fact labels of the cell's facts are permuted;
# all carrier rows of one (fact, paraphrase) move together, so fact:template and fact:carrier groupings follow the new
# label. Fact-level covariates stay with their rows (the y side). This keeps relation, frame and relation:frame
# structure and destroys only the consistency of a fact's depth across paraphrases.
# p = (1 + #{permuted ICC(1) >= observed}) / (1 + successful permutations). Failed refits are dropped and counted.
# Fits use calc.derivs = FALSE (speed); this changes only convergence warnings, not the estimates.
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
source("analysis/p2/p2_model.R")
a <- commandArgs(trailingOnly = TRUE); csv <- a[1]; out <- a[2]
kv <- list(y = "D1", n_perm = "1000", seed = "20261121", cores = "3", nc = "3")
for (x in a[-(1:2)]) { p <- strsplit(x, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
d0 <- read.csv(csv, stringsAsFactors = FALSE); d0$y <- d0[[kv$y]]; d0 <- d0[!is.na(d0$y), ]
d0$fact <- d0$fact_id; nc <- as.integer(kv$nc)
COV <- c("n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior")
COV <- COV[sapply(COV, function(v) v %in% names(d0) && sd(d0[[v]]) > 0)]
subj <- length(unique(d0$subject)) < length(unique(d0$fact))
icc <- function(d) {
  m <- lmer(p2_formula("y", COV, subj, carrier = nlevels(factor(d$carrier)) > 1), data = p2_prep(d), REML = TRUE,
            control = lmerControl(calc.derivs = FALSE))
  v <- as.data.frame(VarCorr(m)); p2_shares(setNames(v$vcov, v$grp), nc)$icc1
}
obs <- icc(d0)
cell <- paste(d0$relation, d0$template_id, sep = "|")
shuffle <- function(i) {
  set.seed(as.integer(kv$seed) + i)
  d <- d0
  for (cl in unique(cell)) {
    idx <- which(cell == cl); f <- unique(d0$fact[idx])
    if (length(f) < 2) next
    map <- setNames(sample(f), f)
    d$fact[idx] <- map[d0$fact[idx]]
  }
  d$subject <- d$fact  # subjects are fact-specific; keep them aligned with the permuted label
  tryCatch(icc(d), error = function(e) NA_real_)
}
np <- as.integer(kv$n_perm)
perm <- mclapply(seq_len(np), shuffle, mc.cores = as.integer(kv$cores), mc.preschedule = TRUE)
# a worker that dies returns an error object, not a number: coerce every element, so such entries become NA (failed)
perm <- vapply(perm, function(x) if (is.numeric(x) && length(x) == 1) as.numeric(x) else NA_real_, numeric(1))
ok <- perm[!is.na(perm)]
res <- list(y = kv$y, status = "ok", statistic = "REML ICC(1)", n_rows = nrow(d0), n_facts = length(unique(d0$fact)), nc = nc,
            observed = obs, n_perm = np, n_failed = sum(is.na(perm)),
            p = (1 + sum(ok >= obs)) / (1 + length(ok)), perm_quantiles = as.list(quantile(ok, c(0.5, 0.95, 0.99, 1))))
writeLines(toJSON(res, auto_unbox = TRUE, digits = NA, na = "null"), out)
