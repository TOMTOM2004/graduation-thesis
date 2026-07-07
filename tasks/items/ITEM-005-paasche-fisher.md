---
id: ITEM-005
title: 交易損失の Paasche/Fisher 化 — 固定数量→実数量ベースへの精緻化
status: todo
priority: P3
source: self
context: personal
created: 2026-07-07
updated: 2026-07-07
links: [docs/design-review.md]
---

## 背景

`trade_loss.py` は固定数量（Laspeyres・2020輸入額固定）。実数量ベース（Paasche/Fisher）へ精緻化すれば価格効果の推計が改善する。design-review 由来の残タスク。

## 現状 / next action

- 前提＝**財務省貿易統計の数量データ取得**（現状 raw は衣類のみ）。`src/data/fetch_trade_stats.py` を拡張し5グループの品目別 数量×価額を取得 → 価格効果を q_t ベースで再計算
- 注意: headline（中心35兆系）が動く可能性がある変更＝実施するなら論文数値の確定**前**に判断。実施しない場合は「Laspeyres 固定数量」を限界として方法章に明記（[[ITEM-002]]）で足りる

## Decision log

