---
id: ITEM-002
title: 論文執筆 — 章ドラフト進行（先行研究・方法論・結果・考察・結論）
status: in_progress
priority: P1
source: self
context: personal
created: 2026-07-07
updated: 2026-07-07
links: [paper/outline.md, docs/decision-log.md, .claude/skills/thesis-writing/SKILL.md]
---

## 背景

Phase 1〜3（分析）完了・実証3本柱（交易損失35兆=会計／Q1-Q5 逆進性=恒等式／識別限界=方法論）を論文本体へ統合する。paper/ 作業は必ず thesis-writing スキル経由（数値規律・クレーム階層・撤回済み主張の混入防止）。⚠数値は必ず暦年再生成値（DEC-023）: 交易損失 中心~35兆/2025年24.8兆・Q1-Q5 +2.01pp(2022)/+3.36pp(2025)・β=0.373(p=0.089)・Shapiro 0.41→0.70→0.83・Koyck RMSE 9.24pp。

## 現状 / next action

- 章状態は `paper/outline.md` が正: 01-introduction ドラフト済（DEC-015 準拠）・04a 国際ベンチマーク小節ドラフト済・**03a 識別戦略節は骨子のみ（DEC-024 準拠・ユーザー合意待ち）**・他は未
- **Next**: ① `paper/03a-identification-strategy.md` 骨子6段落のユーザー合意 → 本文ドラフト ② 先行研究章に shift-share 2経路（GPSS/BHJ/AKM）の導入を書く（03a と分担・重複執筆しない） ③ 以降 outline の章割りで進行
- 執筆前準備（章に着手する際に消化）:
  - [ ] 非線形モデルの扱いの明確化（research-design に「線形・非線形を比較」とあるが結果は線形のみ→未実施理由を DEC 追記）
  - [ ] Koyck δ=0.55 選定根拠の文書化（DEC 起票。C-3: 独立grid最小は0.60・[0.5,0.7]平坦＝「推定」でなく calibration・半減期≈10.4ヶ月）
  - [ ] 先行研究との数値比較表（**β=0.373（暦年DEC-023）** vs Yagi et al.=品目別転嫁率の異質性 / Amiti et al.=自社コスト弾力性≈0.6、交易損失 中心35兆（上限40.7）vs **内閣府SNA 2022年度 −16.4兆円**〔概念差明記・齊藤2022のGNI比4.6%はAI混入としてDEC-019で排除済み・使用禁止〕。第3回デッキ s10 の照合済み内容を流用可）
  - [ ] 政策シナリオ選定の透明性（なぜエネ・食料補助で賃金補助・産業政策でないか＝スコープ限定を論文内に明記）
  - [ ] GPSS 引用ページの AER 刊行版照合（現状 NBER WP 24408 版ページ＝03a 骨子の注意書き）
- 関連: [[ITEM-001]]（appendix ロバストネス・03a 段落4-5 に接続）

## Decision log

- 2026-07-07: 識別節は GPSS share外生枠（DEC-024）で書く。「識別に類例がない」は使用禁止
