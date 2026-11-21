source("/home/user/depth-law/scratch/replicate/fit_lib.R")
args <- commandArgs(TRUE); NB <- as.integer(args[1]); NS <- as.integer(args[2])
set.seed(20261121)
res <- list()
for (m in c("pythia-1.4b","pythia-2.8b","OLMo-2-1124-7B")) {
  d <- load_tab(m); R <- sort(unique(d$relation))
  B <- matrix(NA_real_, NB, 3, dimnames = list(NULL, c("icc","dr2","or"))); nfail <- c(icc=0, dr2=0, or=0); nwarn <- 0
  t0 <- Sys.time()
  for (b in seq_len(NB)) {
    db <- resample(d, sample(R, length(R), replace = TRUE))
    B[b, "icc"] <- tryCatch(withCallingHandlers(icc(fit_h1(db)), warning = function(w) {nwarn <<- nwarn + 1; invokeRestart("muffleWarning")}), error = function(e) {nfail["icc"] <<- nfail["icc"] + 1; NA})
    B[b, "dr2"] <- tryCatch(suppressWarnings(dr2_fn(db)[["dr2"]]), error = function(e) {nfail["dr2"] <<- nfail["dr2"] + 1; NA})
    B[b, "or"] <- tryCatch(suppressWarnings(or_fn(db)), error = function(e) {nfail["or"] <<- nfail["or"] + 1; NA})
    if (b %% 250 == 0) cat(m, b, format(Sys.time() - t0), "\n")
  }
  write.csv(B, file.path(D, paste0("boot_", m, ".csv")), row.names = FALSE)
  q <- function(x) unname(quantile(x, c(.025, .975), na.rm = TRUE))
  # split-half
  facts <- unique(d[, c("fact_id","relation")]); rsb <- numeric(NS); rr <- numeric(NS)
  for (s in seq_len(NS)) {
    ha <- unlist(lapply(split(facts$fact_id, facts$relation), function(f) sample(f, length(f) %/% 2)))
    bl <- lapply(list(d[d$fact_id %in% ha, ], d[!d$fact_id %in% ha, ]), function(h) {
      re <- ranef(suppressMessages(suppressWarnings(fit_h1(h))))$relation; setNames(re[,1], rownames(re))[R] })
    r <- suppressWarnings(cor(bl[[1]], bl[[2]], method = "spearman")); rr[s] <- r
    rsb[s] <- 2 * r / (1 + r)
  }
  write.csv(data.frame(r = rr, r_sb = rsb), file.path(D, paste0("split_", m, ".csv")), row.names = FALSE)
  und <- is.na(rsb); r0 <- ifelse(und, 0, rsb)
  res[[m]] <- list(nboot = NB, nfail = as.list(nfail), n_icc_warn = nwarn,
    icc_ci = q(B[, "icc"]), dr2_ci = q(B[, "dr2"]), or_ci = q(B[, "or"]),
    nsplit = NS, split_n_undefined = sum(und), split_mean_defined = mean(rsb[!und]),
    split_mean_undef0 = mean(r0), split_pct_defined = q(rsb[!und]))
  cat(toJSON(res[[m]], auto_unbox = TRUE, digits = 8), "\n")
}
write(toJSON(res, auto_unbox = TRUE, digits = NA, pretty = TRUE), file.path(D, "boot.json"))
