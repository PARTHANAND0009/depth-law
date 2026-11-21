# EXPLORATORY (post hoc, not preregistered) — E-depthvar B7b planted-depth recovery (bias arm, lme4).
# Simulates on a model's exact correct-cell design: latent midpoint m = mu + relation + relation:template +
# fact + residual with planted shares; per-cell sigmoid curves p(l) = sigmoid(((l+1)/L - m)/s) on the model's
# layer grid (3 identical carriers; D1 and D4 are scale-free in p, so the final probability does not matter);
# applies D1 and D4; refits the B3 model; returns recovered shares per simulation.
# Usage: Rscript <this> <cells.csv> <out.json> n_sim=50 seed=20261121 cores=3
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
a <- commandArgs(trailingOnly = TRUE); csv <- a[1]; out <- a[2]
kv <- list(n_sim = "50", seed = "20261121", cores = "1", s = "0.05")
for (x in a[-(1:2)]) { p <- strsplit(x, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
d <- read.csv(csv, stringsAsFactors = FALSE); d <- d[d$correct == 1, ]
L <- d$L[1]; mu <- mean(d$D1); V <- var(d$D1); s <- as.numeric(kv$s)
d$rt <- paste(d$relation, d$template_id, sep = ":")
lay <- (seq_len(L)) / L
CTL <- lmerControl(calc.derivs = FALSE)
depths <- function(m) {  # D1 and D4 from p(l) = sigmoid((lay - m)/s), vectorized over cells
  P <- plogis(outer(-m, lay, "+") / s)                 # cells x L
  pf <- P[, L]
  ok <- P >= 0.5 * pf
  # first layer from which ok stays TRUE to the end
  last_bad <- apply(!ok, 1, function(r) { w <- which(r); if (length(w)) max(w) else 0 })
  D1 <- (last_bad + 1) / L
  D4 <- 1 - rowMeans(pmin(P / pf, 1))
  cbind(D1 = D1, D4 = D4)
}
shares_of <- function(y, dd) {
  dd$y <- y
  m <- lmer(y ~ 1 + (1|relation) + (1|rt) + (1|subject) + (1|fact_id), data = dd, REML = TRUE, control = CTL)
  v <- as.data.frame(VarCorr(m)); v <- setNames(v$vcov, v$grp); tot <- sum(v)
  c(fact_subject = unname(v["fact_id"] + v["subject"]) / tot, template_main = unname(v["rt"]) / tot,
    residual = unname(v["Residual"]) / tot, relation = unname(v["relation"]) / tot)
}
conds <- expand.grid(fact = c(0.1, 0.3, 0.5, 0.7), tmpl = c(0.05, 0.2)); rel <- 0.05
dd <- d[, c("relation", "rt", "subject", "fact_id")]
for (v in names(dd)) dd[[v]] <- factor(dd[[v]])
run_cond <- function(ci) {
  cf <- conds$fact[ci]; ct <- conds$tmpl[ci]; ce <- 1 - rel - cf - ct
  rows <- lapply(seq_len(as.integer(kv$n_sim)), function(i) {
    set.seed(as.integer(kv$seed) + 1000 * ci + i)
    re <- function(f, sh) { lv <- levels(f); x <- rnorm(length(lv), 0, sqrt(sh * V)); x[as.integer(f)] }
    m <- mu + re(dd$relation, rel) + re(dd$rt, ct) + re(dd$fact_id, cf) + rnorm(nrow(dd), 0, sqrt(ce * V))
    D <- depths(m)
    r1 <- tryCatch(shares_of(D[, "D1"], dd), error = function(e) rep(NA, 4))
    r4 <- tryCatch(shares_of(D[, "D4"], dd), error = function(e) rep(NA, 4))
    c(D1 = r1, D4 = r4)
  })
  list(planted = list(fact = cf, template_main = ct, relation = rel, residual = ce), draws = do.call(rbind, rows))
}
res <- mclapply(seq_len(nrow(conds)), run_cond, mc.cores = as.integer(kv$cores))
outl <- lapply(res, function(r) list(planted = r$planted, draws = lapply(as.data.frame(r$draws), function(x) x)))
writeLines(toJSON(list(n_sim = as.integer(kv$n_sim), seed = as.integer(kv$seed), L = L, mu = mu, V = V, s = s,
                       n_cells = nrow(d), conditions = outl), auto_unbox = TRUE, digits = NA, na = "null"), out)
