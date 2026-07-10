# Handoff — graduation-thesis 卒業論文（案B・論文執筆フェーズ）
_Last updated: 2026-07-07 20:44 / session: 識別戦略 DEC-024（GPSS share外生位置づけ）→ロバストネスプラン ITEM-001 化→ITEM 方式移行→handoff_

## 📇 案件 index（自動生成・SSOT = `tasks/items/*.md` / 再生成 = `item_indexer.py`・手書き禁止）
<!-- item_indexer.py が tasks/items/INDEX.md を生成。下表はその転記
     (鮮度は todo-status-manager が着手/完了時に同期)。原本 = tasks/items/INDEX.md -->

| ID | 概要 | priority | status | updated |
|---|---|---|---|---|
| ITEM-002 | 論文執筆 — 章ドラフト進行（先行研究・方法論・結果・考察・結論） | P1 | in_progress | 2026-07-07 |
| ITEM-021 | 柱②曝露(スライド7)の多年度化(2022→2025)＋五分位DiDの証明可能性検討（ゼミ指摘） | P2 | todo | 2026-07-10 |
| ITEM-001 | 識別限界の鋭利化 — 追加ロバストネス（goods×年FE / exposure-robust推論 / sensemakr任意） | P1 | todo | 2026-07-07 |
| ITEM-004 | 再現性の残穴 — shapiro e-Statキャッシュ化・GDP vintage確定・stale processed削除判断 | P2 | todo | 2026-07-07 |
| ITEM-003 | ハンドオフ§8 残り — 現代 event study/DID（小麦補強）③・財政乗数の状態依存④ | P3 | todo | 2026-07-07 |
| ITEM-005 | 交易損失の Paasche/Fisher 化 — 固定数量→実数量ベースへの精緻化 | P3 | todo | 2026-07-07 |
| ITEM-006 | G-4 エネルギー価格上昇率の表記ゆれ統一（+203% vs +213〜286%） | P3 | todo | 2026-07-07 |
| ITEM-007 | スライド運用ルールの策定（命名規則・格納構成・凍結方針の規約化） | P3 | todo | 2026-07-07 |

## 🎯 Next actions（優先順・直近の作業ポインタ。詳細は各 ITEM ファイル）
- **ITEM-002**: `paper/03a-identification-strategy.md` 骨子6段落（DEC-024 準拠）のユーザー合意 → 合意後に本文ドラフト＋先行研究章の shift-share 2経路導入。⚠数値は暦年（DEC-023）・thesis-writing スキル必須
- **ITEM-001**: プラン承認済み・実装は後日（ユーザー指示 2026-07-07）。着手宣言があってから
- 受動待ち（外部条件）: なし

## 📥 Inbox（未triage）
- claude-brain: 情報の引き出し方の調査とアップデート＋RAG先行研究調査（Slack #todo より _2026-06-23_）→ **本 repo でなく claude-brain 側の案件**。handoff 時に gh issue 化を試みたが permission 拒否（2026-07-07）＝**次回 claude-brain セッションで ITEM 化して本行を消す**（ITEM-016 retrieval gate と統合可否も判断）

## 🗂️ 運用・監視（案件でなく反復運用・トリガー型）
- slides/*.html 編集時: `check_slides.py` PostToolUse hook が自動検査（第1回デッキは発表済み凍結＝編集するとエラーが出る仕様）
- paper/*.md 編集時: thesis-writing スキル必ず経由（golden 表は暦年 DEC-023 準拠に更新済み）
- 数値を触ったら: `check_golden` PASS＋撤回済みパターン grep（スキル §2）

## 🧠 Context not in code
- 決定:
  - **実証の背骨**: Phase 1（~35兆=会計）+ Phase 2b（Q1-Q5 +2.01pp=恒等式・識別仮定に非依存）。Phase 2a は識別限界の方法論的提示（貢献③・DEC-015）、Phase 3 は定性・例示（DEC-014）
  - **識別の枠組（DEC-024）**: 本設計= GPSS share外生設計。shock外生ルートは K=1 で論理的に閉じている。goods/services 交絡=仮定違反の定義そのもの・プラセボ負相関= Test 2 失敗シグナル。「識別に類例がない」は使用禁止
  - **数値の正**: 全て暦年再生成値（DEC-023）。β=0.373(p=0.089)・Q1-Q5 +1.04/+2.01/+2.06/+2.45pp・2025=+3.36pp・交易損失 35.3/28.4/29.1/24.8兆・Koyck RMSE 9.24pp
  - βの正体: 年・費目FE二元除去後の単一スロープ=転嫁率。有意が取れない根本は「独立ショックが実質1つ」＝設定に内在・別の回帰では直らない（DEC-013）
- 参考情報: 先行研究ハンドオフ = `tasks/先行研究_識別戦略ハンドオフ_20260707.md`（①②消化済みバナーあり）

## ❌ Don't do (this task)
- [trap] EnterWorktree は origin/main 起点＝ローカル main の未 push マージを含まない → `git reset --hard main` で追随してから作業する
- [trap] budoux 再適用で中黒 ZWSP の手動挿入2件（第3回デッキ）が消える → 再挿入が必要
- [mistake] スライド・docs の数値を記憶や旧ファイルから転記しない（DEC-021 の事故原因）。必ず生成 CSV / decision-log の正準値から

## 📂 Key files
- `paper/outline.md`（章割り・状態）/ `paper/03a-identification-strategy.md`（識別節骨子・合意待ち）
- `docs/decision-log.md`（DEC-001〜024・数値と判断の正）/ `docs/research-design.md`（識別の到達点と限界）
- `.claude/skills/thesis-writing/SKILL.md`（執筆規律・golden 表）
- `src/analysis/cost_push_panel.py`（β回帰）/ `tasks/_a4_akm.R`（AKM SE）/ `docs/literature/INDEX.md`（P001〜P087）

## ❌ Out of scope
- seminar1 スライドの修正（発表済み凍結。旧 todo の「スライドレイアウト修正」計画は凍結方針と矛盾するため破棄＝2026-07-07 ITEM 移行時）
- 資本フロー・市区町村単位・サプライチェーン/地政学リスク・産業構造変化の原因分析（プロジェクトスコープ外）
- P077 型 SE のフルスクラッチ自力実装（ITEM-001 のスコープ外条項）

---

_完了ログ: `tasks/done/2026-07.md`（2026-07 セッション）・`tasks/done/2026-06.md`（2026-05-31〜06-26 分も移設済み）・`tasks/done/2026-04.md`_
