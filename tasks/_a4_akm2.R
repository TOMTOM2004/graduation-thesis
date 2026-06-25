.libPaths("~/.Rlib"); suppressMessages(library(ShiftShareSE))
d <- read.csv("data/processed/price-indices/_akm_cross.csv")
for (gs in list(c("energy","food"), c("energy","metals","chemicals","food","wood"))) {
  W <- as.matrix(d[, paste0("ic_", gs)])
  shocks <- as.numeric(d[1, paste0("dp_", gs)])
  X <- as.numeric(W %*% shocks)
  r <- reg_ss(d$y ~ 1, X = X, W = W, data = d, method = "all")
  cat(sprintf("groups=%-38s beta=%.3f  AKM_p=%.4f  AKM0_p=%.4f\n",
      paste(gs,collapse="+"), as.numeric(r$beta), r$p["AKM"], r$p["AKM0"]))
}
