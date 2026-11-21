# EXPLORATORY (post hoc, not preregistered) — E-depthvar B3/B5/B7c fits (lme4 REML) and the B3 bootstrap.
# Usage: Rscript <this> <task> <cells.csv> <out.json> key=value ...
#   task point : B3 components, shares, ICC(1), D-study; with cov=1 also B5 (joint + one at a time)
#   task boot  : 1000 cluster-bootstrap resamples of facts within relation (relabelled duplicates)
#   task carrier: B7c carrier facet on the long per-carrier table
#   keys: y=<outcome col> set=correct|all3|all  n_boot=1000 seed=20261121 cores=1
suppressPackageStartupMessages({library(lme4); library(jsonlite); library(parallel)})
a <- commandArgs(trailingOnly = TRUE); task <- a[1]; csv <- a[2]; out <- a[3]
kv <- list(y = "D1", set = "correct", n_boot = "1000", seed = "20261121", cores = "1", cov = "0")
for (s in a[-(1:3)]) { p <- strsplit(s, "=", fixed = TRUE)[[1]]; kv[[p[1]]] <- p[2] }
d0 <- read.csv(csv, stringsAsFactors = FALSE)
if (kv$set == "correct") d0 <- d0[d0$correct == 1, ]
if (kv$set == "all3") d0 <- d0[d0$n_correct_templates == 3 & d0$correct == 1, ]
d0 <- d0[!is.na(d0[[kv$y]]), ]
CTL <- lmerControl(calc.derivs = FALSE)
COV <- c("tmpl_len_tokens", "subj_final_dist", "n_subj_tokens", "answer_prior", "final_logp", "log_cooc")
prep <- function(d) {
  d$rt <- paste(d$relation, d$template_id, sep = ":")
  for (v in c("relation", "rt", "subject", "fact_id")) d[[v]] <- factor(d[[v]])
  d
}
RE <- "(1|relation) + (1|rt) + (1|subject) + (1|fact_id)"
fit <- function(d, y, fixed = "1", re = RE)
  lmer(as.formula(paste(y, "~", fixed, "+", re)), data = d, REML = TRUE, control = CTL)
vcs <- function(m) { v <- as.data.frame(VarCorr(m)); setNames(v$vcov, v$grp) }
summ <- function(v) {
  tot <- sum(v); fs <- unname(v["fact_id"] + v["subject"]); rt <- unname(v["rt"]); e <- unname(v["Residual"])
  k <- 1:30
  phi <- fs / (fs + (rt + e) / k); g <- fs / (fs + e / k)
  list(vc = as.list(v), share = as.list(v / tot),
       share_fact_subject = fs / tot, share_template_main = rt / tot, share_residual = e / tot,
       share_relation = unname(v["relation"]) / tot,
       diff_prompt_minus_fact = (rt + e - fs) / tot,
       icc1 = fs / (fs + rt + e), icc1_rel = fs / (fs + e),
       phi_k = phi, g_k = g,
       nprime_phi = if (any(phi >= 0.8)) min(k[phi >= 0.8]) else NA,
       nprime_g = if (any(g >= 0.8)) min(k[g >= 0.8]) else NA,
       g3 = fs / (fs + e / 3), phi3 = fs / (fs + (rt + e) / 3))
}
warn <- function(m) { w <- m@optinfo$conv$lme4$messages; if (is.null(w)) character(0) else w }
d <- prep(d0)
res <- list(task = task, y = kv$y, set = kv$set, n_cells = nrow(d), n_facts = nlevels(d$fact_id),
            n_relations = nlevels(d$relation), n_rt = nlevels(d$rt), seed = as.integer(kv$seed),
            facts_per_relation = as.list(table(unique(d0[, c("fact_id", "relation")])$relation)))
if (task == "point") {
  m <- fit(d, kv$y)
  res <- c(res, summ(vcs(m)), list(singular = isSingular(m), warnings = warn(m)))
  if (kv$cov == "1") {
    for (v in COV) d[[v]] <- as.numeric(scale(d[[v]]))
    keep <- COV[sapply(COV, function(v) sd(d[[v]], na.rm = TRUE) > 0 && !any(is.na(d[[v]])))]
    base <- vcs(m)
    mj <- fit(d, kv$y, paste(keep, collapse = " + "))
    one <- lapply(keep, function(v) { vv <- vcs(fit(d, kv$y, v)); as.list((vv - base[names(vv)]) / base[names(vv)]) })
    names(one) <- keep
    vj <- vcs(mj)
    res$covariates <- list(used = keep, joint_vc = as.list(vj), joint_pct_change = as.list((vj - base[names(vj)]) / base[names(vj)]),
                           joint_summary = summ(vj), one_at_a_time_pct_change = one, joint_fixef = as.list(fixef(mj)))
  }
} else if (task == "boot") {
  nb <- as.integer(kv$n_boot); seed <- as.integer(kv$seed)
  fr <- split(unique(d0[, c("fact_id", "relation")])$fact_id, unique(d0[, c("fact_id", "relation")])$relation)
  byfact <- split(seq_len(nrow(d0)), d0$fact_id)
  one <- function(b) {
    set.seed(seed + b)
    idx <- list(); j <- 0
    for (r in names(fr)) {
      f <- fr[[r]]; pick <- f[sample.int(length(f), length(f), replace = TRUE)]
      for (i in seq_along(pick)) { j <- j + 1; g <- d0[byfact[[pick[i]]], ]
        g$fact_id <- paste0(g$fact_id, "#", j); g$subject <- paste0(g$subject, "#", j); idx[[j]] <- g }
    }
    db <- prep(do.call(rbind, idx))
    s <- tryCatch(summ(vcs(fit(db, kv$y))), error = function(e) NULL)
    if (is.null(s)) return(rep(NA, 9))
    c(s$share_fact_subject, s$share_template_main, s$share_residual, s$share_relation, s$diff_prompt_minus_fact,
      s$icc1, ifelse(is.na(s$nprime_phi), 31, s$nprime_phi), s$g3, s$phi3)
  }
  rr <- do.call(rbind, mclapply(seq_len(nb), one, mc.cores = as.integer(kv$cores)))
  colnames(rr) <- c("fact_subject", "template_main", "residual", "relation", "diff_prompt_minus_fact", "icc1", "nprime_phi", "g3", "phi3")
  res$n_boot <- nb; res$n_failed <- sum(is.na(rr[, 1]))
  res$draws <- lapply(as.data.frame(rr), function(x) x)
} else if (task == "carrier") {
  d$fc <- factor(paste(d$fact_id, d$carrier)); d$rtc <- factor(paste(d$rt, d$carrier)); d$carrier <- factor(d$carrier)
  m <- lmer(as.formula(paste(kv$y, "~ 1 + (1|relation) + (1|rt) + (1|subject) + (1|fact_id) + (1|carrier) + (1|fc) + (1|rtc)")),
            data = d, REML = TRUE, control = CTL)
  v <- vcs(m)
  res <- c(res, list(vc = as.list(v), share = as.list(v / sum(v)), singular = isSingular(m), warnings = warn(m)))
}
writeLines(toJSON(res, auto_unbox = TRUE, digits = NA, na = "null"), out)
