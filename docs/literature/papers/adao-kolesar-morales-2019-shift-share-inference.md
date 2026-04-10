---
id: P006
title: "Shift-Share Designs: Theory and Inference"
authors: "Adão, Kolesár, Morales"
year: 2019
source: "Quarterly Journal of Economics, 134(4), 1949-2010"
doi: "10.1093/qje/qjz025"
importance: High
categories:
  - identification-strategy
verified: true
added: 2026-04-10
---

## Summary
Shift-share回帰デザインにおける推論問題を理論的に分析。通常の標準誤差では過剰棄却が起きることを示し、シェア構造に由来する残差相関に対処する推論手法を提案。

## Methodology
- Shift-share推定量の漸近理論
- プラセボテストによる通常の標準誤差の過剰棄却の実証
- 残差の地域間相関に頑健な推論手法の提案

## Key Findings
- 通常の標準誤差では名目5%水準で最大55%棄却（重大な過剰棄却）
- 類似したセクターシェアを持つ地域間で残差が相関するため
- 提案手法により信頼区間が大幅に拡大するケースがある

## Relevance to This Thesis
- **推論の正確性**: 本研究でshift-share IVを使う場合、標準誤差の計算にこの論文の手法を適用すべき
- P004, P005と合わせてshift-share IVの実装に必要な三部作

## Limitations / Notes
- 実装が技術的にやや複雑。Stataパッケージが存在するが、Pythonでの実装は要確認
