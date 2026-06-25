---
id: P081
title: "Decomposing Supply and Demand Driven Inflation"
authors: "Shapiro, Adam Hale"
year: 2024
source: "Federal Reserve Bank of San Francisco Working Paper 2022-18 (Feb 2024 revision); forthcoming Journal of Money, Credit and Banking (2026)"
doi: "10.24148/wp2022-18"
importance: High
categories:
  - identification-strategy
  - cost-push-inflation
verified: true
added: 2026-06-01
---

## Summary
100超のPCEカテゴリそれぞれで価格・数量の誘導形回帰を走らせ、残差の符号の共変動からカテゴリ×月を「供給駆動」か「需要駆動」かに分類する枠組み。需要シフトは供給曲線上で価格と数量を**同方向**に動かし、供給シフトは需要曲線上で**逆方向**に動かす、という標準的な符号制約（Faust 1998, Uhlig 2005 系の sign restriction）を per-category で適用。供給駆動・需要駆動寄与は、各ラベル群に属するカテゴリのインフレ率を BEA の支出ウェイト（集計PCEインフレ構築に使うのと同一ウェイト）で加重平均して構築。**集計インフレを「清浄な control 群なしで」供給/需要に分解できる点が本研究の Q1+Q4 への直接的回答**。

## Methodology
- 各セクター i に上方供給曲線 q=σp+α・下方需要曲線 p=−δq+β を仮定。構造ショック ε^s=Δα, ε^d=Δβ。
- これを構造VAR `A^i z_{i,t}=ΣA^i_j z_{i,t−j}+ε_{i,t}`（z=(q,p)）に翻訳。誘導形残差 ν^q, ν^p の符号が構造ショックの符号を識別（Jump & Kohler 2022）：
  - ν^p, ν^q **同符号** → 需要ショック発生（カテゴリを demand-driven と labeling）
  - ν^p, ν^q **逆符号** → 供給ショック発生（supply-driven と labeling）
- データ: 米国 BEA PCE、100超の財・サービスカテゴリ、月次。供給/需要駆動寄与系列を毎月更新可能（FRBSF が公開系列として配信）。
- 妥当性検証: HFI 金融政策ショック（Gürkaynak-Sack-Swanson 2005）の局所射影で需要駆動寄与が2年で1.5pp低下、外生石油供給ショック（Baumeister-Hamilton 2019）で供給駆動コア寄与が上昇、と既知の方向に反応。

## Key Findings
- **control 群・反実仮想を一切要しない**。符号制約のみで各カテゴリ月を供給/需要にラベル付け。これが「単一マクロ事象では清浄な control が欠如」という卒論の識別上のつまずきへの最も実装容易な処方。
- post-COVID: 2021春に需要駆動インフレが急伸（経済再開・American Rescue Plan）、2022初頭に供給駆動が急伸（ロシアのウクライナ侵攻）。Baqaee-Farhi(2022)・di Giovanni et al.(2023) 等の構造アプローチと整合。
- **set-identified に留まる重大な caveat（p.7）**: 構造ショックの「サイズは決定不能」。系列は「at least 供給（需要）ショックを経験した支出加重カテゴリのシェア」を追うのみで、ショックの絶対的・相対的な大きさの時系列変化は測れない。供給・需要が同時発生する場合は弾力性 σ,δ に依存してラベルが決まり、相対的大きさは識別されない。

## Relevance to This Thesis
- **Q1（supply vs demand 分解）+ Q4（清浄 control 欠如）への中核的処方であり、採用候補**: per-category の符号回帰は学部卒論でも再実装可能（軽量）。2022-24 日本のインフレについて品目別 CPI×数量（家計調査の数量 or 数量指数）で同型の符号分解を走らせれば、「観測された価格上昇のうち供給駆動（≒コストプッシュ）成分のシェア」を control 群なしに識別でき、Phase 1/2 の交易損失=外的供給ショックという主張を**三角測量（triangulation）**で補強できる。
- **採用 vs 新規貢献の境界を画定（最重要）**: 本論文は供給/需要の**記述的ラベル**を与えるが、卒論 shift-share の目標だった**因果的パススルー係数 β_g（輸入価格ショック→群 g の価格/消費）は与えない**。set-identified ゆえ magnitude を出せない（p.7）。すなわち Shapiro は「これは供給/コストプッシュか需要か、を清浄 control なしで判定する」問題（Q1+Q4）を**解く＝この軸では新規性が弱まる**が、「相関 shifter 下での群別の因果的帰着」（P077 の contamination 問題が刺さる領域）は**解かない＝ここに貢献が残る**。Shapiro は推定量の**代替ではなく、記述的分解の補完／三角測量**として位置づけるべき。
- **所得階層別への橋渡し（要 caveat）**: 本分解は支出加重・カテゴリ分解可能なので、供給駆動ラベルを所得階層別バスケットウェイトで再加重すれば「群 g の、全国基準で供給駆動とラベルされた品目への**エクスポージャー**」を出せる。ただしラベルは**全国の価格＋数量**で推定されており、群別に供給/需要 split を推定したものではない。よって得られるのは「所得階層別の供給駆動インフレ（split 自体が群別）」ではなく「全国ラベルへの群別エクスポージャー」。卒論はこの仮定を明記して使う。

## Limitations / Notes
- **set-identified**（magnitude 不能、p.7 既読）。同時ショック時の相対サイズは弾力性に依存し未識別。
- ラベルは全国データ由来 → 所得階層別バスケット再加重は「群別エクスポージャー」止まり（上記）。
- 数量データが必要。日本適用時は家計調査の数量・数量指数等の整備が前提（米PCEより粗い可能性）。
- FRBSF 公開系列は米国 PCE のみ。日本系列は自作要。IMF WP 2023/205 等が同手法を多国に拡張済みで参照可能。
