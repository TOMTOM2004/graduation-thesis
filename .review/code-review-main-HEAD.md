# Code Review: main..HEAD（worktree-20260706-audit-doc-fixes・5コミット）

_effort=standard / mode=hunk_focus（実効660行・uv.lock除外） / critics 11（テスト系2体は対象入力なし=pass） / verify=blocker+major 3件を review-skeptic で3値判定（minor は unverified 据置）_

## Summary
- **Overall verdict: GO-WITH-FIXES**（gate 適用後 main blocker 1 → 本レビュー直後に修正予定）
- Findings: blocker 1（CONFIRMED）/ major 0（2件は verify で minor へ降格）/ minor 8 / nit 1
- 監査本体（DEC-019/020/021 の数値置換・再現性強化）の方向・置換値の正確性に対する反証なし

## Findings by Severity

### blocker
1. **README.md:36-47 — 撤回済み旧値の残存** (verified: CONFIRMED) [removed-behavior, cross-file]
   - β=0.431/p=0.002・年次相関+0.42〜+0.60・+1.42pp・RMSE 9.744pp・「⚠️再較正中」警告が README 本文に残存し、DEC-021 で統一した docs/ 新値と矛盾。一次窓口の README だけが旧値。
   - fix: 主要結果節を再生成値（β=0.425/p=0.047・+2.14pp・10.00pp・再較正完了）に更新

### minor（verify で降格した2件）
2. **src/data/fetch_worldbank.py:120 — WB API 応答の無検証保存** (verified: CONFIRMED→downgraded) [correctness, test-coverage]
   - ページング未対応（DEFAULT_YEAR_RANGE=1960-2026×country=all で per_page 4000 超過があり得る＝silent truncation）＋ HTTP200 エラーボディを --force 時に raw へ上書きし得る。降格根拠: --force 明示時のみ・docstring に注意書きあり。fix 推奨: pages ループ＋[metadata, data] 構造 assert
3. **src/analysis/io_price_model.py:48 — BETA_EMPIRICAL の import 時即時読込** (verified: CONFIRMED→downgraded) [correctness, cross-file, principles]
   - CSV 不在の fresh 環境では import 自体が**素の FileNotFoundError** で落ちる（コード中の RuntimeError ガードには到達しない・skeptic が退避実験で実証）。policy_simulation / tasks/_phase3_recalib_check に波及。fix 推奨: FileNotFoundError を捕捉し「先に cost_push_panel.py を実行」の明示メッセージ化

### minor（unverified）
4. trade_loss.py:310 `compute_baseline_sensitivity` だけ force 未対応（README の一般化記述と矛盾）[maintainability]
5. docs/decision-log.md DEC-021 の更新対象ファイル列挙に design-review.md / saito文献メモ / paper/01 / paper/04a が漏れ [maintainability]
6. tasks/_a4_akm_prep.py --check が未実行（B-4 で上流が変わったため既存 _akm_cross.csv とは不一致になる見込み＝Phase 3 で要実行・結果を DEC に1行記録）[test-coverage]
7. principles: cache パターン13箇所複製（DRY・研究コード方針より許容範囲）/ _load_beta_empirical の import 副作用（#3と同根）
8. clarity: DEC-019/021 の長文・「＝」接続・「UB」略語未定義（decision-log 内部文書のため任意）
9. quintile_impact.py:454 force docstring の書式揺れ（nit）

## Strengths
- β/δ/GDP の単一ソース化・force 統一・lockfile 追加は「誰が実行しても同じ結果」への正しい方向（verify でも置換値自体への反証ゼロ）
- _a4_akm_prep.py の --write ゲート・fetch_worldbank のデフォルト skip 等、raw 保護の設計が一貫
- security: secrets 混入なし・setuptools 83.0.0 既知CVE非該当

## Cloud Handoff（/ultrareview 用）
- #1 は本セッションで修正予定のため転送不要。#2/#3 の fix 妥当性、DEC-021 の数値置換の transcription 再検証が cloud 向き

## 次のステップ
push 前に最終レビューを行う場合、user 側で起動: /ultrareview（本ファイルの cloud_handoff を context として渡す）
