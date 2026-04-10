---
id: P016
title: "Nowcasting Norwegian Household Consumption with Debit Card Transaction Data"
authors: "Aastveit, Fastbø, Granziera, Paulsen, Torstensen"
year: 2024
source: "Journal of Applied Econometrics, 39(7), 1220-1244"
doi: "10.1002/jae.3076"
importance: High
categories:
  - alternative-data
  - household-consumption
verified: true
added: 2026-04-10
---

## Summary
ノルウェー全国のデビットカード取引データを用いて、四半期家計消費をナウキャストする手法を開発。MIDAS回帰により標準的なベンチマークモデルを上回る予測精度を実現。

## Methodology
- QMIDAS（Quantile Mixed-Data Sampling）回帰
- データ: ノルウェー国内の全デビットカード物理端末取引（週次）
- 評価期間: 2011Q4–2019Q4、COVID-19期間の追加検証

## Key Findings
- デビットカード取引データは改定がなく、週次で遅延なく利用可能
- MIDAS回帰でポイント予測・密度予測ともに標準ベンチマークを改善
- COVID-19期間（2020Q1）の不確実性が高い局面で特に有効

## Relevance to This Thesis
- **オルタナティブデータ活用の手本**: 決済データ→消費ナウキャストの方法論的先行研究
- MIDAS回帰の枠組みはPhase 2のシミュレーションにリアルタイムデータを投入する際の参考
- データの性質（改定なし・高頻度・地理情報付き）は日本のJCB消費NOW等に類似

## Limitations / Notes
- ノルウェーはキャッシュレス比率が非常に高い。日本は現金比率が高く代表性に注意
