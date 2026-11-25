# P2 robustness simulation (prereg/P2_prompt_vs_fact.md section 4, "Robustness simulation"; plan:
# analysis/p2/robustsim_plan.md, committed before this runs). NON-SELECTING: it is reported next to the results and
# cannot change the CI method or any decision.
# Parametric bootMer 95% percentile coverage of ICC(1), diff and wording, fitting the FROZEN formula (four covariates
# + carrier fixed effect; p2_formula(cov = COV, carrier = TRUE, subject = FALSE)), on data with:
#   - D1 discretised to ceiling(y* L)/L = (l* + 1)/L, L in {24, 36};
#   - missingness tied to correctness: a (fact, template) cell is missing with probability plogis(a + b z), z the
#     standardised latent cell depth (later depth -> more likely missing), dropped across all carriers;
#   - nc in {2, 3} with a carrier shift (fixed carrier offsets);
#   - true values near the boundaries: ICC(1) 0.4-0.5 and diff = 0 (truth A, truth B).
# Truth = latent-scale shares from p2_truth(comp, nc) (before discretisation).
# Usage: Rscript p2_robustsim.R <out.json> n_sim=100 n_boot=500 cores=4 seed=20261125
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
source("analysis/p2/p2_model.R")
a <- commandArgs(trailingOnly = TRUE); out <- a[1]
kv <- list(n_sim = "100", n_boot = "500", cores = "4", seed = "20261125", conds = "all")
for (x in a[-1]) { p <- strsplit(x, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
nsim <- as.integer(kv$n_sim); nb <- as.integer(kv$n_boot); seed <- as.integer(kv$seed)
f <- stream_in(file("materials/facts_v1.jsonl"), verbose = FALSE)
facts <- data.frame(fact = f$fact_id, relation = f$relation, stringsAsFactors = FALSE)
COV <- c("n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior")
BETA <- c(n_answer_tokens = 0.009, n_subject_tokens = -0.005, log_cooc_proxy = -0.007, answer_prior = -0.015)
SHIFT <- c(0, 0.005, -0.006)          # carrier offsets (order of the real carrier fixed effects)
MISS <- list(a = 0.38, b = 1.0)       # target marginal missingness about 0.58 (real: 1 - 1221/3000, 1 - 1355/3000)
TRUTHS <- list(  # latent variances; f = rt + frame + ft, so diff = 0 exactly
  A = list(relation = 0.0004, frame = 0.0002, rt = 0.0005, fact = 0.0014, ft = 0.0007, fc = 0.0001, e = 0.0003),
  B = list(relation = 0.0004, frame = 0.0002, rt = 0.0004, fact = 0.0012, ft = 0.0006, fc = 0.0003, e = 0.0015))
CONDS <- list()
for (tn in names(TRUTHS)) for (L in c(24, 36)) for (nc in c(3, 2))
  CONDS[[sprintf("%s_L%d_nc%d", tn, L, nc)]] <- list(truth = tn, L = L, nc = nc)
if (kv$conds != "all") CONDS <- CONDS[strsplit(kv$conds, ",")[[1]]]

simulate_one <- function(cd, s) {
  set.seed(s); comp <- TRUTHS[[cd$truth]]; nc <- cd$nc; L <- cd$L
  re <- function(n, v) rnorm(n, 0, sqrt(v))
  rels <- unique(facts$relation); nf <- nrow(facts)
  a_rel <- setNames(re(length(rels), comp$relation), rels); a_fr <- re(10, comp$frame)
  a_rt <- matrix(re(length(rels) * 10, comp$rt), length(rels), 10, dimnames = list(rels, NULL))
  X <- matrix(rnorm(nf * 4), nf, 4, dimnames = list(NULL, COV)); a_f <- re(nf, comp$fact)
  cells <- expand.grid(i = seq_len(nf), template_id = 0:9)
  ri <- facts$relation[cells$i]
  m_ft <- 0.55 + a_rel[ri] + a_fr[cells$template_id + 1] + a_rt[cbind(match(ri, rels), cells$template_id + 1)] + a_f[cells$i] +
    re(nrow(cells), comp$ft) + as.vector(X[cells$i, ] %*% BETA)
  z <- (m_ft - mean(m_ft)) / sd(m_ft)
  keep <- runif(nrow(cells)) >= plogis(MISS$a + MISS$b * z)
  cells <- cells[keep, ]; m_ft <- m_ft[keep]
  a_fc <- matrix(re(nf * nc, comp$fc), nf, nc)
  d <- do.call(rbind, lapply(seq_len(nc), function(c) {
    ys <- m_ft + SHIFT[c] + a_fc[cbind(cells$i, c)] + re(nrow(cells), comp$e)
    data.frame(i = cells$i, template_id = cells$template_id, carrier = c - 1, ystar = ys)
  }))
  d$y <- pmin(pmax(ceiling(d$ystar * L), 1), L) / L      # D1 = (l* + 1) / L, l* in 0..L-1
  d$fact <- facts$fact[d$i]; d$relation <- facts$relation[d$i]; d$frame <- d$template_id
  for (v in COV) { x <- X[d$i, v]; d[[v]] <- (x - mean(x)) / sd(x) }  # z-scored over carrier-level rows, as upstream
  d$i <- NULL
  list(d = p2_prep(d), miss = 1 - mean(keep))
}

one <- function(job) {
  cd <- CONDS[[job$cond]]; i <- job$sim; nc <- cd$nc
  s <- seed + 1000 * i + which(names(CONDS) == job$cond)
  sm <- simulate_one(cd, s); d <- sm$d
  stat <- function(m) { v <- as.data.frame(VarCorr(m)); v <- setNames(v$vcov, v$grp); q <- p2_shares(v, nc)
    c(icc1 = q$icc1, diff = q$diff, wording = q$wording) }
  m <- lmer(p2_formula("y", COV, subject = FALSE, carrier = TRUE), data = d, REML = TRUE,
            control = lmerControl(calc.derivs = FALSE))
  pt <- stat(m); tr <- p2_truth(TRUTHS[[cd$truth]], nc)
  truth <- c(icc1 = tr$icc1, diff = tr$diff, wording = tr$wording)
  set.seed(s + 7)
  bt <- bootMer(m, stat, nsim = nb, type = "parametric", use.u = FALSE)$t
  ci <- apply(bt, 2, function(x) quantile(x, c(0.025, 0.975), na.rm = TRUE))
  list(cond = job$cond, sim = i, seed = s, n_rows = nrow(d), n_facts = length(unique(d$fact)), miss = sm$miss,
       point = as.list(pt), truth = as.list(truth), singular = isSingular(m), n_failed = sum(!is.finite(bt[, 1])),
       lo = as.list(ci[1, ]), hi = as.list(ci[2, ]),
       covered = as.list(sapply(names(truth), function(q) ci[1, q] <= truth[q] && truth[q] <= ci[2, q])))
}

jobs <- unlist(lapply(names(CONDS), function(cn) lapply(seq_len(nsim), function(i) list(cond = cn, sim = i))),
               recursive = FALSE)
jdir <- paste0(out, ".jobs"); dir.create(jdir, showWarnings = FALSE, recursive = TRUE)
R <- mclapply(jobs, function(j) {
  fj <- file.path(jdir, sprintf("%s_%03d.json", j$cond, j$sim))
  if (file.exists(fj)) return(fromJSON(fj, simplifyVector = FALSE))
  r <- tryCatch(one(j), error = function(e) list(cond = j$cond, sim = j$sim, error = conditionMessage(e)))
  writeLines(toJSON(r, auto_unbox = TRUE, digits = NA, na = "null"), paste0(fj, ".tmp")); file.rename(paste0(fj, ".tmp"), fj)
  r
}, mc.cores = as.integer(kv$cores), mc.preschedule = FALSE)
writeLines(toJSON(list(settings = kv, truths = TRUTHS, conditions = CONDS, beta = as.list(BETA), shift = SHIFT,
                       miss_model = MISS, sims = R), auto_unbox = TRUE, digits = NA, na = "null"), out)
