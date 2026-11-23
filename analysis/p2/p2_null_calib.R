# Calibration and power of the P2 parametric fact-share null (p2_null_fns.R). Test only; not a result.
# Design: the P2 layout (20 relations x 15 facts = 300 facts, 10 frames shared by all relations), 5 of the 10
# paraphrases present per fact (as in the round-3 reviewer's illustration, results/P2review_round3_scripts/remlnull.R),
# nc carriers. Components as in that illustration: ft = 1, e = 1, fact:carrier = fc; relation, frame, relation:frame = 0.
# The null procedure is the frozen one (primary formula with the carrier fixed effect; null model without (1|fact)).
# Each replicate: a new dataset (seed base + i), then p2_null_test with nsim simulated datasets (seed base + i).
# With nsim = B, "p < 0.01" is "(1 + k)/(1 + B) < 0.01"; for B = 200 this is k <= 1, whose probability under a valid
# null is 2/201 = 0.00995, so the nominal level is unchanged; the analysis itself uses B = 1000.
# Usage: Rscript p2_null_calib.R <out.json> cond=fc1_nc3 fact=0 fc=1 nc=3 nrep=200 nsim=200 cores=3 seed=7000000
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
source("analysis/p2/p2_model.R"); source("analysis/p2/p2_null_fns.R")
a <- commandArgs(trailingOnly = TRUE); out <- a[1]
kv <- list(cond = "fc1_nc3", fact = "0", fc = "1", nc = "3", nrep = "200", nsim = "200", cores = "3", seed = "7000000")
for (x in a[-1]) { p <- strsplit(x, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
FACT <- as.numeric(kv$fact); FC <- as.numeric(kv$fc); nc <- as.integer(kv$nc); base <- as.integer(kv$seed)
sim <- function(seed) {
  set.seed(seed); F <- 300; rel <- rep(1:20, each = 15)
  d <- do.call(rbind, lapply(1:F, function(f) { t <- sort(sample(0:9, 5)); expand.grid(fact = f, template_id = t, carrier = 0:(nc - 1)) }))
  d$relation <- rel[d$fact]; d$frame <- d$template_id; d$subject <- d$fact; d$fact_id <- d$fact
  fa <- rnorm(F, 0, sqrt(FACT)); fc <- matrix(rnorm(F * nc, 0, sqrt(FC)), F); ft <- matrix(rnorm(F * 10), F)
  d$y <- fa[d$fact] + fc[cbind(d$fact, d$carrier + 1)] + ft[cbind(d$fact, d$template_id + 1)] + rnorm(nrow(d))
  d
}
jobs <- file.path(paste0(out, ".jobs")); dir.create(jobs, showWarnings = FALSE)
one <- function(i) {
  f <- file.path(jobs, sprintf("%s_%04d.json", kv$cond, i))
  if (file.exists(f)) return(fromJSON(f))
  r <- tryCatch(p2_null_test(sim(base + i), nc, character(0), FALSE, nsim = as.integer(kv$nsim), seed = base + i, cores = 1),
                error = function(e) list(status = paste("error:", conditionMessage(e)), p = NA, observed = NA, n_failed = NA))
  r <- list(i = i, status = r$status, p = r$p, observed = r$observed, n_failed = r$n_failed)
  writeLines(toJSON(r, auto_unbox = TRUE, digits = NA, na = "null"), paste0(f, ".tmp")); file.rename(paste0(f, ".tmp"), f)
  r
}
t0 <- Sys.time()
rs <- mclapply(seq_len(as.integer(kv$nrep)), one, mc.cores = as.integer(kv$cores), mc.preschedule = FALSE)
p <- vapply(rs, function(r) if (is.list(r) && is.numeric(r$p)) as.numeric(r$p) else NA_real_, numeric(1))
ok <- p[!is.na(p)]; n <- length(ok); rej <- mean(ok < 0.01); rej05 <- mean(ok < 0.05)
share <- FACT / (FACT + 1 + FC / nc + 1 / nc)
res <- list(settings = kv, true_fact_share_icc1 = share, n_ok = n, n_error = sum(is.na(p)),
            reject_p_lt_0.01 = rej, mcse_0.01 = sqrt(rej * (1 - rej) / n), reject_p_lt_0.05 = rej05, mcse_0.05 = sqrt(rej05 * (1 - rej05) / n),
            mean_failed_refits = mean(vapply(rs, function(r) if (is.list(r) && is.numeric(r$n_failed)) as.numeric(r$n_failed) else NA_real_, numeric(1)), na.rm = TRUE),
            minutes = as.numeric(difftime(Sys.time(), t0, units = "mins")))
writeLines(toJSON(res, auto_unbox = TRUE, digits = NA, na = "null", pretty = TRUE), out)
cat(toJSON(res[c("true_fact_share_icc1", "n_ok", "n_error", "reject_p_lt_0.01", "mcse_0.01", "reject_p_lt_0.05", "minutes")], auto_unbox = TRUE), "\n")
