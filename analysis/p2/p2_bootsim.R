# P2 A4: choose the CI method by simulation on the exact P2 design (materials/facts_v1.jsonl: 300 facts,
# 20 relations; 10 frames; 3 carriers). Methods:
#   twoway : resample facts within relation AND frames (10, with replacement), relabel duplicates, refit
#   param  : parametric bootstrap, lme4::bootMer(type = "parametric", use.u = FALSE), refit
# Requirement (human, A4): coverage >= 0.90 and |bias| <= 0.05 for the decision quantities (ICC1, diff).
# Usage: Rscript p2_bootsim.R <out.json> n_sim=60 n_boot=100 miss=0.5 cores=3 seed=20261121
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
source("analysis/p2/p2_model.R")
a <- commandArgs(trailingOnly = TRUE); out <- a[1]
kv <- list(n_sim = "60", n_boot = "100", miss = "0.5", cores = "3", seed = "20261121")
for (x in a[-1]) { p <- strsplit(x, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
nsim <- as.integer(kv$n_sim); nb <- as.integer(kv$n_boot); miss <- as.numeric(kv$miss); seed <- as.integer(kv$seed)
f <- stream_in(file("materials/facts_v1.jsonl"), verbose = FALSE)
design <- list(facts = data.frame(fact = f$fact_id, relation = f$relation, subject = f$subject, stringsAsFactors = FALSE))
CONDS <- list(
  edepthvar_like = list(relation = 0.0017, frame = 0.0005, rt = 0.0025, fact = 0.0027, ft = 0.0012, fc = 0.0002, e = 0.0009),
  fact_dominant  = list(relation = 0.0017, frame = 0.0003, rt = 0.0010, fact = 0.0060, ft = 0.0008, fc = 0.0002, e = 0.0009))
Q <- c("icc1", "diff", "wording")
stat <- function(m) { v <- as.data.frame(VarCorr(m)); v <- setNames(v$vcov, v$grp); s <- p2_shares(v); c(icc1 = s$icc1, diff = s$diff, wording = s$wording) }
fitq <- function(d) lmer(p2_formula("y", subject = FALSE), data = d, REML = TRUE, control = lmerControl(calc.derivs = FALSE))

twoway <- function(d, nb, s0) {
  rels <- split(unique(d[, c("fact", "relation")])$fact, unique(d[, c("fact", "relation")])$relation)
  byf <- split(seq_len(nrow(d)), as.character(d$fact))
  t(sapply(seq_len(nb), function(b) {
    set.seed(s0 + b)
    frs <- sample(0:9, 10, replace = TRUE)
    parts <- list(); j <- 0
    for (r in names(rels)) {
      ff <- as.character(rels[[r]]); pick <- ff[sample.int(length(ff), length(ff), replace = TRUE)]
      for (i in seq_along(pick)) { j <- j + 1; g <- d[byf[[pick[i]]], c("relation", "template_id", "carrier", "y", "fact")]
        g$fact <- paste0(g$fact, "#", j); parts[[j]] <- g }
    }
    db <- do.call(rbind, parts)
    # frames: each drawn frame k contributes its rows, relabelled as a new frame level k
    db <- do.call(rbind, lapply(seq_along(frs), function(k) { g <- db[db$template_id == frs[k], ]; g$template_id <- k - 1; g$frame <- k - 1; g }))
    if (!nrow(db)) return(rep(NA, 3))
    tryCatch(stat(fitq(p2_prep(db))), error = function(e) rep(NA, 3))
  }))
}
param <- function(m, nb, s0) {
  set.seed(s0)
  bm <- bootMer(m, stat, nsim = nb, type = "parametric", use.u = FALSE)
  bm$t
}
one <- function(job) {
  cname <- job$cond; i <- job$sim; comp <- CONDS[[cname]]
  d <- p2_simulate(design, comp, miss = miss, seed = seed + 1000 * i + nchar(cname))
  m <- fitq(d); pt <- stat(m); tr <- p2_truth(comp); truth <- c(icc1 = tr$icc1, diff = tr$diff, wording = tr$wording)
  res <- list(cond = cname, sim = i, point = as.list(pt), truth = as.list(truth), singular = isSingular(m))
  for (meth in c("twoway", "param")) {
    bt <- if (meth == "twoway") twoway(d, nb, seed + 7 * i) else param(m, nb, seed + 11 * i)
    ci <- apply(bt, 2, function(x) quantile(x, c(0.025, 0.975), na.rm = TRUE))
    res[[meth]] <- list(lo = as.list(ci[1, ]), hi = as.list(ci[2, ]), n_failed = sum(is.na(bt[, 1])),
                        covered = as.list(sapply(Q, function(q) ci[1, q] <= truth[q] && truth[q] <= ci[2, q])))
  }
  res
}
jobs <- unlist(lapply(names(CONDS), function(cn) lapply(seq_len(nsim), function(i) list(cond = cn, sim = i))), recursive = FALSE)
# Each job is checkpointed to <out>.jobs/<cond>_<sim>.json; a restart skips finished jobs.
jdir <- paste0(out, ".jobs"); dir.create(jdir, showWarnings = FALSE)
R <- mclapply(jobs, function(j) {
  f <- file.path(jdir, sprintf("%s_%03d.json", j$cond, j$sim))
  if (file.exists(f)) return(fromJSON(f, simplifyVector = FALSE))
  r <- tryCatch(one(j), error = function(e) list(cond = j$cond, sim = j$sim, error = conditionMessage(e)))
  writeLines(toJSON(r, auto_unbox = TRUE, digits = NA, na = "null"), paste0(f, ".tmp")); file.rename(paste0(f, ".tmp"), f)
  r
}, mc.cores = as.integer(kv$cores))
summ <- list()
for (cn in names(CONDS)) {
  rr <- Filter(function(r) r$cond == cn && is.null(r$error), R)
  s <- list(n_ok = length(rr), n_error = sum(sapply(R, function(r) r$cond == cn && !is.null(r$error))))
  for (q in Q) {
    pts <- sapply(rr, function(r) r$point[[q]]); tru <- rr[[1]]$truth[[q]]
    s[[q]] <- list(truth = tru, mean_point = mean(pts), bias = mean(pts) - tru,
                   coverage_twoway = mean(sapply(rr, function(r) r$twoway$covered[[q]])),
                   coverage_param = mean(sapply(rr, function(r) r$param$covered[[q]])),
                   mean_width_twoway = mean(sapply(rr, function(r) r$twoway$hi[[q]] - r$twoway$lo[[q]])),
                   mean_width_param = mean(sapply(rr, function(r) r$param$hi[[q]] - r$param$lo[[q]])))
  }
  s$singular_rate <- mean(sapply(rr, function(r) r$singular))
  summ[[cn]] <- s
}
writeLines(toJSON(list(settings = kv, conditions = CONDS, summary = summ, sims = R), auto_unbox = TRUE, digits = NA, na = "null"), out)
