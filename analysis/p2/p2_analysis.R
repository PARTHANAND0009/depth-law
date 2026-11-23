# P2 confirmatory fits for one model x outcome (prereg/P2_prompt_vs_fact.md). Called by p2_analysis.py.
# Usage: Rscript p2_analysis.R <long.csv> <out.json> y=D1 boot=param|twoway n_boot=1000 seed=20261121 cores=3 cov=1
#        nc=3 carrier=1 tcov=0 h4=0
#   long.csv: one row per (fact, template_id, carrier) with columns relation, frame, fact, subject, y columns
#   and fact-level covariates n_answer_tokens, n_subject_tokens, log_cooc_proxy, answer_prior (z-scored upstream);
#   with tcov=1 also template-level covariates tcov_len, tcov_dist (sensitivity model, prereg section 4).
#   carrier=1: carrier fixed effect (prereg; stats-reviewer round 1 item 2). h4=1: frame fixed effects (H4,
#   EXPLORATORY; point estimates only). n_boot=0: point estimates only (leave-one-frame-out, H4).
# Failed refits (prereg section 4, item 10): counted per statistic; a fit whose icc1 or diff column has > 5% failed
# refits is status MISSING. Boundary (zero) variance estimates are accepted; singular fits and warnings are reported.
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
source("analysis/p2/p2_model.R")
a <- commandArgs(trailingOnly = TRUE); csv <- a[1]; out <- a[2]
kv <- list(y = "D1", boot = "param", n_boot = "1000", seed = "20261121", cores = "3", cov = "1", nc = "3",
           carrier = "1", tcov = "0", h4 = "0")
for (x in a[-(1:2)]) { p <- strsplit(x, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
d <- read.csv(csv, stringsAsFactors = FALSE); d$y <- d[[kv$y]]; d <- d[!is.na(d$y), ]
d$fact <- d$fact_id; d <- p2_prep(d); nc <- as.integer(kv$nc)
COV <- if (kv$cov == "1") c("n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior") else character(0)
if (kv$tcov == "1") COV <- c(COV, "tcov_len", "tcov_dist")
COV <- COV[sapply(COV, function(v) v %in% names(d) && sd(d[[v]]) > 0)]
subj <- length(unique(d$subject)) < length(unique(d$fact))  # subject term only if subjects recur
use_carrier <- kv$carrier == "1"; h4 <- kv$h4 == "1"
if (kv$boot != "param") stop("only boot=param is preregistered (the two-way path has no carrier fixed effect)")
r <- p2_fit(d, "y", COV, subject = subj, carrier = use_carrier, fixed_frame = h4)
s <- p2_shares(r$vc, nc)
stat <- function(m) { v <- as.data.frame(VarCorr(m)); v <- setNames(v$vcov, v$grp); q <- p2_shares(v, nc)
  c(icc1 = q$icc1, diff = q$diff, wording = q$wording, tf_minus_resid = q$template_plus_frame_minus_residual,
    nprime_G = ifelse(is.na(q$nprime_G), 31, q$nprime_G)) }
nb <- as.integer(kv$n_boot); seed <- as.integer(kv$seed)
boot <- list(method = kv$boot, n_boot = nb)
status <- "ok"
if (nb > 0) {
  if (kv$boot == "param") {
    set.seed(seed)
    bt <- bootMer(r$model, stat, nsim = nb, type = "parametric", use.u = FALSE,
                  parallel = "multicore", ncpus = as.integer(kv$cores))$t
  } else {
    source("analysis/p2/p2_bootsim_fns.R")
    bt <- twoway_boot(d, nb, seed, COV, subj, stat, as.integer(kv$cores))
  }
  ci <- apply(bt, 2, function(x) as.numeric(quantile(x, c(0.025, 0.975), na.rm = TRUE)))
  nfail <- colSums(is.na(bt)); ffrac <- nfail / nrow(bt)
  if (any(ffrac[c("icc1", "diff")] > 0.05)) status <- "MISSING: > 5% failed bootstrap refits in icc1 or diff"
  boot$n_failed <- as.list(nfail); boot$failed_frac <- as.list(ffrac)
  boot$ci <- setNames(lapply(seq_len(ncol(ci)), function(j) ci[, j]), colnames(bt))
}
fixef_out <- as.list(lme4::fixef(r$model))
res <- list(y = kv$y, status = status, n_rows = nrow(d), n_facts = length(unique(d$fact)), n_relations = length(unique(d$relation)),
            covariates = COV, subject_term = subj, carrier_fixed = use_carrier && nlevels(d$carrier_f) > 1, h4 = h4, nc = nc,
            vc = as.list(r$vc), fixef = fixef_out, singular = r$singular, warnings = r$warnings,
            point = list(icc1 = s$icc1, diff = s$diff, wording = s$wording, tf_minus_resid = s$template_plus_frame_minus_residual,
                         nprime_G = s$nprime_G, nprime_Phi = s$nprime_Phi, G_k = s$G_k, Phi_k = s$Phi_k, share_total = s$share_total),
            boot = boot)
writeLines(toJSON(res, auto_unbox = TRUE, digits = NA, na = "null"), out)
