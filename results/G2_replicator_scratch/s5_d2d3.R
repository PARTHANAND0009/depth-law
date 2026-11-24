source("/home/user/depth-law/analysis/p2/p2_model.R")
S <- "/tmp/claude-0/-home-user-depth-law/79d106ca-74b7-5e19-8ef3-6880f992c1ff/scratchpad/g2rep/"
cov <- c("n_answer_tokens", "n_subject_tokens", "log_cooc_proxy", "answer_prior")
for (k in c("llama", "olmo")) for (y in c("D2", "D3")) {
  d <- read.csv(paste0(S, "tab_", k, ".csv")); d <- d[!is.na(d[[y]]), ]
  # covariates re-z-scored within this outcome's rows is irrelevant (affine invariance); keep as is
  d <- p2_prep(d); f <- p2_fit(d, y = y, cov = cov, subject = FALSE, carrier = TRUE); sh <- p2_shares(f$vc, 3)
  cat(k, y, "rows", nrow(d), "icc1", sprintf("%.4f", sh$icc1), "diff", sprintf("%.4f", sh$diff), "\n")
}
for (k in c("llama", "olmo")) { }
