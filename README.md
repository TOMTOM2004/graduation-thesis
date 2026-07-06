# 卒業論文 — コストプッシュインフレ下の日本の家計消費の構造解明と政策シミュレーション

外的要因による輸入価格ショック（エネルギー・金属・化学・食料・木材）が日本の実質所得を海外に流出させる構造を定量化し、財の特性（必需品/裁量品）と所得階層の2軸で家計消費への異質な影響を分解した上で、シミュレーションモデルによる政策評価を行う実証経済学研究。

## 中心テーマ

> 外的要因による輸入価格ショックは、日本の実質所得をどのような構造で海外に流出させ、家計の実質消費をどの程度押し下げているか。また、その構造に基づく政策介入はどのような効果をもたらすか。

2022年前後の輸入価格ショック（ウクライナ紛争・ロシア制裁・円安）により、輸入価格上昇分のコストが海外に流出し国内に還流しない → 交易条件の悪化 → 実質所得の海外移転、という問題意識に立つ。現在のインフレに混在するコストプッシュ要因とデマンドプル要因（コロナ財政出動）の識別を試みる。

## 研究質問

| | 問い | 産出物 |
|---|---|---|
| **主問** | 輸入価格ショックは実質所得をどう海外流出させ家計消費をどれだけ押し下げるか。政策介入の効果は | — |
| **副問1** | 実質所得の海外流出は5輸入グループ別にどの規模で、2020年代にどう変化したか | グループ別の所得流出額・構成比・時系列（会計的定量化） |
| **副問2** | 所得流出は財特性・所得階層ごとにどの経路でどれだけ実質消費を下げるか | 費目別の価格転嫁率、所得階層別の実質消費変化 |
| **副問3** | 副問1・2の構造を統合したモデル上で政策介入はどの効果を持つか | パラメータ可変なシミュレーションモデル + 政策シナリオ評価 |

副問2は本研究の独自貢献の核（交易損失の家計レベル・所得階層別への分解は先行研究に空白）。

## 研究設計（積み上げ型3段階）

```
Phase 1（副問1）  IO表の輸入含有率 → 5グループ別の所得流出額を推計（交易損失の会計的定量化）
Phase 2（副問2）  ├─ Step 2a: 財別（必需品/裁量品）のコスト増→価格転嫁→消費変化を分解
                 └─ Step 2b: 所得階層別の実効インフレ逆進性を恒等式で記述（実証的背骨）
Phase 3（副問3）  Phase 1・2の構造を統合したIO価格モデル + マイクロシミュレーション → 政策評価
```

各段階が独立した貢献を持つ。**独自貢献（DEC-015）**: ①交易損失の家計帰着の会計的定量化（識別仮定に非依存）、②逆進的帰着の恒等式ベース記述（頑健・実証的背骨）、③識別限界の方法論的提示、④統合シミュレーションモデル。

### 識別戦略と到達点

輸入含有率（IO表算出）の財間差異を利用してコストプッシュをデマンドプルから識別しようとする（コストプッシュなら輸入含有率の高い財ほど価格上昇が大きい）。

- **主たる falsification 証拠**: IC–ΔCPI 年次相関のコントラスト（ショック期 2021-24 = +0.42〜+0.60 / プラセボ期 2015-19 = ゼロ近傍〜負）
- メイン仕様（競争的輸入財=衣料・履物を除外）のパネルOLS: **β=0.431, p=0.002**（CPI中分類 41カテゴリ × 2021-2024、n=164）
- **重要な限界**: exposure-robust shift-share（グループ別分解）と期間延長（2005遡及）の2手法を実装・検証した結果、**単一マクロ事象からの清浄な cost-push 識別は本設計・データでは不可能**と確認。これを失敗でなく**識別限界の方法論的提示**という貢献に転化（DEC-013/015）。結果は「cost-push と整合的な点推定だが頑健に不確実」と位置づける

詳細は [docs/research-design.md](docs/research-design.md)「識別の到達点と限界」。

## 主要結果（Phase 1-3・実装/検証済）

- **Phase 1（交易損失）**: 5グループ合計の中心推計 2022年 約35兆円 / 2023年 約28兆円 / 2024年 約29兆円。エネルギーが全損失の約67%
- **Phase 2（家計帰着）**: 食料・光熱は必需品かつ高輸入含有率。Q1（最低所得）の実効インフレは Q5 より高い（逆進性・実績CPI）= 2022年 Q1−Q5 格差 **+1.42pp**。原因は Q1 の食料・光熱シェアの高さ
- **Phase 3（政策評価）**: IO価格モデル（コストプッシュ成分）Koyck RMSE 9.744pp。エネルギー補助・食料支援・複合介入の3シナリオを評価。⚠️ 分配/政策の一部数値は再較正中（design-review G-3/C-2/C-4）

> 進捗の最新は [docs/progress.md](docs/progress.md)。設計100% / データ100% / Phase 1-3 100% / 執筆 未着手（全体 約85%）。

## リポジトリ構成

```
src/
  data/         e-Stat / 日銀 CGPI / 貿易統計 等のデータ取得（fetch_*.py, estat_api.py）
  analysis/     輸入含有率・交易損失・コストプッシュ回帰・五分位帰着・Shapiro分解 ほか
  simulation/   シミュレーション（IO価格モデル + マイクロシミュレーション）
  utils/        IO ユーティリティ
notebooks/      Phase別の分析ノート（01_trade_loss 〜 04_phase3_simulation）
docs/           研究設計・分析計画・意思決定ログ・文献レビュー（下記）
slides/         ゼミ発表スライド・スクリプト
tasks/          検証・再現用スクリプト（_an2_*, _phase3_* 等）
data/           raw / processed（実体は .gitignore・構造のみ .gitkeep で管理）
```

## ドキュメント

起点は [docs/INDEX.md](docs/INDEX.md)。

- [docs/overview.md](docs/overview.md) — テーマ・研究質問（主問＋副問1〜3）・スコープ
- [docs/research-design.md](docs/research-design.md) — 研究設計・識別戦略・推定結果・識別の限界・シミュレーションモデル
- [docs/analysis-plan.md](docs/analysis-plan.md) — 分析フロー・Phase別の仮説と推定対象
- [docs/decision-log.md](docs/decision-log.md) — 意思決定ログ（DEC-001〜）
- [docs/progress.md](docs/progress.md) — 進捗ダッシュボード・主要結果サマリー
- [docs/literature/](docs/literature/) — 先行研究（論文サマリー・マトリクス・検索ログ）

## データ

主要ソース: 産業連関表（総務省・2020年表）/ 企業物価指数 輸入物価（日銀 CGPI）/ 貿易統計（財務省・e-Stat）/ 家計調査・全国家計構造調査（総務省）/ 消費者物価指数（総務省）。

分析期間: プラセボ期 2015-2019 / 主分析（ショック期）2021-2024 / 2020 は CGPI 基準年のため回帰から除外。

**raw / processed データは `.gitignore` 済**（容量が大きいため非追跡。`data/raw/`・`data/processed/` の構造のみ `.gitkeep` で管理）。取得は `src/data/fetch_*.py` で再現する。

## セットアップ

Python 3.11+。主要依存は pandas / numpy / statsmodels / linearmodels（クラスタSE付きパネルOLS）/ matplotlib（japanize-matplotlib）。

```bash
pip install -e .          # 依存は pyproject.toml
pip install -e ".[dev]"   # pytest / ruff も入れる場合
```

e-Stat API キー等は `.env`（`.gitignore` 済）で管理。

## 再現手順（Reproducibility）

① 依存関係の固定（`uv.lock`）:

```bash
uv sync
```

② データ取得。e-Stat 系は API キーが必要（`.env` に設定）:

```bash
python -m src.data.fetch_io_table
python -m src.data.fetch_cpi
python -m src.data.fetch_household
python -m src.data.fetch_trade_stats
python -m src.data.fetch_import_prices
python -m src.data.fetch_worldbank    # World Bank（crosscountry / industry-structure）。デフォルトは既存 raw を保護し skip、再取得は --force
```

③ 分析パイプラインの実行順（`src/analysis/*.py` の import 依存に基づく）:

```bash
python -m src.analysis.import_content      # IO表 → セクター/グループ別輸入含有率（他の分析の前提）
python -m src.analysis.trade_loss          # Phase 1: 交易損失（import_content に依存）
python -m src.analysis.bridge_matrix       # 家計調査カテゴリ ⇄ IOセクターのブリッジ
python -m src.analysis.bridge_matrix_mid   # CPI中分類 ⇄ IOセクターのブリッジ（cost_push_panel / io_price_model が依存）
python -m src.analysis.cost_push_id        # bridge_matrix に依存（quintile_impact の前提）
python -m src.analysis.cost_push_panel     # bridge_matrix_mid に依存。cost_push_panel_results.csv を出力
                                            # → io_price_model の BETA_EMPIRICAL がこの CSV を読むため、必ず先に実行すること
python -m src.analysis.quintile_impact     # bridge_matrix + cost_push_id に依存（Phase 2 家計帰着）
python -m src.analysis.shapiro_decomp      # Shapiro分解（e-Stat 直接取得、他モジュールと独立）
python -m src.analysis.shapiro_quintile    # shapiro_decomp に依存
python -m src.analysis.io_price_model      # import_content + bridge_matrix_mid + cost_push_panel_results.csv に依存（Phase 3 IO価格モデル）
python -m src.analysis.policy_simulation   # quintile_impact + io_price_model に依存（Phase 3 政策シナリオ評価）
```

④ キャッシュの無効化: 各 `compute_*` 系関数は `data/processed/` 配下に CSV キャッシュを持つ。再計算したい場合は `force=True` を渡す（例: `compute_trade_loss(force=True)`）。呼び出し先の `compute_*` にも force が伝播する（同一モジュール内のみ）。

⑤ R 依存（AKM / ShiftShareSE）: `tasks/_a4_akm.R` ・ `tasks/_a4_akm2.R` は R + `ShiftShareSE` パッケージが必要（インストール手順は各ファイル冒頭のコメント参照）。入力 CSV（`_akm_cross.csv`）は `tasks/_a4_akm_prep.py` で再生成できる。

## ゼミ発表スケジュール

| 回 | 時期 | 内容 |
|---|---|---|
| 第1回 | 2026-05下旬 | テーマとプランの発表 |
| 第2回 | 2026-07中旬 | 進捗発表① |
| 第3回 | 未定 | 進捗発表② |
