# Illustration only, frozen model functions: REML ICC(1) under fact = 0 with fact:carrier > 0.
# SD of ICC(1) across independent H0 datasets vs SD across within (relation x paraphrase) permutations of one dataset.
suppressPackageStartupMessages(library(lme4)); source("analysis/p2/p2_model.R")
args <- as.numeric(commandArgs(TRUE)); A <- args[1]; nrep <- args[2]; nc <- 3
sim <- function(seed) {
  set.seed(seed); F <- 300; rel <- rep(1:20, each = 15)
  d <- do.call(rbind, lapply(1:F, function(f) { t <- sort(sample(0:9, 5)); expand.grid(fact = f, template_id = t, carrier = 0:(nc - 1)) }))
  d$relation <- rel[d$fact]; d$frame <- d$template_id; d$subject <- d$fact
  fc <- matrix(rnorm(F * nc, 0, sqrt(A)), F); ft <- matrix(rnorm(F * 10), F)
  d$y <- fc[cbind(d$fact, d$carrier + 1)] + ft[cbind(d$fact, d$template_id + 1)] + rnorm(nrow(d)); d }
icc <- function(d) { m <- lmer(p2_formula("y", character(0), FALSE, carrier = TRUE), data = p2_prep(d), REML = TRUE,
  control = lmerControl(calc.derivs = FALSE)); v <- as.data.frame(VarCorr(m)); p2_shares(setNames(v$vcov, v$grp), nc)$icc1 }
obs <- sapply(1:nrep, function(i) icc(sim(100 + i)))
d0 <- sim(1); cell <- paste(d0$relation, d0$template_id)
perm <- sapply(1:nrep, function(i) { set.seed(5000 + i); d <- d0
  for (cl in unique(cell)) { idx <- which(cell == cl); f <- unique(d0$fact[idx]); map <- setNames(sample(f), f); d$fact[idx] <- map[as.character(d0$fact[idx])] }
  icc(d) })
cat(sprintf("fc=%.1f: H0 datasets ICC1 mean %.4f sd %.4f q95 %.4f | permutations mean %.4f sd %.4f q95 %.4f | P(obs > perm q95) %.2f\n",
  A, mean(obs), sd(obs), quantile(obs, .95), mean(perm), sd(perm), quantile(perm, .95), mean(obs > quantile(perm, .95))))
