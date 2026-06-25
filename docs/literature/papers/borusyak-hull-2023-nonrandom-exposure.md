---
id: P084
title: "Nonrandom Exposure to Exogenous Shocks"
authors: "Borusyak, Kirill; Hull, Peter"
year: 2023
source: "Econometrica, Vol. 91, No. 6, pp. 2155-2185 (NBER WP 27845)"
doi: "10.3982/ECTA19367"
importance: High
categories:
  - identification-strategy
verified: true
added: 2026-06-01
---

## Summary
既知の式（formula）に従って複数の変動源を組み合わせた処置・操作変数（shift-share/Bartik、simulated instrument 等）の因果効果推定法を提示。各単位の「エクスポージャー」が非ランダムでも、外生的なショックの実現値を所与とした**反実仮想分布**を用いて操作変数を**recenter（再中心化）**すれば、エクスポージャーの非ランダム性に由来する omitted-variable bias を除去できると示す。**recentered instrument は product characteristics（＝シェア／エクスポージャーの決定要因）の外生性を必要としない**点が核心。

## Methodology
- formula instrument（観測ショック × 既知エクスポージャー）の期待値を、ショックの反実仮想分布（permutation/再抽選）で計算し、実現操作変数からこの期待値を差し引いて recenter。
- recentering により「非ランダムなエクスポージャーが交絡を生む」経路を遮断。残る識別は**ショックの（条件付き）外生性**に依拠。
- 設計ベース推論（design-based inference）を整備。replication package 公開（Zenodo 8286785）。

## Key Findings
- エクスポージャー（シェア）が内生・非ランダムでも、ショック外生性さえあれば recentered IV で一致推定が可能。
- shift-share/Bartik の identification 議論を「シェア外生性 vs ショック外生性」の二経路で整理する文献（GPSS 2020 / BHJ 2022）に対し、**シェア非ランダム性を recentering で吸収する第三の道**を提供。

## Relevance to This Thesis
- **Q2 の「recentered instrument」要素への直接の典拠であり、share-exogeneity 軸を担う**: 既存の P004(BHJ shift-share)・P077(価格エクスポージャー設計の contamination) は主に**ショック外生性**側を扱う。本論文は**シェア／エクスポージャーの非ランダム性**側を扱う点で相補的で、卒論の「群別エクスポージャー（5グループ消費シェア）が所得・地域特性と相関して内生的かもしれない」という識別上の懸念に対する処方を与える。
- **採用可能性**: 卒論の β_g 推定でエクスポージャー（消費バスケットシェア）が所得階層特性と相関する場合、ショックの反実仮想分布で recenter すれば share 内生性を緩和できる。ただし反実仮想分布の設定（何を「ショックの再抽選」とみなすか）が単一マクロ事象では非自明 → P077 の few-shock 問題と合わせ、「日本の2022-24 単一イベントでは recentering の反実仮想設定自体が困難」という限界明記の根拠にもなる（＝清浄識別困難という新規貢献の補強）。
- **本研究との差**: 本論文は手法論（design-based）。日本の輸入インフレ applied 適用は含まない。卒論は share-exogeneity 懸念への「処方は存在するが単一イベントでは適用条件を満たしにくい」文脈で引用。

## Limitations / Notes
- recentering には「ショックの反実仮想分布」の明示的指定が必要。単一マクロショック（2022 ウクライナ・原油）では再抽選の自然な定義が乏しく適用が難しい。
- shift-share 標準誤差の exposure-robust 実装（AKM/BHJ）とは別系統。R/Stata 実装は P077/P080 の整理を参照（Python 成熟版なし）。
