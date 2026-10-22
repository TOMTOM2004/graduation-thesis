---
id: P095
title: "The AI-GPR Index: Measuring Geopolitical Risk using Artificial Intelligence"
authors: "Matteo Iacoviello, Jonathan Tong"
year: 2026
source: "Working Paper"
importance: High
categories:
  - identification-strategy
  - alternative-data
verified: true
added: 2026-07-25
---

## Summary

1960年以降の新聞記事をLLMで分類し、日次の地政学リスク、国別、事象別、
二国間の地政学リスク指数を構築する。

## Methodology

- New York Times、Washington Post、Chicago Tribuneの約460万記事
- GPT-4o-miniによる0〜1の地政学リスク強度分類
- 国を initiator / respondent / spillover に分類し、方向付き二国間指数を作成

## Key Findings

- AI-GPRは従来のキーワード型GPRと相関しつつ、誤検出を減らす。
- Russia→Ukraine 指数は2014年のクリミア併合と2022年の全面侵攻で大きく上昇する。
- 二国間GPRの上昇は二国間貿易の縮小と関連する。

## Relevance to This Thesis

- 公開月次系列が1960年以降をカバーし、既存の2005–2025年固定バスケットLPと接続できる。
- 方向付き Russia→Ukraine ニュース強度から一方向の予測革新を構築し、原油ニュースLPとの探索的比較に使える。

## Limitations / Notes

- 2026年のworking paperで、二国間指数について構造ショックとしての外生識別は行っていない。
- 米国新聞の報道量であり、日本の家計物価への因果ショックではない。
- 本研究ではデータゲートは通過するが因果ゲートは通過しないため、探索的分析に限定する。
