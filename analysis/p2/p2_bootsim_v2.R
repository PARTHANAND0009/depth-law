# P2 CI-method simulation v2 (analysis/p2/bootsim_v2_plan.md): parametric bootMer only, 120 sims per condition,
# 500 replicates; percentile intervals at nominal 95% and 97.5% from the same replicates. New seeds (base 20261122).
# Usage: Rscript p2_bootsim_v2.R <out.json> n_sim=120 n_boot=500 miss=0.5 cores=3 seed=20261122
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
source("analysis/p2/p2_model.R")
a <- commandArgs(trailingOnly = TRUE); out <- a[1]
kv <- list(n_sim = "120", n_boot = "500", miss = "0.5", cores = "3", seed = "20261122")
for (x in a[-1]) { p <- strsplit(x, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
nsim <- as.integer(kv$n_sim); nb <- as.integer(kv$n_boot); miss <- as.numeric(kv$miss); seed <- as.integer(kv$seed)
f <- stream_in(file("materials/facts_v1.jsonl"), verbose = FALSE)
design <- list(facts = data.frame(fact = f$fact_id, relation = f$relation, subject = f$subject, stringsAsFactors = FALSE))
CONDS <- list(  # identical to v1
  edepthvar_like = list(relation = 0.0017, frame = 0.0005, rt = 0.0025, fact = 0.0027, ft = 0.0012, fc = 0.0002, e = 0.0009),
  fact_dominant  = list(relation = 0.0017, frame = 0.0003, rt = 0.0010, fact = 0.0060, ft = 0.0008, fc = 0.0002, e = 0.0009))
Q <- c("icc1", "diff", "wording")
LEVELS <- list(n95 = c(0.025, 0.975), n975 = c(0.0125, 0.9875))
stat <- function(m) { v <- as.data.frame(VarCorr(m)); v <- setNames(v$vcov, v$grp); s <- p2_shares(v); c(icc1 = s$icc1, diff = s$diff, wording = s$wording) }
fitq <- function(d) lmer(p2_formula("y", subject = FALSE), data = d, REML = TRUE, control = lmerControl(calc.derivs = FALSE))
one <- function(job) {
  cname <- job$cond; i <- job$sim; comp <- CONDS[[cname]]
  d <- p2_simulate(design, comp, miss = miss, seed = seed + 1000 * i + nchar(cname))
  m <- fitq(d); pt <- stat(m); tr <- p2_truth(comp); truth <- c(icc1 = tr$icc1, diff = tr$diff, wording = tr$wording)
  set.seed(seed + 11 * i + nchar(cname))
  bt <- bootMer(m, stat, nsim = nb, type = "parametric", use.u = FALSE)$t
  res <- list(cond = cname, sim = i, point = as.list(pt), truth = as.list(truth), singular = isSingular(m),
              n_failed = sum(!is.finite(bt[, 1])))
  for (lv in names(LEVELS)) {
    ci <- apply(bt, 2, function(x) quantile(x, LEVELS[[lv]], na.rm = TRUE))
    res[[lv]] <- list(lo = as.list(ci[1, ]), hi = as.list(ci[2, ]),
                      covered = as.list(sapply(Q, function(q) ci[1, q] <= truth[q] && truth[q] <= ci[2, q])))
  }
  res
}
jobs <- unlist(lapply(names(CONDS), function(cn) lapply(seq_len(nsim), function(i) list(cond = cn, sim = i))), recursive = FALSE)
jdir <- paste0(out, ".jobs"); dir.create(jdir, showWarnings = FALSE, recursive = TRUE)
R <- mclapply(jobs, function(j) {
  f <- file.path(jdir, sprintf("%s_%03d.json", j$cond, j$sim))
  if (file.exists(f)) return(fromJSON(f, simplifyVector = FALSE))
  r <- tryCatch(one(j), error = function(e) list(cond = j$cond, sim = j$sim, error = conditionMessage(e)))
  writeLines(toJSON(r, auto_unbox = TRUE, digits = NA, na = "null"), paste0(f, ".tmp")); file.rename(paste0(f, ".tmp"), f)
  r
}, mc.cores = as.integer(kv$cores), mc.preschedule = FALSE)
writeLines(toJSON(list(settings = kv, conditions = CONDS, sims = R), auto_unbox = TRUE, digits = NA, na = "null"), out)
