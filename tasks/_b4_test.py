"""B-4: 輸入含有率の競争輸入型補正の検証（実験ブランチ・非保持）。

旧: IC = μ^T (I−A)^{-1}        … A は輸入中間投入を含む総合係数 → 二重計上で IC>1
新: IC = μ^T (I−(I−M̂)A)^{-1}  … 国内投入係数 A^d=(I−M̂)A の国内レオンチェフ → [0,1]
"""
import numpy as np
import pandas as pd
from src.utils.io_utils import load_io_table, compute_input_coefficients, compute_leontief_inverse

io = load_io_table()
A = compute_input_coefficients(io)
x = io["output"]
imp = io["imports"].abs()
mu = (imp / (x + imp).replace(0, np.inf)).fillna(0.0)  # 輸入浸透率
n = A.shape[0]

# 旧
L_old = compute_leontief_inverse(A)
ic_old = pd.Series(mu.values @ L_old.values, index=A.index)

# 新（競争輸入型）: A^d = (I−M̂)A, L^d=(I−A^d)^{-1}, IC = μ^T L^d
M_hat = np.diag(mu.values)
A_d = (np.eye(n) - M_hat) @ A.values
L_d = np.linalg.inv(np.eye(n) - A_d)
ic_new = pd.Series(mu.values @ L_d, index=A.index)

print("=== 有界性チェック ===")
print(f"旧 IC: max={ic_old.max():.3f}  min={ic_old.min():.3f}  n(>1)={(ic_old>1).sum()}  n(>1.001)={(ic_old>1.001).sum()}")
print(f"新 IC: max={ic_new.max():.3f}  min={ic_new.min():.3f}  n(>1)={(ic_new>1).sum()}  n(>1.001)={(ic_new>1.001).sum()}")
print()
print("=== 旧で IC>1 だったセクター（61,231,271）の新旧 ===")
for s in ["061", "231", "271"]:
    if s in ic_old.index:
        print(f"  sector {s}: 旧={ic_old[s]:.3f} → 新={ic_new[s]:.3f}")
print()
print("=== 主要エネルギー/食料セクター（参考）の新旧 ===")
for s in ["061", "211", "111", "112"]:
    if s in ic_old.index:
        print(f"  sector {s}: 旧={ic_old[s]:.3f} → 新={ic_new[s]:.3f}  (μ={mu[s]:.3f})")
print()
print(f"=== 全体: 新IC平均={ic_new.mean():.3f} 旧={ic_old.mean():.3f}  相関={ic_new.corr(ic_old):.3f} ===")
print("（新が[0,1]に収まり、旧>1が解消されていれば B-4 修正は妥当）")
