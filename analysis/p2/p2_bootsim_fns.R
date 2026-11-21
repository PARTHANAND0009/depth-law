# Two-way cluster bootstrap (facts within relation AND frames), shared by p2_analysis.R (and identical in
# logic to twoway() in p2_bootsim.R). Returns an nb x k matrix of stat(model) values.
twoway_boot <- function(d, nb, seed, COV = character(0), subj = FALSE, stat, cores = 1) {
  fr <- unique(d[, c("fact", "relation")]); rels <- split(as.character(fr$fact), fr$relation)
  byf <- split(seq_len(nrow(d)), as.character(d$fact))
  one <- function(b) {
    set.seed(seed + b)
    frs <- sample(0:9, 10, replace = TRUE); parts <- list(); j <- 0
    for (r in names(rels)) {
      ff <- rels[[r]]; pick <- ff[sample.int(length(ff), length(ff), replace = TRUE)]
      for (i in seq_along(pick)) { j <- j + 1; g <- d[byf[[pick[i]]], ]; g$fact <- paste0(g$fact, "#", j); g$subject <- paste0(g$subject, "#", j); parts[[j]] <- g }
    }
    db <- do.call(rbind, parts)
    db <- do.call(rbind, lapply(seq_along(frs), function(k) { g <- db[db$template_id == frs[k], ]; g$template_id <- k - 1; g$frame <- k - 1; g }))
    keep <- c("relation", "template_id", "frame", "carrier", "y", "fact", "subject", COV)
    db <- p2_prep(db[, keep])
    tryCatch(stat(lmer(p2_formula("y", COV, subj), data = db, REML = TRUE, control = lmerControl(calc.derivs = FALSE))),
             error = function(e) rep(NA, 5))
  }
  do.call(rbind, mclapply(seq_len(nb), one, mc.cores = cores))
}
