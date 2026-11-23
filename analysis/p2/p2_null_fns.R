# P2 fact-share null: parametric bootstrap (prereg/P2_prompt_vs_fact.md section 4; human decision 2026-11-23 on
# stats-reviewer round 3, finding B1). Replaces the shuffled-fact null, whose permutations also removed fact:carrier.
# H0: fact variance = 0, with every other component as estimated.
#   1. Fit the null model: the primary model (same covariates, carrier fixed effect, (1|relation), (1|frame),
#      (1|relation:template), (1|fact:template), (1|fact:carrier)) WITHOUT (1|fact), by REML.
#   2. Simulate nsim datasets from that fit (lme4 simulate, new random effects and residuals; seed).
#   3. Refit the full primary model on each (lme4 refit) and compute ICC(1) = fact / den (p2_shares).
#   4. p = (1 + #{null ICC(1) >= observed ICC(1)}) / (1 + number of successful refits).
# Fits use calc.derivs = FALSE (speed); this changes only convergence warnings, not estimates.
suppressPackageStartupMessages({library(lme4); library(parallel)})

p2_null_test <- function(d, nc, cov = character(0), subject = FALSE, nsim = 1000, seed = 20261121, cores = 1) {
  d <- p2_prep(d)
  carrier <- nlevels(d$carrier_f) > 1
  ctl <- lmerControl(calc.derivs = FALSE)
  m1 <- lmer(p2_formula("y", cov, subject, carrier = carrier), data = d, REML = TRUE, control = ctl)
  m0 <- lmer(p2_formula("y", cov, subject, carrier = carrier, fact = FALSE), data = d, REML = TRUE, control = ctl)
  icc <- function(m) { v <- as.data.frame(VarCorr(m)); p2_shares(setNames(v$vcov, v$grp), nc)$icc1 }
  obs <- icc(m1)
  ys <- simulate(m0, nsim = nsim, seed = seed)
  one <- function(i) tryCatch(icc(refit(m1, newresp = ys[[i]])), error = function(e) NA_real_)
  null <- mclapply(seq_len(nsim), one, mc.cores = cores, mc.preschedule = TRUE)
  # a worker that dies returns an error object, not a number: coerce every element, so such entries become NA (failed)
  null <- vapply(null, function(x) if (is.numeric(x) && length(x) == 1) as.numeric(x) else NA_real_, numeric(1))
  ok <- null[!is.na(null)]
  v0 <- as.data.frame(VarCorr(m0))
  list(status = "ok", statistic = "REML ICC(1)", method = "parametric bootstrap from the fit without (1|fact)",
       observed = obs, n_sim = nsim, n_failed = sum(is.na(null)),
       p = (1 + sum(ok >= obs)) / (1 + length(ok)),
       null_quantiles = as.list(quantile(ok, c(0.5, 0.95, 0.99, 1))),
       null_model_vc = as.list(setNames(v0$vcov, v0$grp)), null_model_singular = isSingular(m0))
}
