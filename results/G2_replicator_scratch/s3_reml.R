# REML point fits on own tables; reuses only p2_formula/p2_prep/p2_fit/p2_shares from analysis/p2/p2_model.R
source("/home/user/depth-law/analysis/p2/p2_model.R")
library(jsonlite)
S <- "/tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/g2rep/"
cov <- c("n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior")
out <- list()
for (k in c("llama", "olmo")) {
  d <- read.csv(paste0(S, "tab_", k, ".csv"))
  d <- p2_prep(d)
  for (y in c("D1", "D4")) {
    f <- p2_fit(d, y = y, cov = cov, subject = FALSE, carrier = TRUE)
    sh <- p2_shares(f$vc, nc = 3)
    v <- f$vc
    ceil <- unname(v["fact"] / (v["fact"] + v["fc"] / 3))
    out[[paste(k, y, sep = "_")]] <- list(vc = as.list(v), icc1 = sh$icc1, wording = sh$wording, diff = sh$diff,
      tf_minus_resid = sh$template_plus_frame_minus_residual, nprime_G = sh$nprime_G, G_k = sh$G_k, ceiling = ceil,
      share_total = sh$share_total, singular = f$singular, warnings = f$warnings, nobs = nobs(f$model),
      formula = deparse(formula(f$model), width.cutoff = 500))
    cat(k, y, "icc1", sh$icc1, "wording", sh$wording, "diff", sh$diff, "n'", sh$nprime_G, "ceil", ceil,
        "tf-res", sh$template_plus_frame_minus_residual, "sing", f$singular, "warn", length(f$warnings), "\n")
  }
}
write_json(out, paste0(S, "s3_reml.json"), auto_unbox = TRUE, digits = NA, pretty = TRUE)
