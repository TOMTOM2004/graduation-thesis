---
id: ITEM-001
title: 識別限界の鋭利化 — 追加ロバストネス（goods×年FE / exposure-robust推論 / sensemakr任意）
status: todo
priority: P1
source: self
context: personal
created: 2026-07-07
updated: 2026-07-07
links: [docs/decision-log.md, docs/research-design.md, paper/03a-identification-strategy.md]
---

## 背景

DEC-024 で本設計を GPSS share外生設計（exposure research design）に正式位置づけた際、先行研究が処方する「正しい計算」を当てるとメイン仕様の p=0.089 はむしろ拡大する方向であることが判明。これを appendix 用の追加ロバストネスとして実装し、識別限界（貢献③）を自分の手で鋭利化する。**β を救う試みではない**——事前登録した読みでどちらに転んでも論文に書ける構造にする。ユーザー承認済みプラン（2026-07-07・実装は後日）。関連: [[ITEM-002]]（論文執筆・03a 骨子の段落4-5 に結果を接続）。

## 現状 / next action

**プラン承認済み・実装未着手**。着手時は worktree でコード実装 → `/review-code` light → main へ --no-ff。結果は DEC-025 起票。

### 共通の枠（事前登録）
- メイン仕様 (iii)（β=0.373, p=0.089・暦年DEC-023）は変更しない。新結果は全て appendix・Tier 2。headline・golden 値に影響なし（`check_golden` PASS 維持）
- 各項目の「予想される結果と論文上の読み」を実施前に DEC-025 へ固定

### 項目1: goods×年 FE 仕様（先行・軽量・依存なし）
- GPSS Test 1（シェアの相関物コントロール）の回帰版＝DEC-022 相関分解の格上げ
- 仕様 (vi): ΔCPI_{c,t} = β(IC_c×P_t) + γ_{g(c),t} + δ_c + ε（年FE→財/サービス区分×年FE）
- 補助: within-goods / within-services サブサンプル β
- 流用: `goods_services_contrast.py` の41カテゴリ分類（官公表突合済）・`cost_push_panel.py` のパネル構築
- 事前登録の読み: (a) β 減衰・非有意化（本命予想。within-goods 相関 −0.18〜+0.10 から示唆）→交絡吸収後は cost-push シグナル識別不能の回帰的確認 (b) β 残存→within-goods でも整合シグナル＝強材料。どちらも informative
- 出力: `cost_push_panel_results.csv` に (vi) 行追加

### 項目2: exposure-robust 推論（feasibility ゲート付き）
- **Phase 2-0（ゲート・30分）**: P077（Moreno-Louzada et al. 2025, arXiv:2512.10076）の replication code 有無を確認。無く自力実装が重ければ打ち切り＝「P077 型 SE が必要だが実装非公開・限界として明記」で確定（P077 メモ選択肢 (c)・正当化済み）
- Phase 2-1（code あれば）: メイン仕様 (iii) に適用し p=0.089 との乖離を計測
- フォールバック（軽量・選択実施）: ① AKM `reg_ss`（R導入済み）を 2021-2024 各年クロスセクションへ拡張（現状2022のみ） ② 時点方向 Rotemberg weights α_t（GPSS §3.3・純Python可）＝どの年が β を駆動するかの透明化。**②のみは軽いので打ち切り時も実施推奨**
- 事前登録の読み: p は 0.089 以上に拡大する公算大（AKM 2022 p≈0.15・P077 応用例 SE×2 と整合）→ cluster p の楽観性を自設計で定量化

### 項目3（任意・優先度最低）: Cinelli-Hazlett robustness value（sensemakr）
- P087。within 変換後 OLS に `PySensemakr` 適用。goods ダミーを benchmark に「財/サービス交絡の何倍の交絡で β=0.373 がゼロ化するか」を RV で報告
- caveat: p=0.089 ゆえ有意性喪失 RV はほぼゼロ＝点推定ゼロ化 RV を主報告とする framing 必須
- 採否は執筆時判断（DEC-024）。項目1-2 の結果を見てから決めてよい

### Done when
- 仕様 (vi) の β/p が CSV 再現つきで確定・DEC-025 起票・appendix 表ドラフト（数値は全て repo 再現値）
- 項目2 は「実装して数値確定」or「feasibility 打ち切り記録＋α_t のみ実施」で決着

### スコープ外
- メイン仕様の変更・headline 差し替え、P077 型 SE のフルスクラッチ自力実装、ハンドオフ§8 ③④（→ [[ITEM-003]]）

## Decision log

- 2026-07-07: プラン承認（ユーザー）。実装は後日。感度分析は Cinelli-Hazlett 軸・優先度最下位（E-value/Rosenbaum は不適合＝DEC-024 で確定）
