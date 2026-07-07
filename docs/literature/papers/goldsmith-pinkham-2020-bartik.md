---
id: P005
title: "Bartik Instruments: What, When, Why, and How"
authors: "Goldsmith-Pinkham, Sorkin, Swift"
year: 2020
source: "American Economic Review, 110(8), 2586-2624"
doi: "10.1257/aer.20181047"
importance: High
categories:
  - identification-strategy
verified: true
added: 2026-04-10
updated: 2026-07-07  # DEC-024: NBER WP 24408 全文精読で深化（識別失敗後の本設計との突合）
---

## Summary
Bartik（shift-share）操作変数の解釈と妥当性検証を体系化。Bartik TSLS は「シェアを操作変数・国全体成長率の外積をウェイト行列とする GMM」と数値的に同一（Prop 1.1）であることを示し、識別を**シェアの外生性**に基づくものとして定式化。診断ツール一式（Rotemberg weights・シェアの相関物・pre-trends・過剰識別・代替推定量）を提示。

## Methodology
- Bartik IV = シェアを IV とする GMM の等価性定理（Prop 1.1, WP p.11）
- 識別仮定（Assumption 2, Strict Exogeneity, WP p.13）: E[e_lt · z_lk0 | D_lt] = 0 — コントロール条件付きで初期シェアが構造誤差と無相関
- **仮定の対象は水準でなく「変化」**（WP p.14）: 「変化で定義した仕様／unit FE 入り仕様では、シェアがアウトカムの*変化*（誤差項の変化）と無相関という仮定。*水準*との相関は設計を壊さない」
- 設計の性格づけ: "an exposure research design, where the shares measure the differential exogenous exposure to the common shock. In settings where the researcher has a pre-period, this empirical strategy is just difference-in-differences."（Intro, p.2）

## Key Findings
- **固定 K・T（少数ショック）設定では shares 解釈が自然＝事実上唯一**（§2, p.13）。shocks ルート（BHJ）は「only consistent as the number of industries grows」（§2.2, p.15）＝ K が増えない設計では選択不能。**どちらの物語に立つかを選び、明示的に擁護せよ**と勧告。
- **Rotemberg weights**（Prop 3.1, p.16）: β̂_Bartik = Σ_k α̂_k β̂_k、α̂_k = g_k Z_k′X⊥ / Σ g_k′ Z_k′′X⊥。どの IV（シェア）が推定を駆動し、どの排除制約の誤設定に最も敏感かを可視化。パネルでは (k,t) レベルで定義され、**時間側へ集計 α_t も明示的に許容**（§3.3, p.18）＝ K=1 の単一 shifter 設計でも「どの年が β を駆動するか」の分解が可能。
- **推奨診断 5 種**（§5）: ①シェアの相関物（シェア*水準*の相関物がアウトカム*変化*を予測したら OVB 示唆。コントロール追加で点推定が動くこと自体が Altonji-Taber/Oster 的に未観測交絡を示唆）②pre-period placebo/pre-trends（非ゼロ＝シェアが他チャネルで結果変化を予測＝仮定違反の証拠）③代替推定量比較（MBTSLS/LIML/HFUL の一致）④過剰識別検定 ⑤異質性パターンの可視化。

## Relevance to This Thesis（DEC-024 で確定）
- **本設計の methodological home**: ΔCPI_{c,t} = β(IC_c×P_t)+FE は教科書的な GPSS share外生設計（単一集計ショック×ショック前決定エクスポージャ・K=1・T=4）。shock外生ルートは論理的に閉じている（＋A-4 実装検証済み＝DEC-013）。
- **goods/services 交絡（DEC-022）＝ Assumption 2 違反の定義そのもの**。財/サービス分解は GPSS Test 1（シェアの相関物）の実施に相当。
- **プラセボ期の負相関＝ Test 2（pre-period falsification）の失敗シグナル**。「ill-posed で無情報」（pooled 回帰）に加え、share 内生性の直接証拠という積極的読みができる。China shock 応用でも pre-trend が「効果の一部を説明しうる」と読んでいる（Intro, p.4）。
- **識別戦略の1段落言語化は `docs/decision-log.md` DEC-024 が正**。方法論章はこの枠組で書く。
- 任意の追加診断: 時点方向 Rotemberg weights α_t（未実装・実装するなら要承認）。

## Limitations / Notes
- 精読は NBER WP 24408 版（AER 版と内容同一とされるが、**AER 版の正確なページ番号は未照合**。引用ページは WP 版）。
- 第三著者は **Swift**（Henry Swift）。Swanson ではない（ハンドオフメモの誤記憶を DEC-024 で補正済）。
- K=1 では産業間の過剰識別検定は使えない（時点方向の β̂_t 一致性のみ検定可能）。
