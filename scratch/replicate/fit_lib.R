suppressPackageStartupMessages({library(lme4); library(jsonlite)})
D <- "/home/user/depth-law/scratch/replicate"
FX <- c("n_answer_tokens","log_prior","obj_logprob_final","n_subject_tokens","subj_final_dist")
load_tab <- function(m) {
  d <- read.csv(file.path(D, paste0("tab_", m, ".csv")), stringsAsFactors = FALSE)
  for (v in FX) d[[v]] <- as.numeric(scale(d[[v]]))
  d$rt <- paste(d$relation, d$template_id, sep = ":")
  d
}
F_H1 <- y ~ n_answer_tokens + log_prior + obj_logprob_final + n_subject_tokens + subj_final_dist +
  (1|relation) + (1|rt) + (1|subject)
F_H3 <- update(F_H1, . ~ . + cooc_within)
F_OR <- correct ~ cooc_within + n_answer_tokens + log_prior + n_subject_tokens + subj_final_dist + factor(relation)
vcs <- function(fit) { v <- as.data.frame(VarCorr(fit)); setNames(v$vcov, v$grp) }
icc <- function(fit) { v <- vcs(fit); unname(v["relation"] / sum(v[c("relation","rt","subject","Residual")])) }
r2m <- function(fit) {
  vf <- var(as.vector(model.matrix(fit) %*% fixef(fit))); v <- vcs(fit)
  vf / (vf + sum(v[c("relation","rt","subject","Residual")]))
}
ctrl <- lmerControl(calc.derivs = FALSE)
fit_h1 <- function(d) lmer(F_H1, data = d, REML = TRUE, control = ctrl)
dr2_fn <- function(d) {
  f0 <- lmer(F_H1, data = d, REML = FALSE, control = ctrl); f1 <- lmer(F_H3, data = d, REML = FALSE, control = ctrl)
  c(r2m0 = r2m(f0), r2m1 = r2m(f1), dr2 = r2m(f1) - r2m(f0))
}
or_fn <- function(d) exp(coef(glm(F_OR, data = d, family = binomial()))[["cooc_within"]])
# relation-cluster resample: duplicated relations get new labels for relation, rt, subject
resample <- function(d, rels) {
  sp <- split(d, d$relation); seen <- list(); out <- vector("list", length(rels))
  for (i in seq_along(rels)) {
    r <- rels[i]; k <- if (is.null(seen[[r]])) 1L else seen[[r]] + 1L; seen[[r]] <- k
    x <- sp[[r]]
    if (k > 1) { tag <- paste0("#", k); x$relation <- paste0(x$relation, tag); x$rt <- paste0(x$rt, tag); x$subject <- paste0(x$subject, tag) }
    out[[i]] <- x
  }
  do.call(rbind, out)
}
