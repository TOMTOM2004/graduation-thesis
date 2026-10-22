> **Status: 中断（2026-10-06・いつか再開）** — 終了ではない。再開時は下記 Next actions から。
> ic-claims ブランチ（`codex/20260725-ic-claims`）の main マージはユーザー判断待ちのまま。

# Handoff — graduation-thesis 卒業論文（案B・論文執筆フェーズ）
_Last updated: 2026-07-27 22:55 / session: LP調査セッション handoff（main 15コミットを origin へ push・IC過小計上を lesson 化）_

## 📇 案件 index（自動生成・SSOT = `tasks/items/*.md` / 再生成 = `item_indexer.py`・手書き禁止）
<!-- item_indexer.py が tasks/items/INDEX.md を生成。下表はその転記
     (鮮度は todo-status-manager が着手/完了時に同期)。原本 = tasks/items/INDEX.md -->

| ID | 概要 | priority | status | updated |
|---|---|---|---|---|
| ITEM-022 | IC正準化・クレーム精緻化・LP統合の監査修正 | P1 | done | 2026-07-25 |
| ITEM-002 | 論文執筆 — 章ドラフト進行（先行研究・方法論・結果・考察・結論） | P1 | 中断 | 2026-07-07 |
| ITEM-021 | 柱②曝露(スライド7)の多年度化(2022→2025)＋五分位DiDの証明可能性検討（ゼミ指摘） | P2 | 中断 | 2026-07-25 |
| ITEM-001 | 識別限界の鋭利化 — 追加ロバストネス（goods×年FE / exposure-robust推論 / sensemakr任意） | P1 | todo | 2026-07-07 |
| ITEM-004 | 再現性の残穴 — shapiro e-Statキャッシュ化・GDP vintage確定・stale processed削除判断 | P2 | todo | 2026-07-07 |
| ITEM-003 | ハンドオフ§8 残り — 現代 event study/DID（小麦補強）③・財政乗数の状態依存④ | P3 | todo | 2026-07-07 |
| ITEM-005 | 交易損失の Paasche/Fisher 化 — 固定数量→実数量ベースへの精緻化 | P3 | todo | 2026-07-07 |
| ITEM-006 | G-4 エネルギー価格上昇率の表記ゆれ統一（+203% vs +213〜286%） | P3 | todo | 2026-07-07 |
| ITEM-007 | スライド運用ルールの策定（命名規則・格納構成・凍結方針の規約化） | P3 | todo | 2026-07-07 |

## 🎯 Next actions（優先順・直近の作業ポインタ。詳細は各 ITEM ファイル）
- **ITEM-002**: `paper/03a-identification-strategy.md` 骨子6段落（DEC-024 準拠）のユーザー合意 → 合意後に本文ドラフト＋先行研究章の shift-share 2経路導入。⚠数値は暦年（DEC-023）・thesis-writing スキル必須
- **ITEM-001**: プラン承認済み・実装は後日（ユーザー指示 2026-07-07）。着手宣言があってから
- **ITEM-021**: 残り1件のみ＝**論文の識別限界節に「時系列＋クロスセクション曝露の2設計での識別失敗」1段落追記**（thesis-writing スキル経由・素材= `docs/quintile-did-investigation.md`）。他は完遂: ゲート通過(2025年報○)・DiD実証(採否=記述形式で採用/係数不採用)・柱②多年度化・s8b回答スライド・チャートバグ修正・DEC-025
- 受動待ち（外部条件）: なし

## 📋 ITEM-025 第3回ゼミ発表準備 — 実行プラン（2026-10-22・Stage 3 実施済み・コミット前／残=通し練習・Q&A）
<!-- 前提: 本編18枚＋補足b1・既存ナラティブ維持。構成変更なし。編集は Sonnet、マージ・コミットはユーザー判断 -->
- [x] 発表版を `codex/20260725-ic-claims` 上のデッキ/原稿に確定（**main へマージしない**・main 側旧版 β=0.373 は使わない）。ITEM-025 の P0 欄にも決定を記録
- [x] **データ鮮度ゲート（数値編集・スライド編集の前に必須／詳細・判定表 = `tasks/items/ITEM-025-seminar3-prep.md`「データ鮮度ゲート」節）**: 発表デッキの根拠データが公開側で更新されたかを先に確定し、更新ありなら既存スクリプト再実行→正準値と比較→**第3回・第4回の HTML と対応 MD 原稿の両方**を更新、更新なしなら証跡だけ残して数値には触れない。分岐判断は全て Codex に報告（ユーザーには聞かない）
  - [x] G0 準備: 一時ディレクトリ（repo 外・ソースごとに新規の空ディレクトリ）へだけ取得。`data/raw` は読み取り専用（`fetch_*.py` は出力先が `data/raw` なので**そのまま実行しない**）。取得物の解析は `python -I`、スクリプトは別ディレクトリ。取得日時・URL・SHA-256 を記録
  - [x] G1 ソース別比較（snapshot vs 公開現行）: ①CPI 2020年基準 ②CPI 2025年基準（新） ③家計調査2025年報 年次値 ④日銀 輸入CGPI ⑤Känzig 原油供給ニュースショック ⑥AI-GPR 二国間（Russia|Ukraine） ⑦GDP分母（名目暦年） ⑧2020年産業連関表（固定）。各ソースで「出典版・期間・定義」を確認
  - [x] G2 差分分類: A=差なし／B=新期間の追加のみ（2026年の部分月など。履歴は不変）／C=既存期間の改訂値／D=基準年・分類・ウェイト等の方法論変更。**B は数値に触れない（2026年は年平均化しない）**。C・D で表示精度に効くものだけ「関連更新」。差分は期間×系列×旧値×新値で厳密に記録
  - [x] G3 判定: 関連更新なし→証跡を記録して**数値主張は据え置き（デッキ・原稿とも無編集）**。関連更新あり→ITEM-025「データ鮮度ゲート」節の手順（テスト先行の最小適応→既存スクリプト再実行→出力検査→正準値比較→両デッキ HTML＋MD 同期更新）へ。第4回 s11 の「第3回フィードバック応答」placeholder は実フィードバックまで**触らない**
- [x] s11 の「非有意性（β）：これも頑健」を更新: 正準IC β=0.633（通常p=0.0009）を明記したうえで、DEC-026 どおり「p値改善≠識別改善・財サービス交絡で因果解釈しない」「ショック数に正直な推論では識別不能」へ。s9 周辺の「独立ショックが実質1つ」「非有意」表現との整合も確認
- [x] 「独立した証拠」→「相補的な証拠」: s7c 見出し/本文（draft L558–561）、s7c 原稿（script L151）、s10 原稿（script L229「独立な証拠」）、s6 note「識別問題から独立して頑健」（意味を確認し必要なら「回帰の識別仮定に依存しない」へ）。DEC-026 動詞規律に合わせる
- [x] 「消費への影響」系の表現を固定バスケット生活費負担へ: 表紙/`<title>` の「家計消費への異質な影響」、s9 の「GDP集計の消費減少」（draft L654・script L225）、結論 s14 の「実質消費」を DEC-026 の RQ（生活費負担の逆進的押し上げ）に整合。発表タイトル変更は **ユーザー承認後**
- [x] 日付: 表紙（draft L320）・原稿ヘッダ（script L4）の「2026年秋（日程調整中）」→「2026-10-23」。ファイル名 `20261101-*` は変更しない（参照リンク波及）
- [x] （**データ鮮度ゲート G3 通過後に実施**。以降の数値系 2 項目も同様）b1 の 12.9 vs 13.0 の不一致を解消: draft L822（12.9・バー87.1%）と script L374（13.0）。**先に生成CSVで食料30%補填の gap 削減率の正値を確認**してから両者をそろえる（どちらが正かは未確定）
- [x] 数値の最終照合（DEC-026/027 と生成物）: 35.3/28.4/29.1/24.8兆、+2.01/+2.06/+2.45/+3.36pp、β=0.633、LP global p=0.035、Koyck RMSE 10.40pp、b1 の 1.56pp/44.7%/57.8%。撤回済み主張（β=0.373・「初」「空白を埋める」）を grep
- [x] 静的検査: `check_slides.py` エラー0
- [x] ブラウザ実レンダ: 全19枚 1280×720・全フラグメント表示で境界超過0、s7b の棒の実測（getBoundingClientRect）、カウントアップ着地値、段階表示/動き（frag・emph）の動作
- [ ] 通し練習・時間計測（目標19〜20分・s2–s5 は4.5分以内・山場 s7b/s7c/s13 はゆっくり）。押した場合の削減候補は原稿「補足メモ」
- [ ] 想定問答・補足・書き出し: Q&A を DEC-026/027 で再確認（β/p値/戦争ニュース比較は口頭対応）、b1 は caveat 付き、budoux 後の中黒 ZWSP 2件の再挿入有無、PDF/印刷の予備出力

## 📥 Inbox（未triage）
- **⚠ 未マージブランチ `codex/20260725-ic-claims`（main+4コミット）**: ITEM-022 監査修正＋ITEM-024 戦争ニュース比較の実体。**ユーザーのマージ判断待ち**（他ツール作業のため自動マージせず 2026-07-27）。マージ後にこの行を消す。注: index の ITEM-022 done / DEC-026-027 / 正準値（β=0.633 等）はこのブランチ上の状態で、main 未着地
- **[繰越] critic-calib**: pending-review-findings 2件 [deferred]（coherence/testability-critic・claude-brain 側）。次回 claude-brain セッションで「calib」起動
- **[繰越] lesson review 期限超過**: 候補32件(hot_to_warm 5 / chromadb_to_warm 27)・前回2026-07-13。次回任意セッション冒頭で「lesson review」起動（承認ゲート伴うため handoff 時に skip した 2026-07-25）
- **[繰越] 孤児 pending の一括回収**: `~/.claude/state/pending_{lessons,corrections}/` に他セッション分 38+14件（14日TTL内）。次回 claude-brain セッションで lesson-recorder sweep
- claude-brain: 情報の引き出し方の調査とアップデート＋RAG先行研究調査（Slack #todo より _2026-06-23_）→ **本 repo でなく claude-brain 側の案件**。handoff 時に gh issue 化を試みたが permission 拒否（2026-07-07）＝**次回 claude-brain セッションで ITEM 化して本行を消す**（ITEM-016 retrieval gate と統合可否も判断）

## 🗂️ 運用・監視（案件でなく反復運用・トリガー型）
- slides/*.html 編集時: `check_slides.py` PostToolUse hook が自動検査（第1回デッキは発表済み凍結＝編集するとエラーが出る仕様）
- paper/*.md 編集時: thesis-writing スキル必ず経由（golden 表は暦年 DEC-023 準拠に更新済み）
- 数値を触ったら: `check_golden` PASS＋撤回済みパターン grep（スキル §2）

## 🧠 Context not in code
- 決定:
  - **監査後の背骨（DEC-026）**: 固定数量輸入コスト約35兆円（会計近似）+ Q1-Q5固定バスケット生活費 +2.01pp。正準IC回帰はβ=0.633（通常p=0.0009）だが財サービス交絡のため因果解釈しない
  - **識別の枠組（DEC-024）**: 本設計= GPSS share外生設計。shock外生ルートは K=1 で論理的に閉じている。goods/services 交絡=仮定違反の定義そのもの・プラセボ負相関= Test 2 失敗シグナル。「識別に類例がない」は使用禁止
  - **数値の正**: Q1-Q5 +1.04/+2.01/+2.06/+2.45pp・2025=+3.36pp、固定数量輸入コスト35.3/28.4/29.1/24.8兆、正準IC β=0.633、LP gap global p=0.035、Phase3 Koyck RMSE=10.40pp
  - βは関連の要約であり転嫁率の因果推定ではない。Phase3は正準ICスケールでもovershootし、方向のみ使用
- 参考情報: 先行研究ハンドオフ = `tasks/先行研究_識別戦略ハンドオフ_20260707.md`（①②消化済みバナーあり）

## ❌ Don't do (this task)
- [trap] EnterWorktree は origin/main 起点＝ローカル main の未 push マージを含まない → `git reset --hard main` で追随してから作業する
- [trap] budoux 再適用で中黒 ZWSP の手動挿入2件（第3回デッキ）が消える → 再挿入が必要
- [mistake] スライド・docs の数値を記憶や旧ファイルから転記しない（DEC-021 の事故原因）。必ず生成 CSV / decision-log の正準値から
- [trap] データ駆動チャートの検証は CSS 宣言値の照合で止めない — flex 内ラベル同居で棒の実効上限（~82%）を超えると同長に潰れる。getBoundingClientRect 実測で px/データ比の一定性を確認（2026-07-24 s7b で実害・lesson 記録済）
- [trap] 家計調査「実収入」は移転込み（2020年は給付金で全分位+11%）かつ勤労者世帯のみ収録 — 賃金ストーリーや全体母集団の実質所得検証には使えない（DEC-025）

## 📂 Key files
- `paper/outline.md`（章割り・状態）/ `paper/03a-identification-strategy.md`（識別節骨子・合意待ち）
- `docs/decision-log.md`（DEC-001〜027・数値と判断の正）/ `docs/research-design.md`（識別の到達点と限界）
- `.claude/skills/thesis-writing/SKILL.md`（執筆規律・golden 表）
- `src/analysis/cost_push_panel.py`（β回帰）/ `tasks/_a4_akm.R`（AKM SE）/ `docs/literature/INDEX.md`（P001〜P095）

## ❌ Out of scope
- seminar1 スライドの修正（発表済み凍結。旧 todo の「スライドレイアウト修正」計画は凍結方針と矛盾するため破棄＝2026-07-07 ITEM 移行時）
- 資本フロー・市区町村単位・サプライチェーン/一般的な地政学リスク・産業構造変化の原因分析（プロジェクトスコープ外。Russia→Ukraine 戦争ニュースは DEC-027 の識別頑健性比較に限定）
- P077 型 SE のフルスクラッチ自力実装（ITEM-001 のスコープ外条項）

---

_完了ログ: `tasks/done/2026-07.md`（2026-07 セッション）・`tasks/done/2026-06.md`（2026-05-31〜06-26 分も移設済み）・`tasks/done/2026-04.md`_
