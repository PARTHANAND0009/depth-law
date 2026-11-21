source("/home/user/depth-law/scratch/replicate/fit_lib.R")
res <- list()
for (m in c("pythia-1.4b","pythia-2.8b","OLMo-2-1124-7B")) {
  d <- load_tab(m)
  t0 <- Sys.time(); f <- fit_h1(d); t1 <- Sys.time()
  dr <- dr2_fn(d); t2 <- Sys.time(); orv <- or_fn(d); t3 <- Sys.time()
  b <- ranef(f)$relation; blup <- data.frame(relation = rownames(b), blup = b[,1])
  write.csv(blup, file.path(D, paste0("blup_", m, ".csv")), row.names = FALSE)
  res[[m]] <- list(n_rows = nrow(d), icc_rel = icc(f), vc = as.list(vcs(f)), singular = isSingular(f),
                   r2m_without = dr[["r2m0"]], r2m_with = dr[["r2m1"]], dr2 = dr[["dr2"]], or = orv,
                   secs = c(as.numeric(t1-t0), as.numeric(t2-t1), as.numeric(t3-t2)))
}
write(toJSON(res, auto_unbox = TRUE, digits = NA, pretty = TRUE), file.path(D, "point.json"))
cat(toJSON(res, auto_unbox = TRUE, digits = 8, pretty = TRUE))
