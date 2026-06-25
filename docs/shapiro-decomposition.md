# Shapiro 供給/需要分解 — 層1 結果（national・ベンチマーク）

_実装: `src/analysis/shapiro_decomp.py` / 出力: `data/processed/shapiro/` / 根拠: DEC-016 + 補遺（pre-registration）_

## 位置づけ
Phase 2a の弱識別 β に依存しない**第3の柱**。Shapiro (2024, P081) の価格×数量 comovement 符号分解を日本に適用し、観測された価格変動のうち**供給駆動（≒コストプッシュ）成分のシェア**を清浄 control なしにラベル付けする＝Phase 1（会計）/ Phase 2b（恒等式）の cost-push 主張を**三角測量**で補強。

## データ・手法（pre-registration 通り・split を見る前に固定）
- **価格 P**: CPI 品目指数（`0003427113`・2020基準・月次・全国）
- **数量 Q**: 家計調査 品目別数量（`0003343670`・月次・二人以上世帯・2000–2024）
- **ウェイト**: 同調査 金額（`0003343671`・**全国 `cdArea=00000`**・2015–24 平均）＝固定支出ウェイト
- **バスケット = 116 物理数量 食料＋家庭用エネルギー品目**（crosswalk 116/192・正規化名称 exact マッチ・未マッチ76は `crosswalk.csv` に記録／silent cap なし）。**公式 食料CPI とは別物**（後述・物理数量で測れる品目のみ＝外食/調理/加工を含まず、ガソリン・LPガス等の家庭用エネルギーを含む）
- **残差化**: Δlog(P), Δlog(Q) に per-item **VAR（P・Q両方の cross-lag）+ 11ヶ月ダミー**（季節→期待成分）。月の**連続性マスク**（非連続月の Δlog を NaN 化＝gap跨ぎの spurious 変動を除去）。残差 ν^p, ν^q の符号で分類: **逆符号→supply**（コストプッシュ）／**同符号→demand**
- **集計**: Shapiro (P081) の定義に従い**インフレ寄与加重**（Σ w_i·Δp_i）。supply share = supply ラベル品目の寄与 / 全寄与。**品目数の割合でなく寄与で加重**（Shapiro 本来の定義。割合metricは価格変化の大きさを無視し survey noise に支配され ≈0.5 でフラットになることも確認）

## 結果 ★headline = supply-driven SHARE（within-basket・Shapiro 本来の出力）
primary spec = VAR・6 lag、post-mask:

| 年 | supply share |
|----|------|
| 2019 | 0.50 |
| 2020 | 0.90（デフレ年・符号messy） |
| 2021 | **0.41**（需要主導＝経済再開） |
| 2022 | **0.70**（供給surge） |
| 2023 | 0.60 |
| 2024 | 0.83 |

- **2021 需要主導 → 2022 供給主導の転換**は Shapiro 米国系列（2021春 需要急伸→2022初 供給急伸）および本プロジェクト `inflation-timeline.md`（日本 cost-push 主導 2022–24）と整合。月次では **2022年2月（侵攻）から supply share が 0.80→0.93→1.0+** に跳ね上がるクリーンな署名
- **2022 supply 寄与(+2.58pp相当)の品目構成は broad（top5=43%）・筆頭は ガソリン・鶏肉・さけ・プロパンガス・ブロッコリー** ＝エネルギー＋輸入食料＝**輸入コストプッシュ・チャネルそのもの**

## Robustness（share・spec lock 後に確認・tuning せず）
- **5 spec で 2022>2021 の supply-share 上昇が頑健**: {VAR,AR}×{3,12 lag}+primary。2022 share = 0.70/0.79/0.68/1.02/0.70
- **balanced 105品目（full-coverage）**: 2021 0.42 → 2022 0.72（保持）＝バスケット集合のアーティファクトは share に届かない
- **生鮮除外（高ボラ27品目・std>0.08）**: 2021 0.42 → 2022 0.76（保持）。生鮮（天候=国内供給）を除いても転換は残る
- **near-zero ν^p**: 0.01%閾値で1.6%、0.1%閾値でも 2022 supply 寄与のうち near-zero 由来は **5.5%** のみ（sticky-CPI で label が数量符号に collapse する懸念は実質非問題）

## ⚠️ バスケット vs 公式 食料CPI（開示・hide でなく disclosure）
covered basket の年平均 YoY は**公式 食料CPI を tracking しない（構造上の乖離）**:

| 年 | 公式 食料CPI YoY | covered basket YoY |
|----|------|------|
| 2022 | +4.45% | +6.12%（バスケットは2022でピーク） |
| 2023 | **+8.06%**（公式ピーク） | +3.99% |
| 2024 | +4.34% | +2.60% |

- 乖離の理由: バスケットは**物理数量品目のみ**で、2023食料サージを牽引した**外食・調理食品・加工食品が欠落**、かつエネルギーを含む
- **この乖離は contradiction でなく feature**: 同じ輸入ショックが 2022 に生鮮・素材へ、2023 に外食/調理/加工へと**ラグ付き転嫁**した姿＝cost-push の supply-chain passthrough と整合
- ∴ 主張スコープを厳守: 「**この basket 内で 2022 に供給圧力が surge した**」は ship／「日本の**食料**インフレの X% が供給駆動」は**書かない**

## Caveat（claim を縛る・全 docs 共通）
1. **「供給駆動」≠「輸入コストプッシュ」**: Shapiro の supply ラベルは国内労働・天候等の全供給ショックを含む広い対象。三角測量/補強であり headline で "X%が輸入cost-push" と断定しない
2. **scope = covered basket（116 物理数量 食料+家庭用エネルギー）内**のシェア。headline CPI でも 食料CPI でもない
3. **set-identified**（Shapiro・magnitude 不能・ラベルのみ）。因果 β の代替でなく記述的分解の補完
4. **家計調査数量は標本調査ノイズ**（~9千世帯）→ 品目別月次ラベルはノイズ大。支出加重集計で平均化されるが、これが層2（五分位＝少標本・年次）を exploratory に留める理由でもある
5. **pp 寄与（supply_infl/total_infl）は Dec-to-Dec モメンタム＝内部 denominator**。年平均YoYでも 食料CPI 比較対象でもない。headline は share

## 出力ファイル
- `data/processed/shapiro/crosswalk.csv` — 品目対応（matched フラグ・未マッチ記録）
- `data/processed/shapiro/price_quantity_panel.csv` — 月次 P×Q パネル
- `data/processed/shapiro/supply_share_primary.csv` — primary 月次系列（supply_infl/total_infl/share/near-zero）
- `data/processed/shapiro/supply_share_{VAR,AR}_lag{3,12}.csv` — robustness grid

---

# 層2 — group-specific（五分位・年次・novel）★INCONCLUSIVE

_実装: `src/analysis/shapiro_quintile.py` / 出力: `data/processed/shapiro/quintile_*.csv` / 根拠: DEC-016 層2 pre-registration_

## 設計の crux（framing knife-edge・advisor）
P=national CPI は**全 quintile 共通**→ ν^p は全 group 同一系列（コードで assert・GATE OK）、group 差は **sign(ν^q_g)＝数量応答の差のみ**。∴測るのは「共通価格ショックを数量削減で吸収するか消費拡大で吸収するか」＝**差別的消費応答**。
- ✅「Q1 の共通価格ショックへの消費応答がより収縮的/不本意(supply-like)、Q5 は維持/拡大(demand-like)」
- ❌「Q1 はより供給駆動/cost-push インフレに直面」（誤り・価格共通）
- 位置づけ: Phase 2b 背骨（Q1 実効インフレ+1.42pp）の**メカニズム**を探る三角測量。

## spec（exploratory・1 spec のみ）
五分位数量 `0003348236`（年次2000-2024=25点・crosswalk 116品目再利用）×national CPI 年次。残差化=**(group,item)別 YoY demean のみ**（VAR は24点で不可）。ウェイト=五分位金額 `0003348240`。headline=**shock years 2021-24 pooled の group別 supply share**。

## 結果・判定 ★pre-registered 仮説は robust に支持されず＝INCONCLUSIVE
pooled supply share: Q1 0.573 / Q2 **0.666** / Q3 0.509 / Q4 0.501 / Q5 0.530（Q1−Q5=+0.043・**非単調**）。

per-year で Q1>Q5 は **2/4 shock years のみ**:

| 年 | Q1 | Q5 | Q1>Q5 |
|----|----|----|----|
| 2021 | 0.61 | 0.47 | ✅ |
| 2022 | 0.66 | 0.71 | ❌（コア cost-push 年で逆転） |
| 2023 | 0.55 | 0.62 | ❌（同上） |
| 2024 | 0.58 | 0.49 | ✅ |

- **pooled の正(+0.043)は 2021+2024 由来のアーティファクト**。2022-23 で逆転＝方向が robust でない
- **全 group が ~0.50-0.67 に clustering ＝層1で noise と診断した flat-~0.5 署名と同じ**（層2 は P 共通ゆえ寄与加重で group 差別化できず fraction-base 不可避＝metric エラーでなく「五分位×年次で符号分類がほぼランダム」を意味）。∴ null は wishy-washy な「weak support」でなく **decisive**
- **null の第一診断＝識別限界**（coarse data/noise だけでない・advisor）: 符号法は高 ν^p 年に数量を多く削った group を supply ラベルするが、**不本意な収縮（Q1 squeezed）と裁量的柔軟性（Q5 が trade-down/代替）を区別できない**。むしろ後者が優勢になり得る（裕福層ほど任意品目で削れる数量が多い／Q1 は必需品で subsistence 近く数量を削れない＝厚生損失は大きいのに数量応答は小さい）。2022-23 の Q5>Q1 は**符号法が誤読する実信号かもしれず**、単なる noise でない。DEC-015「識別限界の方法論的提示」frame と整合
- **a-priori sign は曖昧**（pre-registered Q1>Q5 は richer-household substitutability が反対に効くため断定不可）。「Q1 がより収縮的消費応答」も robust には言えない（✅ branch 内の第2 knife-edge）
- **Phase 2b は無傷**: 実効インフレ gap はウェイトベースで robust。層2 は別マージン（数量応答）を探り解像/識別不能と判明しただけ。五分位は1/5ずつ＝標本サイズ可比なので gap 不在は標本数アーティファクトでない
- **rescue しない**: elasticity 回帰（Δlog Q_g on Δlog P × group）は better-powered な「真の object」だが別手法＝done-line での scope creep。本セッションの誠実 posture を保ち exploratory Shapiro null を as-is で残す

## 出力（層2）
- `quintile_quantity.csv` `quintile_expenditure.csv`（五分位 年次 raw）/ `quintile_labels.csv`（item-year ラベル）/ `quintile_supply_share.csv`（pooled）
