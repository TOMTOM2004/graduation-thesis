---
id: P079
title: "The consumption side of trade shocks: Inequality dynamics and luxury imports"
authors: "Cícero, Heras-Recuero"
year: 2025
source: "Journal of Development Economics (online Oct 2025)"
doi: ""
importance: Medium
categories:
  - identification-strategy
  - regional-heterogeneity
  - household-consumption
verified: true
added: 2026-05-31
---

## Summary
中国の WTO 加盟（2001）を外生ショックとし、ブラジル地域の**事前輸出構造に基づく shift-share 操作変数**で「中国需要ブームへの地域エクスポージャー」を構築。エクスポージャーの高い地域ほど一人当たり所得が伸び、地域内格差が拡大し、その結果として**輸入（特に高所得層が消費する奢侈財・消費財）**が増えるという、貿易ショックの「消費・輸入側」を実証。

## Methodology
- **Shift-share IV**: 中国の輸出需要 × ブラジル地域の事前（pre-shock）輸出構造シェア → 地域別エクスポージャー
- 単位: ブラジルの地域（regions / microregions）
- 財を必需財/奢侈財に分類（ブラジル家計データ + 米国高所得層の支出パターンに基づく補助的分類）
- 結果変数: 地域の一人当たり所得、域内格差、輸入額（財タイプ別）

## Key Findings
- エクスポージャー高地域ほど一人当たり所得が速く成長し、**域内格差が拡大**
- エクスポージャー高地域は輸入を多く増やす（25→75 パーセンタイルの移動で総輸入が地域輸入成長の約 15%、消費財だけなら約 20% 増）
- 増加は製造財・中高技術財（奢侈財・消費財）に集中 = 分布上位の所得増による消費需要の現れ

## Relevance to This Thesis
- **shift-share/exposure × 分配 × 輸入の applied 先例（support 側、設計テンプレート）**: 「外生的国際ショック × 事前構造シェア」で地域エクスポージャーを作り、所得・格差・輸入を結果にする流れは、本研究の輸入価格ショック × 地域別カテゴリシェアの設計と構造的に同型。ADH(P013) の労働市場版に対し、本論文は**消費・輸入・格差**を結果にした版で、本研究のテーマにより近い。
- **格差の方向の対比**: 本論文は「貿易ショック → 上位所得増 → 奢侈輸入増 → 格差拡大」。本研究は「輸入**価格**ショック → 低所得層の生計費上昇 → 格差拡大（逆進）」。同じ格差拡大でも経路が逆（所得側 vs 価格側）。本研究の「価格・必需財経路」の独自性を際立たせる対照例として使える。
- **本研究 A-4（群別識別）への効き方**: 本論文は単一の集計エクスポージャー（China demand）で many-region の横断変動を使う典型的 shift-share。本研究は逆に「ショック側を 5 群に増やすが相関が高い」設定で、横断（地域）より時系列（年次）変動に依存する。つまり本論文は「many-shock/many-region で shift-share が効く理想形」を示し、本研究がそこから**外れている**（few correlated shocks、地域変動が弱い）ことの対照に使える。

## Limitations / Notes
- 著者名は VoxDev コラム経由で確認（Vinicius C. Cícero, Laura Heras-Recuero）。ScienceDirect 本体は paywall のため詳細手法は二次情報。粒度（region か microregion か）は本文で要確認。
- ブラジル・China shock の文脈。日本・輸入価格ショックへの直接外挿は不可だが、設計ロジックは転用可能。
- 価格ショックではなく**需要/数量ショック**（China demand boom）が主。本研究の価格転嫁とは因果経路が異なる。
