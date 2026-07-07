---
id: P087
title: "Making Sense of Sensitivity: Extending Omitted Variable Bias"
authors: "Cinelli, Hazlett"
year: 2020
source: "Journal of the Royal Statistical Society Series B, 82(1), 39-67"
doi: "10.1111/rssb.12348"
importance: Medium
categories:
  - identification-strategy
  - sensitivity-analysis
verified: true
added: 2026-07-07
---

## Summary
線形回帰の omitted variable bias を partial R² でパラメタ化した感度分析枠組。未観測交絡が「処置・アウトカム双方とどれだけ強く相関すれば結論（点推定ゼロ化／有意性喪失）が覆るか」を robustness value (RV) として1つの数値で報告でき、観測共変量を benchmark に交絡強度の上限を議論できる。

## Methodology
- OVB を partial R²（処置との R²_D・アウトカムとの R²_Y）の2次元で完全に特徴づけ
- Robustness value RV_q: β を割合 q だけ縮小させるのに必要な最小の交絡強度（両 R² が等しい場合）
- 観測共変量の k_d・k_y 倍という benchmark で bias 上限を計算（bias contour plot）
- 実装: R `sensemakr`（CRAN）/ Python `PySensemakr` / Stata。within 変換後の OLS に適用可（FE は残差変動で処理・自由度調整）

## Key Findings
- E-value（リスク比・二値曝露）や Rosenbaum bounds（マッチング二値処置）と異なり、**連続処置の線形回帰係数にそのまま適用できる**唯一の標準ツール
- RV は「交絡がこれ未満なら結論不変」を単一数値で伝える。benchmark により「観測済みの X の◯倍強い交絡が必要」という具体的言明が可能

## Relevance to This Thesis
- **本設計（連続処置 IC×P・two-way FE・n=156）に適合する唯一の感度分析枠**（DEC-024 で E-value / Rosenbaum bounds を不適合と判定・比較検討済み）
- 使うなら: β=0.373 の点推定ゼロ化 RV を主報告とし、goods ダミー（財/サービス交絡＝DEC-022）を benchmark covariate に「観測済み財区分の何倍の交絡で覆るか」を定量化
- caveat: p=0.089 ゆえ有意性喪失の RV はほぼゼロに近く出る。有意性でなく点推定ベースの framing が必須
- **採否未定・未実装**（優先度低）。実装するなら要承認・`PySensemakr` で within 変換後に適用

## Limitations / Notes
- 線形・単一交絡（または線形結合）の枠。非線形交絡経路は上限議論の外
- ハンドオフメモの E-value / Rosenbaum bounds 案は本設計に不適合として不採用（DEC-024）
