---
id: P080
title: "A Practical Guide to Shift-Share Instruments"
authors: "Borusyak, Hull, Jaravel"
year: 2025
source: "Journal of Economic Perspectives, 39(1), 181-204（旧 NBER WP 33236。確定掲載を DEC-024 で verify・2026-07-07）"
doi: "10.1257/jep.20231370"
importance: High
categories:
  - identification-strategy
verified: true
added: 2026-05-31
updated: 2026-07-07
---

## Summary
Shift-share IV の**実務ガイド**（P004 の 2022 ReStud 理論論文とは別物）。識別には「多数の外生ショック（exogenous shifts）」と「外生シェア（exogenous shares）」の2経路があると整理し、どちらに依拠するかをチェックリスト形式で判断させる。実証設定の例とともに、推論・診断・実装の実務的勘所を示す。

## Methodology
- 識別の2経路（many exogenous shifts ↔ exogenous shares）の論理と前提を対比し、簡潔なチェックリスト化
- 各経路で必要な検証（ショック数・シェア外生性・Rotemberg 診断・exposure-robust SE）を実務手順として提示
- 複数の実証設定（ADH 中国ショック等）でポイントを例示
- 付随コード: `borusyak/shift_share_jep`（**Stata 100%**）。「交互作用つき shift-share IV の exposure-robust SE の計算」を実演

## Key Findings
- shift-share IV の妥当性は「ショック外生（多数の準ランダムショック）」か「シェア外生」のどちらの物語に立つかで前提が変わる。**両立はしない**ので設計時に選ぶ
- 「多数の外生ショック」経路は**有効ショック数が十分多い**ことを要する（少数ショックでは漸近近似が崩れ、推論が信頼できない）
- exposure-robust SE は shock-level の等価回帰で取得でき、Stata で実装可能（交互作用にも対応）

## Relevance to This Thesis
- **A-4 の設計判断を直接ガイドする（support-vs-undermine の判定基準）**: 本研究 A-4 は 5 群別 shifter で「多数ショック経路」に乗ろうとするが、本ガイドの基準では「ショック5本・相関 0.66〜0.93」は many-shock 経路の前提（十分多い独立ショック）を**満たさない**。したがって本研究は (a) シェア外生経路（地域カテゴリシェアの外生性）に立論を切り替えるか、(b) 探索的に留め exposure-robust SE で正直に推論するか、を本ガイドのチェックリストで明示的に選べる。
- **実装の決定版出典（Q3）**: exposure-robust SE の公式実装が **Stata**（このリポジトリ + `ssaggregate`）であることを確定。Python 成熟版なしの結論を補強。卒論で BHJ 流 SE を使うなら Stata 併用が最短、Python 単独なら shock-level 等価回帰を手実装する必要があると判断できる。
- **P004 との分担**: P004（ReStud 2022）= 理論・漸近の証明。P080（JEP 2024）= 実務チェックリスト・コード・診断。A-4 の「どの識別経路に立つか」「SE をどう取るか」の実務判断は P080 を一次参照にする。

## Limitations / Notes
- 付随コードは **Stata のみ**。R は別途 `kolesarm/ShiftShareSE`（AKM, P006 系）、`zhangxiang0822/ShiftShareSEStata`（Stata 版 AKM）。**Python の公式/成熟実装は無し**（Borusyak が beta 版を request ベースで配布する旨をリサーチページに記載）。
- ガイドであり新規定理はない。few-shock 設定そのものの新推論手法は P077（Moreno-Louzada et al. 2025）や AKM(P006) を参照。
- 「ショックが十分多い」の具体的閾値は文脈依存。本研究の 5 群は明らかに少数側で、本ガイドの many-shock 推奨レンジ外という限界明記の根拠になる。
