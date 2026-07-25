---
id: ITEM-022
title: IC正準化・クレーム精緻化・LP統合の監査修正
status: done
priority: P1
source: user
context: personal
created: 2026-07-25
updated: 2026-07-25
links: [tasks/plan-audit-20260725-ic-claims.md, docs/decision-log.md, docs/oil-shock-lp-investigation.md]
---

## 背景

研究・論文・スライドの全体監査で、輸入含有率（IC）の定義、購入者価格・マージン、
35兆円と +2.01pp の表記、先行研究上の貢献、LP のクレーム階層、DESIGN.md の
数値規律に残ギャップが確認された。外部レビューの全面改修案を repo 実物と再照合し、
既実装の定義2・DiD・LPを活用する選択的修正 plan にユーザー承認済み。

## 承認済み方針

1. 定義2を記述・会計用途の正準候補とし、人工IOテストと購入者価格感度を通過後に正式決定する。
2. 回帰では定義1・定義2を併記し、既存の識別限界を覆したとは書かない。
3. RQは縮小せず、「実質消費」から測定対象である生活費負担へ動詞を精緻化する。
4. LPは石油供給ニュースに限定した因果証拠として統合し、同時推論までは Tier 2 とする。
5. 35兆円は固定数量の Laspeyres 型近似、+2.01pp は2015–19年平均基準からの累積と本文初出で明記する。

## 実装チェックリスト

- [x] `tests/test_io_ic.py` を先に追加し、定義1・定義2の人工IO表手計算を固定する
- [x] 既存テスト相当の print 検証を pytest 化する
- [x] 購入者価格表・商業運輸マージンの構造を調査する
- [x] 生産者価格版と購入者価格版の IC 感度を計算する
- [x] 定義2の正準判断を DEC に記録する
- [x] 5グループ限定 IC を「総輸入含有率」と呼ばないよう命名・表記を修正する
- [x] 定義2を用いたパネル回帰・年次相関・財サービス分解の感度列を追加する
- [x] Phase 3 の IC 定義依存を再計算し、絶対値を補助扱いに固定する
- [x] LP のホライズン横断 joint inference / uniform band を実装する
- [x] 日銀・OECDを含め所得階層別インフレの先行研究ギャップを再検証する
- [x] decision-log → overview → research-design → contribution → outline → paper の順で同期する
- [x] seminar3/4 の数量固定、貢献、基準期間表記を同期する
- [x] `docs/DESIGN.md` の32px / 15–17px / min16px競合を解消する
- [x] キャッシュなし再生成、撤回済み表現grep、pytest、HTML描画検証を通す

## 対象外

- 発表済み seminar1 の修正
- seminar4 s11 の意図的 placeholder の削除
- 実質消費数量・名目所得を新規推計する大規模な研究拡張

## Decision log

- 2026-07-25: ユーザーが `tasks/plan-audit-20260725-ic-claims.md` と追加校正
  （定義2は条件付き正準化、RQは動詞精緻化、LPは限定的因果証拠）を承認。
- 2026-07-25: 定義2を正準化。価格評価は用途別併存、3貢献へ精緻化、
  LP共同推論を統合。14 tests pass、将来2デッキは静的検査・1280×720描画検査を通過。
