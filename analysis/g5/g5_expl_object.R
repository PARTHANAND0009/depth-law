# EXPLORATORY (not preregistered; G5 reviews: skeptic F4, reviewer-sim point 2). Study 2, set correct, D1 and D4.
# Refits the frozen P2 formula (analysis/p2/p2_model.R) with
#   (a) an added relation:object random intercept (answer identity within relation),
#   (b) an added cell-level covariate z(obj_first_logprob) (final confidence of the unpatched prompt),
#   (c) both.
# Point estimates only (no bootstrap). Shares within relation on the carrier-averaged scale, as in p2_shares, with
# the object component added to the denominator. Usage: Rscript g5_expl_object.R <out.json> <long.csv>=<label> ...
suppressPackageStartupMessages({library(lme4); library(jsonlite)})
source("analysis/p2/p2_model.R")
a <- commandArgs(trailingOnly = TRUE); out <- a[1]
facts <- stream_in(file("materials/facts_v1.jsonl"), verbose = FALSE)
obj <- setNames(facts$object, facts$fact_id)
COV <- c("n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior")
res <- list()
for (arg in a[-1]) {
  p <- strsplit(arg, "=", fixed = TRUE)[[1]]; csv <- p[1]; lab <- p[2]
  d0 <- read.csv(csv, stringsAsFactors = FALSE); d0$fact <- d0$fact_id
  d0$object <- obj[d0$fact_id]; stopifnot(!any(is.na(d0$object)))
  d0$ro <- factor(paste(d0$relation, d0$object, sep = ":"))
  d0$lp_z <- as.numeric(scale(d0$obj_first_logprob))
  nc <- length(unique(d0$carrier))
  for (y in c("D1", "D4")) {
    d <- d0; d$y <- d[[y]]; d <- d[!is.na(d$y), ]; d <- p2_prep(d)
    fit <- function(extra_re = "", extra_fx = character(0)) {
      f <- p2_formula("y", c(COV, extra_fx), subject = FALSE, carrier = TRUE)
      if (nzchar(extra_re)) f <- update(f, as.formula(paste(". ~ . +", extra_re)))
      w <- character(0)
      m <- withCallingHandlers(lmer(f, data = d, REML = TRUE, control = lmerControl(calc.derivs = TRUE)),
                               warning = function(x) { w <<- c(w, conditionMessage(x)); invokeRestart("muffleWarning") })
      v <- as.data.frame(VarCorr(m)); v <- setNames(v$vcov, v$grp)
      g <- function(k) if (k %in% names(v)) unname(v[k]) else 0
      den <- g("fact") + g("ro") + g("rt") + g("frame") + g("ft") + g("fc") / nc + g("Residual") / nc
      list(vc = as.list(v), fact_share = g("fact") / den, object_share = g("ro") / den,
           wording_share = (g("rt") + g("frame") + g("ft")) / den, fact_plus_object = (g("fact") + g("ro")) / den,
           singular = isSingular(m), warnings = w, n_rows = nrow(d),
           n_objects = nlevels(d$ro), n_facts = length(unique(d$fact)))
    }
    res[[lab]][[y]] <- list(base = fit(), object = fit("(1|ro)"), logprob = fit("", "lp_z"),
                            object_logprob = fit("(1|ro)", "lp_z"))
    cat(lab, y, "done\n")
  }
}
writeLines(toJSON(list(status = "EXPLORATORY", note = "point estimates; frozen formula plus terms named in each entry",
                       results = res), auto_unbox = TRUE, digits = NA, pretty = TRUE), out)
