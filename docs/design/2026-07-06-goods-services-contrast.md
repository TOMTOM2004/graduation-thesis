# 設計書: 財/サービス分解による識別限界の実証（goods-services contrast）v2

_status: 設計確定（v2・/review-basic-design の blocker/major 反映済み）。実装は別セッション（Sonnet）が本書のみを根拠に行う。_
_発注者: DEC-021 補遺の探索診断（2026-07-06）で「全体の符号コントラストが goods-vs-services 交絡由来の可能性」が示唆されたため、これを正式分析に格上げする。_
_DEC 番号: 本分析の完了時に **DEC-022** として decision-log に記録する（書式は DEC-021 のエントリ構造〔太字小見出しの箇条書き〕に倣う）。_

---

## 0. プラン（What / Why / Done when）

- **What**（3点）: ① IC-ΔCPI の年次符号コントラストを CPI 中分類の財/サービス分解で再計算する分析スクリプト `src/analysis/goods_services_contrast.py` を新規追加する。② その出力（CSV・図）を生成する。③ 結果の数値を §5 指定の3箇所（research-design.md・decision-log.md・第2回原稿の補足メモ）に反映する。
- **Why**（2つの目的）: (1) research-design.md が「最大の脅威」とする goods-vs-services 交絡が、主 falsification 証拠（年次相関コントラスト: ショック期全年正 vs プラセボ期全年負）をどこまで説明するかを定量化する。(2) 貢献③（識別限界の方法論的提示）を「限界がある」から「限界の所在を財/サービス分解で特定した」へ格上げする。※識別の救済（β の有意性回復）は目的ではない。
- **事前登録（結果に依らず採用・判定は下記の機械的規則で行う）**:
  - **判定規則**: S1 の goods バケットのショック期年次相関4つ（2021/2022/2023/2024）を CSV から取り、「**4年すべて正 かつ 中央値 ≥ +0.10**」なら **(b) 勾配が残る**、それ以外はすべて **(a) 消える** と判定する。実装者はこの規則以外で判定しない。
  - (a) → 「符号コントラストの主要部分は財/サービス構成差で説明される」と限界節に明記。(b) → 「財内部にも IC 勾配が残る」と1段強い支持として記載。**どちらの結果でも書く。結果を見てから仕様・判定規則を変えない。**
- **Done when**: ①スクリプトが入力から決定論的に CSV+図を再生成できる ②doc 3箇所が CSV の値だけで更新されている（手打ち数値ゼロ・§6-3 の突合通過） ③DEC-022 記録済み ④スクリプトの diff が `/review-code light`（コードレビューの slash command。実装セッション内で実行）を blocker/major ゼロで通過。

### 0.1 golden（S0 期待値・year:value 対応表）

S0（全39・分類に依存しない）の年次相関は、**既存 `src/analysis/cost_push_panel.py` の `plot_yearly_correlation` と同一手法**（①`is_competitive_import` で衣料・履物を除外 → ②年ごとに subset → ③`dropna(subset=["ic","delta_cpi"])` → ④Pearson `Series.corr`）で算出したとき、次の値に **±0.005** で一致しなければならない（一致しない場合のみ実装バグと判定する）:

| year | 2015 | 2016 | 2017 | 2018 | 2019 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|---|---|---|---|
| corr | −0.196 | −0.096 | −0.147 | −0.222 | −0.267 | +0.083 | +0.103 | +0.405 | +0.235 |

（2020 年は panel に存在しない。**暦年再生成＝DEC-023・2026-07-07**。旧・年度ベース値: −0.167/−0.102/−0.174/−0.253/−0.232/+0.064/+0.136/+0.389/+0.255。）

---

## 1. 基本設計

### 1.1 スコープ

| In | Out |
|---|---|
| 新規分析スクリプト `src/analysis/goods_services_contrast.py` | 既存パネル回帰（cost_push_panel.py）の変更 |
| 財/サービス分類テーブル（本書 §3 で確定済・41カテゴリ） | 分類の再判断（Sonnet は本書の表を変更しない） |
| 出力 CSV + 図 各1 | β メイン仕様・Tier1 数値・スライド HTML の変更 |
| doc 反映3箇所（§5・アンカー指定済み） | 新しい識別戦略の追加・因果主張 |

### 1.2 入力（すべて既存・生成コード実在）

| 入力 | 生成元 | 使用列 |
|---|---|---|
| `data/processed/price-indices/panel_cost_push.csv`（41カテゴリ×2015-2024・2020欠落・369行） | `src.analysis.cost_push_panel.build_panel_dataset()` | `cpi_mid_name, year, delta_cpi, ic, is_competitive_import` |
| 分類テーブル | 本書 §3（スクリプト内 dict として**手入力で転記**。分類は「結果数値」ではなく研究上の事前定義なので DEC-019 のハードコード禁止に該当しない。各行に根拠コメント必須） | — |

**データ提供（worktree 前提・重要）**: `data/raw/**` と `data/processed/**` は gitignore されており、**新規 worktree にはコピーされない**。実装開始時に最初に次を実行すること（これをしないと §2.2 の全コマンドが失敗する）:

```bash
# worktree 内で（<MAIN> = /Users/ishidatomonori/Desktop/graduation-thesis）
cp -R <MAIN>/data/raw/. data/raw/
cp -R <MAIN>/data/processed/. data/processed/
```

### 1.3 分析仕様（4仕様・すべて出力）

分析単位は既存回帰と同じ「競争的輸入財（衣料・履物）除外後の39カテゴリ」。

| spec | バケット定義 | 目的 |
|---|---|---|
| S0 | 全39（既存の全体コントラストの再現） | golden・比較基準 |
| S1 | goods(20) / services(14)（energy_util(3) と mixed(2) は除外） | 主仕様: 純粋な財/サービス対比 |
| S2 | goods + energy_util (23) / services(14) | エネルギー公共料金を財側に含める感度 |
| S3 | S2 と同じバケットから、`cpi_mid_name ∈ {"電気代","ガス代"} かつ year ∈ {2023, 2024}` の**レコード（CSV の行）のみ**除外 | 電気・ガス激変緩和補助金（2023/1〜）が高IC財の ΔCPI を人為的に抑制する歪みの除去（「他の光熱」=灯油は補助対象外なので除外しない） |

各 spec × バケットについて算出する指標:
1. **年次断面相関** corr(IC, ΔCPI)（2015-2019, 2021-2024 の各年。算出手法は §0.1 の4ステップと同一。dropna 後の n が `MIN_N_CORR=8` 未満の年は value=NaN とし n は記録）
2. **pooled 回帰 β**（ショック窓 `years=(2021,2024)` / プラセボ窓 `years=(2015,2019)` の2本）: 既存 `cost_push_panel.run_panel_regression` をバケット部分集合 df に適用（§2.1）。**note 列に「p は entity-cluster（クラスタ数=当該バケットのカテゴリ数）・exposure-robust でない参考値」と、クラスタ数の実数を記録する**。exposure-robust とは「少数の共通ショックに頑健な推論（AKM 等）」の意で、本分析の p 値はそれではないため参考値扱い（過大解釈防止）。

### 1.4 出力

| 出力 | 形式 |
|---|---|
| `data/processed/price-indices/goods_services_contrast.csv` | long 形式: `spec, bucket, metric('corr'\|'beta'\|'beta_p'), year_or_window('2015'..'2024'\|'shock'\|'placebo'), value, n, note` |
| `data/processed/price-indices/fig_goods_services_contrast.png` | 左: S0 の年次相関棒（既存 `fig_yearly_correlation` と同スタイル）/ 右: S1 の goods vs services 年次相関を並置。japanize_matplotlib 使用 |
| doc 反映 | §5 のアンカー3箇所 |

### 1.5 失敗モードと対策（risk）

| リスク | 対策 |
|---|---|
| 分類の恣意性で結果が動く | §3 の表を固定・S1/S2/S3 の感度で頑健性を示す・官公表分類との突合手順（§4）で検証 |
| 補助金歪み（2023-24 電気ガス）で within-goods 相関が下向きバイアス | S3 で分離。S2 と S3 の差自体を「政策価格統制の影響」として記載可 |
| n が小さい年・クラスタ数が少ないバケットの過大解釈 | n<8 は NaN・全出力に n 併記・β の note にクラスタ数と参考値注記・doc には相関の範囲（min〜max）だけ書く |
| 実装者による doc の書き過ぎ（因果主張への滑り） | doc 反映は §5 の指定文面のみ。追加の解釈文を書かない |
| doc 反映の誤記載 | 該当アンカー1箇所のみを元の文面に戻し、CSV を force=True で再生成してから §6-3 の突合をやり直す（他の箇所に触れない） |

---

## 2. 詳細設計

### 2.1 ファイル: `src/analysis/goods_services_contrast.py`

モジュール構成（順序: パス定数 → 分類 dict → load → compute → 回帰 wrapper → print → plot → `__main__`）:

```python
import matplotlib
matplotlib.use("Agg")   # 必須: pyplot import より前。plt.show() は呼ばない（savefig + close のみ）

DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
PRICE_DIR = DATA_PROCESSED / "price-indices"

# §3 の分類テーブル41件を手入力で転記（キー=cpi_mid_name、値="goods"|"services"|"energy_util"|"mixed"）
# 各行に §3 の「根拠」列をコメントとして付ける
GOODS_SERVICES_MAP: dict[str, str] = {...}

SHOCK_YEARS = (2021, 2024)      # run_panel_regression の years 引数形式（両端含むタプル）
PLACEBO_YEARS = (2015, 2019)
MIN_N_CORR = 8

# §0.1 の golden（year: 期待相関）。検証専用・分析には使わない
GOLDEN_S0_CORR = {2015: -0.196, 2016: -0.096, 2017: -0.147, 2018: -0.222, 2019: -0.267,
                  2021: 0.083, 2022: 0.103, 2023: 0.405, 2024: 0.235}  # 暦年DEC-023

def load_panel() -> pd.DataFrame:
    """panel_cost_push.csv を読む。
    - 存在しなければ RuntimeError（『先に python -m src.analysis.cost_push_panel を実行』と案内。io_price_model._load_beta_empirical と同型）
    - 衣料・履物（is_competitive_import==True）を除外
    - 双方向の分類検証を assert:
        (1) panel の distinct cpi_mid_name（除外前41件）⊆ GOODS_SERVICES_MAP.keys()
        (2) GOODS_SERVICES_MAP.keys() ⊆ panel の distinct cpi_mid_name（除外前）
        (3) bucket 別カテゴリ数（除外後）が goods=20 / services=14 / energy_util=3 / mixed=2 に一致
      いずれか不成立なら AssertionError で fail（silent drop 禁止）
    - bucket 列を付与して返す"""

def yearly_corr(df: pd.DataFrame) -> dict[int, tuple[float, int]]:
    """§0.1 の4ステップ（年 subset → dropna(subset=["ic","delta_cpi"]) → Series.corr）。
    戻り値 {year: (corr or NaN, n)}。n < MIN_N_CORR は corr=NaN"""

def run_bucket_regression(df: pd.DataFrame, years: tuple) -> dict:
    """from src.analysis.cost_push_panel import run_panel_regression し、
    バケット部分集合 df をそのまま渡す（years はタプル・df 側で bucket 絞り込み済み）。
    **自前で回帰を再実装しない・コードのコピーもしない**（import 一択。
    部分集合で動くことは 2026-07-06 に services n=13 相当で実測確認済み）。
    戻り値から beta, pval, n_categories を取り出して返す"""

def compute_contrast(force: bool = False) -> pd.DataFrame:
    """§1.3 の4仕様×指標を計算し goods_services_contrast.csv にキャッシュ。
    force: キャッシュを無視して再計算（再現性検証用）
    出力スキーマは §1.4 のとおり"""

def check_golden(df: pd.DataFrame) -> None:
    """S0 の corr を GOLDEN_S0_CORR と突合（§6-1）。実装はこのまま使う:
    sub = df[(df.spec=="S0") & (df.metric=="corr")]
    for year, expected in GOLDEN_S0_CORR.items():
        actual = float(sub[sub.year_or_window==str(year)]["value"].iloc[0])
        assert abs(actual - expected) <= 0.005, f"golden mismatch {year}: {actual} vs {expected}"
    print("golden OK")"""

def print_summary(df) -> None: ...   # 数値は全て df から f-string で（直書き禁止）
def plot_contrast(df, output_path=None) -> None: ...

if __name__ == "__main__":
    df = compute_contrast()
    check_golden(df)
    print_summary(df)
    plot_contrast(df)
```

実装上の必須事項:
- 回帰は `run_panel_regression` の **import 一択**（再実装・コピー禁止。式 ΔCPI = β×(IC×P_import) + γ_t + δ_c と SE 設定の実装差分を作らないため）
- 乱数不使用・キャッシュは force 対応・print/図に結果数値の直書き禁止（DEC-019/021 準拠）
- matplotlib は `use("Agg")` を pyplot import 前に明示・`plt.show()` 禁止（`cost_push_panel.plot_scatter_panel` は show() があり headless でハングする悪い例。`plot_yearly_correlation` の savefig+close パターンに従う）

### 2.2 実行・検証手順（worktree 内・この順で全て成功すること）

```bash
# 0. データ提供（§1.2。worktree には gitignored data が無い）
cp -R /Users/ishidatomonori/Desktop/graduation-thesis/data/raw/. data/raw/
cp -R /Users/ishidatomonori/Desktop/graduation-thesis/data/processed/. data/processed/

# 1. 構文
python3 -m py_compile src/analysis/goods_services_contrast.py

# 2. 初回生成 + golden（__main__ が check_golden を含む）
uv run python -m src.analysis.goods_services_contrast

# 3. 決定論（force 再計算が同値）
uv run python -c "
from src.analysis.goods_services_contrast import compute_contrast, check_golden
import pandas as pd
a = compute_contrast()
b = compute_contrast(force=True)
pd.testing.assert_frame_equal(a.reset_index(drop=True), b.reset_index(drop=True))
check_golden(b); print('deterministic OK')"

# 4. doc 転記の直前にもう一度 force=True で再生成してから §5 の値を抽出する（stale 転記防止）
```

### 2.3 やってはいけないこと（Sonnet 向けガードレール）

1. §3 の分類・§0 の判定規則を変更・追加・削除しない。§4 の突合で公式資料と食い違いが見つかっても**表は変えず**、本設計書末尾に「突合結果」節を追記して食い違い一覧を報告するだけにする（判断は設計者が次セッションで行う）
2. 本体ツリーの `data/` に書き込まない（コピーは本体→worktree の一方向のみ）。worktree 内でも `data/raw/` は変更しない
3. 既存モジュール（cost_push_panel 等）のコードを変更しない（import のみ）
4. doc へ §5 指定以外の文章・数値を書かない。スライド HTML は変更しない
5. §5 の値は CSV から §5 記載のフィルタ条件で抽出して転記し、転記後に §6-3 の突合を実行する（手打ち禁止）
6. 結果が事前診断と方向が違っても実装をやり直さない — §0 の判定規則を適用してそのまま報告（事前登録原則）
7. golden（§6-1）が ±0.005 で合わない場合: §0.1 の4ステップと実装の差分を特定して修正する。golden の期待値・許容差は変更しない

---

## 3. 財/サービス分類テーブル（確定・41カテゴリ全件）

分類の性格: 研究上の**事前定義**（DEC-010 の競争的輸入財除外と同格）。主基準=当該中分類の支出の過半を占める構成が財かサービスか。
（2026-07-06 検証済み: 本表の41キーは panel_cost_push.csv の distinct cpi_mid_name と字面完全一致する。）

| cpi_mid_name | bucket | 根拠 |
|---|---|---|
| 穀類 | goods | 食料品（財） |
| 魚介類 | goods | 同上 |
| 肉類 | goods | 同上 |
| 乳卵類 | goods | 同上 |
| 野菜・海藻 | goods | 同上 |
| 果物 | goods | 同上 |
| 油脂・調味料 | goods | 同上 |
| 菓子類 | goods | 同上 |
| 調理食品 | goods | 中食（財として販売） |
| 飲料 | goods | 財 |
| 酒類 | goods | 財 |
| 外食 | services | 飲食サービス |
| 家賃 | services | 住居サービス（帰属家賃は分析対象外・実支出家賃） |
| 設備修繕・維持 | mixed | 工事サービス＋資材の混在 |
| 電気代 | energy_util | 財（公共料金）・2023-24 激変緩和補助対象 |
| ガス代 | energy_util | 同上 |
| 他の光熱 | energy_util | 灯油等（財・補助対象外） |
| 上下水道料 | services | 公共サービス料金（輸入含有低・価格は行政決定） |
| 家庭用耐久財 | goods | 財 |
| 室内装備品 | goods | 財 |
| 家事用消耗品 | goods | 財 |
| 家事サービス | services | サービス |
| 衣料 | goods | 財（※回帰では競争的輸入財として除外済・本分析にも入らない） |
| 履物類 | goods | 同上 |
| 被服関連サービス | services | クリーニング等 |
| 保健医療用品・器具 | goods | 財 |
| 医薬品・健康保持用摂取品 | goods | 財 |
| 保健医療サービス | services | 診療等（公定価格） |
| 交通 | services | 運賃（サービス） |
| 自動車等関係費 | mixed | ガソリン（財・高IC）＋整備/保険（サービス）の混在 |
| 通信 | services | 通信サービス（政策的価格操作あり・既存 (ii) 仕様で除外対象だが本分析では services に残す） |
| 授業料等 | services | 教育サービス |
| 教科書・学習参考教材 | goods | 財 |
| 補習教育 | services | 教育サービス |
| 教養娯楽用耐久財 | goods | 財 |
| 教養娯楽用品 | goods | 財 |
| 書籍・他の印刷物 | goods | 財 |
| 教養娯楽サービス | services | パック旅行を除くサービス |
| パック旅行費 | services | 旅行サービス |
| 理美容サービス | services | サービス |
| 放送受信料 | services | 公共サービス料金 |

**集計（検算済み・回帰対象39カテゴリ内訳）**: goods=20（表の goods 22 から衣料・履物を除外）/ energy_util=3 / **services=14** / **mixed=2**。20+3+14+2=39 ✓（この内訳は load_panel の assert (3) と §1.3 のバケットサイズに一致していなければならない）

## 4. 分類の官公表突合（実装ステップに含める・変更は不可）

1. **WebSearch** で総務省「2020年基準消費者物価指数」の財・サービス分類の公式資料の URL を探し（検索語例: `消費者物価指数 財・サービス分類 2020年基準 site:stat.go.jp`）、見つかった URL を **WebFetch** で読む（2段階。WebFetch は URL 必須で検索はできない）
2. §3 の表と食い違う割当が見つかった場合: **表を変更せず**、本設計書の末尾に「突合結果」節を追記して食い違い一覧（カテゴリ名・§3 の割当・公式の区分・出典URL）を報告し、実装を継続（S1-S3 は §3 の表のまま）
3. 公式資料に到達できない場合もその旨を突合結果節に記録（実装は止めない）

## 5. doc 反映（アンカー指定・この3箇所のみ）

値の抽出規則（共通）: `goods_services_contrast.csv` から `spec, bucket, metric=='corr', year_or_window ∈ {'2021','2022','2023','2024'}`（ショック期）または `{'2015'..'2019'}`（プラセボ期）で絞った `value` 列の min と max を取り、小数2桁・符号付き（例 `+0.08〜+0.41`）で表記する。

**(a) `docs/research-design.md`** — 「識別の到達点と限界」節の「**最大の脅威は goods-vs-services 交絡**」bullet の直後に、次の1 bullet を追加（[ ] 内は上記抽出規則で置換。分岐は §0 の判定規則で機械的に決定）:

> - **交絡の定量化（財/サービス分解・DEC-022）**: 年次相関コントラストを財のみ／サービスのみに分解すると、ショック期の within-goods 相関は [S1 goods shock min〜max]、within-services は [S1 services shock min〜max]（全39 は +0.08〜+0.41（暦年DEC-023））。[(a) の場合:「全体コントラストの相当部分は財/サービス構成差で説明され、cost-push 固有シグナルとしての解釈はさらに限定される」／(b) の場合:「財内部にも IC 勾配が残り、構成差だけでは説明されない」]。エネルギー公共料金の扱いと 2023-24 補助金の感度は S2/S3（`goods_services_contrast.csv`）。

**(b) `docs/decision-log.md`** — 末尾に `### DEC-022:` を追記（DEC-021 の書式に倣う）。必須項目: 目的（限界の定量化・救済ではない）／事前登録の判定規則（§0）と適用結果（(a) or (b)）／4仕様の相関レンジと β（note 込み）／解釈（§5(a) と同文）／「識別断念（DEC-013/DEC-021補遺）の結論は不変」

**(c) `slides/20260626-seminar2-script.md`** — 補足メモ内の一意アンカー文字列
`で説明する）` を含む一文の末尾を、(a) の場合「で説明する。ただし財/サービス分解では構成差の寄与が大きく、その旨まで含めて誠実に答える — DEC-022）」、(b) の場合「で説明する。財/サービス分解でも財内部に勾配が残る — DEC-022）」に置換

## 6. 受け入れ基準（すべて機械判定）

1. **golden**: `check_golden`（§2.1 の実装そのまま）が pass（S0 × GOLDEN_S0_CORR × ±0.005）
2. **決定論**: §2.2-3 のコマンドが pass（force 再計算が frame 単位で同値）
3. **doc 突合**: doc 反映後、次が全て一致すること —
   `uv run python -c "import pandas as pd; d=pd.read_csv('data/processed/price-indices/goods_services_contrast.csv'); s=d[(d.spec=='S1')&(d.metric=='corr')&(d.year_or_window.isin(['2021','2022','2023','2024']))]; print(s.groupby('bucket')['value'].agg(['min','max']).round(2))"`
   の出力値（表記桁で完全一致）が、docs/research-design.md と docs/decision-log.md に書いた [min〜max] と一致（grep で確認し、結果を実装報告に貼る）
4. **バケットサイズ**: load_panel の assert (3)（goods=20/services=14/energy_util=3/mixed=2）が pass
5. py_compile 通過・`__main__` 実行 exit 0・図が生成される（Agg・show() 無し）
6. §4 の突合結果節が本書末尾に追記されている
7. スクリプト diff の `/review-code light` で blocker/major ゼロ

## 7. 見積り・段取り

- ブランチ: `claude/20260707-goods-services-contrast`（**worktree 使用・main 起点**。EnterWorktree → §1.2 のデータコピー → 実装）
- スクリプト 150-200行・実行数分・全体1-2時間（Sonnet）
- 完了後: §5 反映 → §6 全通過 → commit → main へ --no-ff マージ（マージ前に main 側の未コミット変更と衝突しないか git status 確認）

---

## 付録: v1→v2 の主な変更（/review-basic-design 反映・2026-07-06）

- golden を year:value 対応表（3桁精度）＋導出手法参照＋実 assert コードに具体化（testability blocker / assumption / clarity）
- §3 集計誤りを訂正: services=13→**14**・mixed=3→**2**（scope / coherence が独立に検出）。§1.3 のバケットサイズ・load_panel assert (3) を同期
- (a)/(b) の機械的判定規則を事前登録に追加（scope / risk）
- worktree に gitignored data が無い問題への対処（§1.2 データ提供手順）を追加（risk）
- matplotlib Agg 明示・plt.show() 禁止を必須事項に追加（feasibility が plot_scatter_panel のハングを実測）
- run_panel_regression のコピー分岐を廃止し import 一択に（testability の同一性検証問題を構造的に解消）
- 分類検証を双方向 assert ＋バケットサイズ assert に強化（testability）
- §5 の値抽出フィルタ条件・§6-3 の突合コマンドを明文化（testability / clarity）
- §4 を WebSearch→WebFetch の2段階に修正（feasibility）・DEC-022 書式参照先を明示（specificity）・doc 誤記載時の戻し方を §1.5 に追加（gap D5）・β note にクラスタ数記録を追加（gap D9）

---

## 追記（2026-07-06・設計者）: worktree の基点に関する注意

EnterWorktree の既定は **origin/main 起点**。本設計書を含む一連のコミットが origin へ push される前に実装セッションが worktree を作ると、**worktree 内に本設計書・DEC-021 後の docs が存在しない**。実装開始時に `ls docs/design/` で本書の存在を確認し、無ければ (1) ユーザーに main の push を依頼するか (2) 本体ツリー `/Users/ishidatomonori/Desktop/graduation-thesis/docs/design/` から本書を参照すること（コード・docs の変更コミットは通常どおり worktree ブランチで行い、マージ時に main との差分を確認する）。

---

## 突合結果（§4・実装時点で追記）

**出典**: 総務省統計局「2020年基準消費者物価指数の解説」IV-4 「品目から類への合算表(財・サービス分類)」（`https://www.stat.go.jp/data/cpi/2020/kaisetsu/pdf/4-4.pdf`）。総務省の当該分類は「財」「サービス」の2区分（類2以下でさらに細分）で、本書 §3 が採用する `energy_util`/`mixed` の中間バケットは存在しない。

§3 の表（41カテゴリ）と突合した結果、以下の2件で割当が食い違う。**表は変更していない**（§4 の指示どおり実装は継続）。

| カテゴリ名 | §3 の割当 | 公式の区分 | 出典 |
|---|---|---|---|
| 上下水道料 | services | 財（類2=0218「電気・都市ガス・水道」に電気代・都市ガス代と並んで水道料が計上） | 4-4.pdf p.129 |
| 設備修繕・維持 | mixed | サービス（類2=0228「一般サービス」→類3=0232「他のサービス」→類4=0233「家事関連サービス」に畳替え費・屋根修理費・水道工事費等が全て計上。公式分類上は財の構成要素が別枠に無い） | 4-4.pdf p.130 |

他の39カテゴリ中37件は §3 の割当と公式分類が一致（例: 家賃→民営家賃はサービス、電気代/ガス代→財、通信→運輸・通信関連サービス、家賃の帰属家賃除外の扱いも整合）。

**判断は設計者が次セッションで行う**（本節は報告のみ・§3 の表・S1-S3 の計算には反映していない）。
