# P2 analysis model (prereg/P2_prompt_vs_fact.md, A4). Functions shared by the confirmatory analysis and
# the bootstrap-selection simulation.
#
# Data: one row per (fact, template, carrier) with outcome y (D1 or D4 normalized depth).
# Templates are relation-specific but each template_id is one of 10 frames shared by all relations, so
#   relation:template == relation:frame.
# Model (REML, convergence checks ON):
#   y ~ covariates + (1|relation) + (1|frame) + (1|relation:template) + (1|subject) + (1|fact)
#       + (1|fact:template) + (1|fact:carrier) + residual
# (1|fact:template) is added to the human's formula so that the fact x wording interaction (G1's
# "residual") is separated from carrier-level noise; the combined residual is also reported.
# Shares are on the carrier-averaged scale with relation removed (within-relation), nc carriers:
#   denom   = f + rt + fr + ft + fc/nc + e/nc,   f = fact + subject
#   ICC1    = f / denom                          (primary fact share)
#   wording = (rt + fr + ft) / denom             (H1 wording share; G1 analogue: template-main + residual)
#   diff    = wording - ICC1
#   G(k)    = f / (f + ft/k + fc/nc + e/(k nc))  (relative: the same k templates for every fact)
#   Phi(k)  = f / (f + (rt + fr + ft)/k + fc/nc + e/(k nc))
suppressPackageStartupMessages({library(lme4)})

p2_formula <- function(y = "y", cov = character(0), subject = TRUE) {
  re <- "(1|relation) + (1|frame) + (1|rt) + (1|fact) + (1|ft) + (1|fc)"
  if (subject) re <- paste(re, "+ (1|subject)")
  as.formula(paste(y, "~", paste(c("1", cov), collapse = " + "), "+", re))
}

p2_prep <- function(d) {
  d$rt <- factor(paste(d$relation, d$template_id, sep = ":"))
  d$ft <- factor(paste(d$fact, d$template_id, sep = ":"))
  d$fc <- factor(paste(d$fact, d$carrier, sep = ":"))
  for (v in c("relation", "frame", "fact", "subject")) if (v %in% names(d)) d[[v]] <- factor(d[[v]])
  d
}

p2_fit <- function(d, y = "y", cov = character(0), subject = TRUE) {
  w <- character(0)
  m <- withCallingHandlers(
    lmer(p2_formula(y, cov, subject), data = d, REML = TRUE, control = lmerControl(calc.derivs = TRUE)),
    warning = function(x) { w <<- c(w, conditionMessage(x)); invokeRestart("muffleWarning") })
  v <- as.data.frame(VarCorr(m)); v <- setNames(v$vcov, v$grp)
  list(model = m, vc = v, singular = isSingular(m), warnings = w)
}

p2_shares <- function(v, nc = 3) {
  g <- function(k) if (k %in% names(v)) unname(v[k]) else 0
  f <- g("fact") + g("subject"); rt <- g("rt"); fr <- g("frame"); ft <- g("ft"); fc <- g("fc"); e <- g("Residual")
  den <- f + rt + fr + ft + fc / nc + e / nc
  k <- 1:30
  G <- f / (f + ft / k + fc / nc + e / (k * nc)); Phi <- f / (f + (rt + fr + ft) / k + fc / nc + e / (k * nc))
  tot <- den + g("relation")
  list(icc1 = f / den, wording = (rt + fr + ft) / den, diff = (rt + fr + ft - f) / den,
       share_total = list(fact = f / tot, relation = g("relation") / tot, frame = fr / tot, rt = rt / tot, ft = ft / tot,
                          fc = fc / nc / tot, residual = e / nc / tot),
       template_plus_frame_minus_residual = (rt + fr - ft - e / nc) / den,
       G_k = G, Phi_k = Phi, nprime_G = if (any(G >= 0.8)) min(k[G >= 0.8]) else NA,
       nprime_Phi = if (any(Phi >= 0.8)) min(k[Phi >= 0.8]) else NA)
}

# Simulated data on the exact P2 design (facts, relations, 10 frames, nc carriers) with planted components
# (variances) and missing (fact, template) cells at rate miss (dropped across all carriers).
p2_simulate <- function(design, comp, miss = 0, seed = 1, nc = 3) {
  set.seed(seed)
  facts <- design$facts; rels <- unique(facts$relation); frames <- 0:9
  re <- function(n, s2) rnorm(n, 0, sqrt(s2))
  a_rel <- setNames(re(length(rels), comp$relation), rels)
  a_fr <- setNames(re(10, comp$frame), frames)
  a_rt <- setNames(re(length(rels) * 10, comp$rt), as.vector(outer(rels, frames, paste, sep = ":")))
  a_f <- setNames(re(nrow(facts), comp$fact), facts$fact)
  d <- expand.grid(i = seq_len(nrow(facts)), template_id = frames, carrier = seq_len(nc) - 1)
  d$fact <- facts$fact[d$i]; d$relation <- facts$relation[d$i]; d$subject <- facts$subject[d$i]; d$frame <- d$template_id
  keep_cells <- unique(d[, c("fact", "template_id")])
  keep_cells <- keep_cells[runif(nrow(keep_cells)) >= miss, ]
  d <- merge(d, keep_cells, by = c("fact", "template_id"))
  ftk <- paste(d$fact, d$template_id, sep = ":"); fck <- paste(d$fact, d$carrier, sep = ":")
  a_ft <- setNames(re(length(unique(ftk)), comp$ft), unique(ftk))
  a_fc <- setNames(re(length(unique(fck)), comp$fc), unique(fck))
  d$y <- 0.6 + a_rel[d$relation] + a_fr[as.character(d$frame)] + a_rt[paste(d$relation, d$frame, sep = ":")] +
    a_f[d$fact] + a_ft[ftk] + a_fc[fck] + re(nrow(d), comp$e)
  d$i <- NULL
  p2_prep(d)
}

p2_truth <- function(comp, nc = 3) {
  v <- c(relation = comp$relation, frame = comp$frame, rt = comp$rt, fact = comp$fact, ft = comp$ft, fc = comp$fc,
         Residual = comp$e)
  p2_shares(v, nc)
}
