---
id: P073
title: "Bridging between Economy-Wide Activity and Household-Level Consumption Data: Matrices for European Countries"
authors: "Cabrera, Miriam; Luger, Thomas; Roettger, Julia"
year: 2020
source: "Data in Brief, 29, 105395"
doi: "10.1016/j.dib.2020.105395"
importance: Medium
categories:
  - household-consumption
  - simulation-model
verified: true
added: 2026-04-11
---

## Summary
家計消費の目的別分類（COICOP、35カテゴリ）と産業活動別分類（CPA、63カテゴリ）の間のブリッジ・マトリクスを、EU30カ国について構築。マトリクスバランシング手法により Eurostat データから整合的な変換表を推定。

## Methodology
- Eurostat の家計最終消費支出データ（2015年、COICOP×CPA）を入力
- マトリクスバランシング技法（RAS/GRAS系）で整合的なブリッジ・マトリクスを推定
- 30カ国（EU全加盟国＋英国・ノルウェー・セルビア）をカバー
- データセット公開（再現可能）

## Key Findings
- COICOP-CPA 間の対応は多対多（1つの消費目的が複数産業の財に対応し、逆も同様）
- 国ごとにブリッジ構造が異なる（消費パターン・産業構造の反映）
- 既存の手動マッピングよりも統計的に整合的な変換を提供

## Relevance to This Thesis
- 副問2（所得階層別の消費反応）: IO表（産業分類）と家計調査（消費分類）を接合する際のブリッジ・マトリクス構築手法は、本研究の日本版構築に直接参照可能
- P074 Cazcarro et al. (2022) と対をなすデータセット（同論文がこのデータを活用した分析手法を提示）
- 日本では総務省「産業連関表」（産業分類）と「家計調査」（用途分類）の接合が課題であり、同様のブリッジ手法が必要

## Limitations / Notes
- EU諸国のみ対象（日本のCOICOP対応は別途構築が必要）
- 2015年の単一時点データ（時系列変動は未考慮）
- Data in Brief 掲載のデータ記述論文であり、分析論文ではない
