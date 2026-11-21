source("/home/user/depth-law/scratch/replicate/fit_lib.R")
set.seed(1)  # different seed from the 20261121 run, to measure Monte Carlo spread
m <- "pythia-2.8b"; NS <- 1000
d <- load_tab(m); R <- sort(unique(d$relation)); facts <- unique(d[, c("fact_id","relation")])
rsb <- numeric(NS); zero_half <- integer(NS)
for (s in seq_len(NS)) {
  ha <- unlist(lapply(split(facts$fact_id, facts$relation), function(f) sample(f, length(f) %/% 2)))
  bl <- lapply(list(d[d$fact_id %in% ha, ], d[!d$fact_id %in% ha, ]), function(h) {
    re <- ranef(suppressMessages(suppressWarnings(fit_h1(h))))$relation; setNames(re[,1], rownames(re))[R] })
  zero_half[s] <- sum(sapply(bl, function(b) all(b == 0)))
  r <- suppressWarnings(cor(bl[[1]], bl[[2]], method = "spearman")); rsb[s] <- 2 * r / (1 + r)
}
und <- is.na(rsb)
cat("undefined total", sum(und), "of", NS, "; undefined all due to an all-zero BLUP half:", all(zero_half[und] > 0), "\n")
blk <- split(seq_len(NS), rep(1:5, each = 200))
for (b in blk) cat("block undefined", sum(und[b]), "mean_defined", round(mean(rsb[b][!und[b]]), 4), "mean_undef0", round(mean(ifelse(und[b], 0, rsb[b])), 4), "\n")
