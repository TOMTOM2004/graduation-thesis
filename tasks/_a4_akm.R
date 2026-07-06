# Step4: AKM/BHJ exposure-robust SE（実験・非保持）
# 入力 data/processed/price-indices/_akm_cross.csv は tasks/_a4_akm_prep.py で再生成可能（DEC-019）。
# ShiftShareSE インストール: install.packages("ShiftShareSE", lib="~/.Rlib")
#   CRAN に無い場合: remotes::install_github("kolesarm/ShiftShareSE", lib="~/.Rlib")
.libPaths("~/.Rlib")
library(ShiftShareSE)
d <- read.csv("data/processed/price-indices/_akm_cross.csv")
groups <- c("energy","metals","chemicals","food","wood")
W <- as.matrix(d[, paste0("ic_", groups)])
shocks <- as.numeric(d[1, paste0("dp_", groups)])   # ΔP_g（全行共通）
X <- as.numeric(W %*% shocks)                        # 群別 shift-share regressor
Y <- d$y

cat("=== 2022 クロスセクション shift-share: naive vs AKM exposure-robust ===\n")
cat(sprintf("N=%d categories, %d group-shocks\n\n", nrow(d), length(groups)))

# naive OLS
ols <- lm(Y ~ X)
b <- coef(ols)["X"]; se_naive <- summary(ols)$coefficients["X","Std. Error"]
cat(sprintf("naive OLS : beta=%.3f  SE=%.3f  t=%.2f  p=%.4f\n", b, se_naive, b/se_naive, summary(ols)$coefficients["X","Pr(>|t|)"]))

# AKM / AKM0 exposure-robust
r <- reg_ss(Y ~ 1, X = X, W = W, data = d, method = "all")
print(r)
