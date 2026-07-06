# Basic Design Review: goods-services-contrast（v1 に対する所見・v2 で全て反映済み）

_critics 9（assumption/feasibility/risk/scope/testability = high, specificity/coherence/clarity = medium, gap = low）。verdict: v1 = soft_fail（blocker 1・major 8）→ **v2 で全件反映済み・GO**_

## Findings（dedupe 後・v2 での対応）
1. [blocker→解消] golden 照合が擬似コード・year 対応暗黙・導出手法参照なし（testability+assumption+clarity）→ §0.1 year:value 表（3桁実測値）+ §2.1 check_golden 実コード
2. [major→解消] §3 集計誤り services=13/mixed=3 → 実カウント **14/2**（scope・coherence が独立検出）→ 集計行・§1.3・assert(3) を同期
3. [major→解消] (a)/(b) 判定の定量基準なし（scope+risk・事前登録の穴）→ 「4年全正かつ中央値≥+0.10 なら (b)」の機械規則
4. [major→解消] worktree に gitignored data 不在で初手デッドエンド（risk・実測ベース）→ §1.2 データ提供手順
5. [major→解消] matplotlib Agg/show() 未規定（feasibility が plot_scatter_panel のハングを実測）→ §2.1 必須事項
6. [major→解消] 分類の双方向検証欠落（testability）→ load_panel 双方向 assert + バケットサイズ assert
7. [major→解消] doc 突合・CSV 抽出条件が曖昧（testability+clarity）→ §5 抽出規則・§6-3 突合コマンド
8. [major→解消] 回帰コピー分岐の同一性検証不能（testability）→ import 一択に単純化（feasibility が部分集合で動作することを実測済み）
9. [minor 群→解消] WebSearch/WebFetch 2段階・DEC-022 書式参照・S3 条件式・差し戻し手順・クラスタ数 note・rollback 一文 ほか

## 検証済みの強み（critic 実測）
- §3 の41キーは panel_cost_push.csv の distinct cpi_mid_name と字面完全一致（assumption が実測）
- golden 値はデータで再現確認済み（assumption・feasibility が独立に再計算一致）
- §5 アンカー3箇所は実ファイルで一意ヒット（risk が grep 確認）
- run_panel_regression はバケット部分集合（n=13相当）で正常動作（feasibility が実行確認）

## verdict: v2 = GO（実装セッションに渡してよい）
