# Revised H-R fits (prereg/HR_revised.md B4-B9). Called from depthlaw.hr.run.
# Usage: Rscript hr_fit.R <task> <csv> <out.json> [key=value ...]
#   tasks: main | boot | split | variant | surv
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
args <- commandArgs(trailingOnly = TRUE)
task <- args[1]; csv <- args[2]; out <- args[3]
kv <- list(n_boot = "2000", seed = "20261121", cores = "1", y = "y", subset = "all", template_re = "1",
           n_split = "200", chunk = "0")
for (a in args[-(1:3)]) { p <- strsplit(a, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
d0 <- read.csv(csv, stringsAsFactors = FALSE)
FC <- c("n_answer_tokens", "log_prior", "obj_logprob_final", "n_subject_tokens", "subj_final_dist")
CTL <- lmerControl(calc.derivs = FALSE)

prep <- function(d) {
  d$relation <- factor(d$relation); d$rt <- factor(paste(d$relation, d$template_id, sep = ":"))
  d$subject <- factor(d$subject); d
}
fml <- function(y, extra = NULL, template_re = TRUE) {
  re <- if (template_re) "(1|relation) + (1|rt) + (1|subject)" else "(1|relation) + (1|subject)"
  as.formula(paste(y, "~", paste(c(FC, extra), collapse = " + "), "+", re))
}
vc_tab <- function(m) { v <- as.data.frame(VarCorr(m)); setNames(v$vcov, v$grp) }
icc <- function(m) { v <- vc_tab(m); unname(v["relation"] / sum(v)) }
r2m <- function(m) {
  f <- as.vector(model.matrix(m) %*% fixef(m)); vf <- var(f); vf / (vf + sum(vc_tab(m)))
}
warn_of <- function(m) { w <- m@optinfo$conv$lme4$messages; if (is.null(w)) character(0) else w }
blup <- function(m) { r <- ranef(m)$relation; setNames(r[, 1], rownames(r)) }

h1 <- function(d, y = "y", template_re = TRUE) lmer(fml(y, NULL, template_re), data = d, REML = TRUE, control = CTL)
h3 <- function(d, y = "y", template_re = TRUE) {
  m0 <- lmer(fml(y, NULL, template_re), data = d, REML = FALSE, control = CTL)
  m1 <- lmer(fml(y, "cooc_within", template_re), data = d, REML = FALSE, control = CTL)
  list(m0 = m0, m1 = m1, dr2 = r2m(m1) - r2m(m0))
}
orfit <- function(d) {
  g <- glm(correct ~ cooc_within + n_answer_tokens + log_prior + n_subject_tokens + subj_final_dist + relation,
           family = binomial, data = d)
  unname(coef(g)["cooc_within"])
}
resample <- function(d, rels, k) {
  parts <- lapply(seq_along(rels), function(i) {
    g <- d[d$relation == rels[i], ]
    g$relation <- paste0(rels[i], "#", i); g$subject <- paste0(g$subject, "#", i); g
  })
  prep(do.call(rbind, parts))
}

d <- prep(d0)
res <- list(task = task, csv = csv, n_rows = nrow(d), n_relations = nlevels(d$relation), seed = as.integer(kv$seed),
            R = R.version.string, lme4 = as.character(packageVersion("lme4")))

if (task == "main") {
  m <- h1(d)
  hh <- h3(d)
  cf <- summary(hh$m1)$coefficients
  g <- glm(correct ~ cooc_within + n_answer_tokens + log_prior + n_subject_tokens + subj_final_dist + relation,
           family = binomial, data = d)
  res <- c(res, list(icc_rel = icc(m), vc = as.list(vc_tab(m)), fixef = as.list(fixef(m)), blup = as.list(blup(m)),
                     warnings_h1 = warn_of(m), r2m_m0 = r2m(hh$m0), r2m_m1 = r2m(hh$m1), dr2 = hh$dr2,
                     cooc_coef = cf["cooc_within", "Estimate"], cooc_se = cf["cooc_within", "Std. Error"],
                     warnings_h3 = c(warn_of(hh$m0), warn_of(hh$m1)),
                     log_or = unname(coef(g)["cooc_within"]), log_or_se_model = summary(g)$coefficients["cooc_within", 2],
                     n_correct = sum(d$correct)))
} else if (task == "boot") {
  rels <- levels(d$relation); nb <- as.integer(kv$n_boot); seed <- as.integer(kv$seed)
  one <- function(b) {
    set.seed(seed + b)
    db <- resample(d0, sample(rels, length(rels), replace = TRUE))
    o <- c(icc = NA, dr2 = NA, log_or = NA)
    try(o["icc"] <- icc(h1(db)), silent = TRUE)
    try(o["dr2"] <- h3(db)$dr2, silent = TRUE)
    try(o["log_or"] <- orfit(db), silent = TRUE)
    o
  }
  rr <- do.call(rbind, mclapply(seq_len(nb), one, mc.cores = as.integer(kv$cores)))
  res <- c(res, list(n_boot = nb, icc = rr[, "icc"], dr2 = rr[, "dr2"], log_or = rr[, "log_or"]))
} else if (task == "split") {
  ns <- as.integer(kv$n_split); seed <- as.integer(kv$seed)
  one <- function(s) {
    set.seed(seed + s)
    half <- unlist(lapply(split(unique(d0[, c("fact_id", "relation")]), unique(d0[, c("fact_id", "relation")])$relation),
                          function(g) sample(g$fact_id, floor(nrow(g) / 2))))
    a <- prep(d0[d0$fact_id %in% half, ]); b <- prep(d0[!(d0$fact_id %in% half), ])
    ba <- blup(h1(a)); bb <- blup(h1(b)); r <- intersect(names(ba), names(bb))
    cor(ba[r], bb[r], method = "spearman")
  }
  r <- unlist(mclapply(seq_len(ns), one, mc.cores = as.integer(kv$cores)))
  res <- c(res, list(n_split = ns, r = r, r_sb = 2 * r / (1 + r)))
} else if (task == "variant") {
  y <- kv$y; tre <- kv$template_re == "1"
  dv <- prep(d0[!is.na(d0[[y]]), ])
  res$n_rows <- nrow(dv); res$n_relations <- nlevels(dv$relation)
  m <- h1(dv, y, tre); hh <- h3(dv, y, tre)
  res <- c(res, list(y = y, template_re = tre, icc_rel = icc(m), vc = as.list(vc_tab(m)), blup = as.list(blup(m)),
                     dr2 = hh$dr2, warnings = c(warn_of(m), warn_of(hh$m0), warn_of(hh$m1))))
} else if (task == "surv") {
  L <- d0$L[1]; idx <- rep(seq_len(nrow(d0)), d0$event_layer)
  pp <- d0[idx, c("relation", FC, "cooc_within", "event_layer")]
  pp$layer <- sequence(d0$event_layer); pp$event <- as.integer(pp$layer == pp$event_layer)
  pp$bin <- factor(pmin(8, ceiling(8 * pp$layer / L)))
  pp$relation <- factor(pp$relation)
  m <- glmer(event ~ 0 + bin + n_answer_tokens + log_prior + obj_logprob_final + n_subject_tokens + subj_final_dist +
               cooc_within + (1|relation), family = binomial(link = "cloglog"), data = pp,
             control = glmerControl(calc.derivs = FALSE))
  cf <- summary(m)$coefficients
  b <- cf["cooc_within", "Estimate"]; se <- cf["cooc_within", "Std. Error"]
  res <- c(res, list(n_person_periods = nrow(pp), frailty_sd = attr(VarCorr(m)$relation, "stddev")[[1]],
                     hr_cooc = exp(b), hr_cooc_ci = exp(b + c(-1, 1) * 1.959964 * se), p_cooc = cf["cooc_within", 4],
                     frailty_blup = as.list(blup(m)), warnings = warn_of(m)))
}
writeLines(toJSON(res, auto_unbox = TRUE, digits = NA, na = "null"), out)
