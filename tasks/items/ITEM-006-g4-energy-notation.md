---
id: ITEM-006
title: G-4 エネルギー価格上昇率の表記ゆれ統一（+203% vs +213〜286%）
status: todo
priority: P3
source: self
context: personal
created: 2026-07-07
updated: 2026-07-07
links: [docs/design-review.md, docs/research-design.md]
---

## 背景

+203%（年平均集計・再現可）vs +213〜286%（品目別ピーク?・リポジトリのデータで再現不能、286 は集計月次ピーク 268 超）の表記ゆれが docs/slides に残る。design-review G-4。

## 現状 / next action

- 品目別ピークの一次ソースを示すか、**+203%（年平均）/ +268%（月次ピーク）に統一**するかを決めて全ファイル一括修正
- 論文には再現可能な値のみ書く（thesis-writing §1.4）ため、[[ITEM-002]] の結果章執筆前に決着させる

## Decision log

