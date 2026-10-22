# ITEM-025 データ鮮度監査（2026-10-22）

取得: 2026-10-22 11:36–11:50 UTC（日本時間 20:36–）／保存先 `/private/tmp/ic-fresh-20261022/`（repo外・`data/raw` 無変更）／e-Stat は APIキーを `.env` から読むのみ（本書に鍵・appId付URLなし）。分類 A=差なし／B=新期間追加のみ／C=既存期間の改訂／D=方法論・基準変更。比較は snapshot（`data/raw`）対 公開側。

## 判定表

| # | ソース | 公開側 公表/更新日 | 手元最新 | 公開側最新 | 分類 | 表示値への影響 |
|---|---|---|---|---|---|---|
| 1 | CPI 2020基準（e-Stat 0003427113） | OPEN 2026-09-18 | 2025-12 | 2026-08 | **A**（2015–2025の重複 100,000セル全一致・費目名一致）＋**B**（2026-01..08、FY2025集計） | なし。Q1-Q5 +2.01/2.06/2.45/3.36pp 据え置き |
| 2 | CPI 2025基準（e-Stat 0004052037） | OPEN 2026-10-02／**UPDATED 2026-10-22（当日更新）** | 無し | 2026-08（全国）、1970年まで遡及接続 | **D**（基準・ウェイト・品目改定：品目 797 vs 790、名称変更49、新設19・廃止12） | 総合の新/旧比 0.8933–0.8935 で一定。41中分類の「対2020累積」差は最大0.057pp（2021–25）、10大費目≤0.05pp。gap への影響は推定<0.01pp（再計算は未実施＝**未検証**）。生鮮野菜の2025値のみ品目差最大4.9pp（キャベツ）・ウェイト小 |
| 3 | 家計調査 用途分類 五分位（0002070005） | OPEN 2026-02-06／UPDATED 2026-05-19 | 2025 | 2025 | **A**（25,818/25,818 セル一致、五分位名・費目名一致） | なし。※品目分類DB 0004023607 は未取得・手元snapshotで未使用＝**未検証（対象外）** |
| 4 | BOJ 輸入CGPI（cgpi_m_jp.zip）＋cgpilink1.csv | 2026-10-13 掲載（2026-09月分）／定期遡及訂正 2026-09-11 | 2026-03 | 2026-09 | **C**（2025-01..12 のみ改訂）＋**B**（2026-04..09）。cgpilink1.csv は SHA 一致=**A**、2015–2024 は差0 | **2025中心 24.762→24.712兆（表示24.8→24.7）**、net 19.112→19.045（19.1→19.0）、上限30.233→30.182（30.2不変）。2022–24 不変 |
| 5 | Känzig 原油供給ニュース | GitHub最終 commit 2026-06-05（shocks到2025M12）／06-09 は VARdata.xlsx のみ | 2025M12 | 2025M12 | **A**（xlsx SHA 一致） | なし。LP gap p=0.035 据え置き |
| 6 | AI-GPR bilateral | Last-Modified 2026-10-19 | 2026-06 | 2026-09 | Russia\|Ukraine の 1960–2025 は **A**。2026-01/03/06 に微小改訂（C相当だが窓外）、2026-07..09 は **B** | なし（war_news_lp 標本は〜2025-12）。全列192セル改訂は全て2026年 |
| 7 | 名目GDP（内閣府 QE 2026Q2 2次速報） | 2026-09-08 | コード内ハードコード 2022: 561,000 | 暦年 2022–2025 あり | **C/D（版差＋分母バグ）** | 下記。**s6 の6.3%・4.4%が現行値で変わる** |
| 8 | 2020 IO表（108部門 生産者/購入者価格） | e-Stat。soumu に2025-07-11 再集計の記載 | 2020表 | 2020表（2025表なし・予告なし） | **A**（両xlsx SHA 一致） | なし |

2025基準 CGPI: 基本方針公表 2026-06-03（意見募集〜08-28）のみ。初回公表日は**未確認**。現時点で 2020基準 CGPI が継続（2026-09月分まで）。

## 証跡（SHA-256 ほか）
- BOJ zip: 手元 `a7ac74aacac232e36d076891384aacccc6550a91ca7602af8ff00b21ecf33273` ／ 公開 `7ad65cba26372fef88401390ce7f4055afae0fea1f6d0479a64e7738a98a1a43`（CSV 78列→84列）。重複 2020-01..2025-12 の全3042系列で変更 7,433セル（全て2025年）、利用12系列で107セル。
- cgpilink1.csv: `cf38d934941925c001fbdf55f6f659c03b10699155a1bf8ba89e29fd9400f4e1`（一致）
- AI-GPR: 手元 `e542e4b8bb64159e1f68f31f0226852e89db85b590d20592da992fc0eab05180` ／ 公開 `50dce47fc524bd7fe0b0bba1e612e425694f90fb99d23250819e486a683d7165`
- Känzig xlsx: `8aa80042f84071ea310b3c2f604b177aed57ee7575e6a18aed5b8ad52ec353de`（手元=公開。git blob d5f7829b）
- IO: producer `8115f7f6…5607`、purchaser `730d575c…a8f6e`（手元=公開）
- GDP CSV `gaku-mcy2622.csv`: `670fd1130075925c8e015e1c4da6f01f1d90d9d77fd7c182615e16146cb2cbe9`
- e-Stat JSON（取得物）: cpi2020_all `4894cce8…ee4c`、cpi2025_nat_idx `8b3e9d3730112f5d77f29f2ffc2a0a261a6183bdf5bb30bfeadb94edda40e3db`、hh_use_quintile `00207392…dd7f`（先頭一致で記録、全長は /private/tmp）

## 差分詳細

### 7. GDP（暦年名目・10億円・QE2026Q2 2次速報）
| 年 | 現行値 | コード/表示の分母 | 交易損失(中心) | 表示 | 現行年別GDP比 |
|---|---|---|---|---|---|
| 2022 | 584,501.3 | 561,000 | 35.275 | 6.3% | **6.04%** |
| 2023 | 616,659.4 | 561,000 | 28.350 | 5.1%（内部） | 4.60% |
| 2024 | 636,893.3 | 561,000 | 29.125 | 5.2%（内部） | 4.57% |
| 2025 | 666,440.7 | 561,000 | 24.762→24.712 | 4.4% | **3.71%** |

(i) 版差: 2022年が 561→584.5兆。(ii) 表示の2023–25比は**全年に2022年GDPを分母**に使用（5.05/5.19/4.41%が表示値と一致）＝「名目GDP比」ではなく「2022年GDP固定比」。**基準年は検証済み＝2020年(令和2年)基準**（ESRI「2026年」一覧 `toukei_2026.html`〔取得 2026-10-22・SHA-256 `60afcab091328fb58dab483ad5f6f82a8a3cc71c035c34522d7b91572dae1d97`、保存先 /private/tmp/ic-stage2-dl〕76行目: 「1994年1-3月期～2026年4-6月期2次速報値 （2020年（令和2年）基準）」＜2026年9月8日公表＞）。なお統計表一覧ページ `gdemenuja.html` 自体には基準年表記なし。旧コード値 561,000 の取得時点の版・基準年は記録なし（版差＝C は確定、基準改定＝D の有無は旧版不明のため判別不能）。主因はコード側の分母バグ（全年に2022年GDPを流用）。

### 4. BOJ 改訂（利用12系列、2025年、old→new）
| series | month | old | new |
|---|---|---|---|
| food* | 202501 | 172.8 | 172.9 |
| food* | 202502 | 171.7 | 171.6 |
| food* | 202503 | 171.8 | 171.6 |
| food* | 202504 | 169.0 | 168.9 |
| food* | 202505 | 169.8 | 169.6 |
| food* | 202506 | 167.3 | 167.1 |
| food* | 202509 | 167.4 | 167.3 |
| food* | 202510 | 169.9 | 169.8 |
| food* | 202511 | 174.4 | 174.3 |
| textiles | 202501 | 131.8 | 132.0 |
| textiles | 202502 | 129.4 | 129.7 |
| textiles | 202503 | 128.2 | 128.8 |
| textiles | 202504 | 126.5 | 126.7 |
| textiles | 202505 | 126.5 | 126.8 |
| textiles | 202506 | 126.9 | 127.5 |
| textiles | 202507 | 128.0 | 128.1 |
| textiles | 202508 | 128.4 | 128.2 |
| textiles | 202509 | 128.2 | 129.2 |
| textiles | 202510 | 130.0 | 130.5 |
| textiles | 202511 | 131.5 | 132.1 |
| textiles | 202512 | 132.1 | 132.8 |
| metals* | 202502 | 171.8 | 171.7 |
| metals* | 202503 | 171.5 | 171.4 |
| metals* | 202504 | 167.9 | 167.7 |
| metals* | 202505 | 168.8 | 168.6 |
| metals* | 202506 | 171.3 | 171.2 |
| metals* | 202507 | 177.6 | 177.5 |
| metals* | 202508 | 177.0 | 176.9 |
| metals* | 202510 | 189.3 | 189.2 |
| wood* | 202503 | 155.4 | 155.3 |
| wood* | 202504 | 152.6 | 152.4 |
| wood* | 202505 | 153.2 | 153.1 |
| wood* | 202506 | 154.4 | 154.3 |
| wood* | 202508 | 159.2 | 159.3 |
| wood* | 202509 | 160.1 | 160.5 |
| wood* | 202510 | 163.0 | 163.4 |
| wood* | 202511 | 167.2 | 167.6 |
| wood* | 202512 | 168.9 | 169.4 |
| energy* | 202501 | 245.3 | 245.2 |
| energy* | 202502 | 241.5 | 241.0 |
| energy* | 202503 | 233.0 | 232.4 |
| energy* | 202504 | 220.8 | 220.2 |
| energy* | 202505 | 211.9 | 211.3 |
| energy* | 202506 | 201.7 | 200.7 |
| energy* | 202507 | 207.4 | 207.5 |
| energy* | 202509 | 209.4 | 209.3 |
| energy* | 202510 | 215.0 | 215.1 |
| energy* | 202512 | 214.3 | 214.4 |
| chemicals* | 202501 | 115.9 | 115.8 |
| chemicals* | 202503 | 113.8 | 113.6 |
| chemicals* | 202504 | 111.2 | 111.1 |
| chemicals* | 202505 | 110.7 | 111.0 |
| chemicals* | 202507 | 109.5 | 109.4 |
| chemicals* | 202509 | 109.9 | 109.8 |
| chemicals* | 202511 | 112.4 | 112.5 |
| chemicals* | 202512 | 112.8 | 112.6 |
| gen_mach | 202502 | 140.5 | 140.6 |
| gen_mach | 202506 | 140.2 | 139.0 |
| gen_mach | 202507 | 143.7 | 142.9 |
| gen_mach | 202508 | 146.2 | 145.4 |
| gen_mach | 202509 | 146.6 | 145.8 |
| gen_mach | 202510 | 148.8 | 148.0 |
| gen_mach | 202511 | 151.1 | 150.3 |
| gen_mach | 202512 | 149.7 | 148.9 |
| electronics | 202501 | 134.6 | 134.7 |
| electronics | 202502 | 129.6 | 129.7 |
| electronics | 202503 | 127.8 | 127.9 |
| electronics | 202506 | 124.9 | 124.8 |
| electronics | 202507 | 126.6 | 126.3 |
| electronics | 202510 | 130.0 | 129.9 |
| electronics | 202511 | 133.3 | 133.2 |
| electronics | 202512 | 136.5 | 136.4 |
| transport | 202501 | 142.4 | 142.5 |
| transport | 202502 | 140.1 | 140.2 |
| transport | 202503 | 139.5 | 139.1 |
| transport | 202504 | 137.6 | 137.2 |
| transport | 202505 | 137.1 | 136.6 |
| transport | 202506 | 136.6 | 136.0 |
| transport | 202507 | 140.4 | 139.8 |
| transport | 202508 | 141.9 | 141.5 |
| transport | 202509 | 141.7 | 141.8 |
| transport | 202510 | 143.9 | 144.2 |
| transport | 202511 | 147.2 | 147.5 |
| transport | 202512 | 147.3 | 147.6 |
| other | 202503 | 143.9 | 143.7 |
| other | 202504 | 140.9 | 140.8 |
| other | 202505 | 141.7 | 141.6 |
| other | 202506 | 141.1 | 141.0 |
| other | 202507 | 142.9 | 142.8 |
| other | 202508 | 143.2 | 143.1 |
| other | 202509 | 143.6 | 143.5 |
| other | 202510 | 145.8 | 145.6 |
| other | 202511 | 148.5 | 148.4 |
| other | 202512 | 149.5 | 149.3 |
| total | 202502 | 162.8 | 162.7 |
| total | 202503 | 160.2 | 160.1 |
| total | 202504 | 155.5 | 155.3 |
| total | 202505 | 153.9 | 153.7 |
| total | 202506 | 151.6 | 151.2 |
| total | 202507 | 154.7 | 154.5 |
| total | 202508 | 155.3 | 155.2 |
| total | 202511 | 162.0 | 161.9 |
| domestic* | 202508 | 126.4 | 126.5 |
| domestic* | 202509 | 127.0 | 127.1 |
| domestic* | 202510 | 127.6 | 127.7 |
| domestic* | 202511 | 128.0 | 128.1 |
| domestic* | 202512 | 128.1 | 128.2 |

`*`=交易損失で使用する5グループ＋国内総平均（49セル）。年平均（旧→新）: energy 218.617→218.350／metals 179.392→179.308／chemicals 111.692→111.658／food 170.567→170.483／wood 158.992→159.100／domestic 126.733→126.775。

### 6. AI-GPR Russia|Ukraine（改訂3か月、全て窓外）
| 月 | old | new |
|---|---|---|
| 2026-01 | 14.6552 | 14.6522 |
| 2026-03 | 7.4036 | 7.4039 |
| 2026-06 | 9.8580 | 9.8106 |

新月 2026-07/08/09 = 19.6134／16.0895／21.5966（B）。

### 1/2. CPI 補足
- 手元 `cpi_category_2015_2025.csv` は**ちょうど100,000行＝APIページ上限で切断**: 790費目中116費目が欠落、43費目が部分欠落（品目入替の自然欠損と区別）。分析で使うコード（最大 `0177`、41中分類）は全て存在し影響なし。再取得時はページング必須（本監査は NEXT_KEY で全件取得）。他の手元CPI（headline_major / category_2005_2024 tab1 / total_food）も公開側と全セル一致。
- 時間コード: `YYYY000000`=暦年、`YYYY100000`=年度。手元に 2025年度(`2025100000`)なし（暦年統一のため未使用）。
- 2020基準 e-Stat 表は 2026-08 まで併存更新。2026-09月分（全国）以降も継続するかは**未確認**。2025基準表は当日更新のため、再取得すると差が出る可能性。
- 参考（新規月）: 輸入物価 energy は 2026-03 226.5→04 289.2→05 314.1→06 317.1→07 316.8→09 300.5（2020=100）。2026年は9か月のため不完全年ガード（<12）で除外される。

### 8. 注記
soumu 頁の「2025-07-11 再集計」記載があるが、108部門xlsx はバイト一致。

## 表示主張への影響（第3回/第4回）
- 変わる: 「2025年 24.8兆」→24.7兆（C、再実行で確定）、net 19.1→19.0（参考値）、GDP比 6.3%（2022）→6.0%、4.4%（2025）→3.7%（現行GDP年別）。
- 変わらない/据え置き: Q1-Q5 gap、β=0.633、LP p=0.035、Shapiro、戦争ニュース比較、2022–2024 の兆円値、IO固定。
- Stage 2 で検証済み: β・Koyck RMSE・b1 は不変（下記「Stage 2 実施結果」）。未検証は次の点のみ:2025基準CPI下の gap（推定<0.01pp）。

## 判断事項 D1–D5（Codex向け）
- **D1** CPI: 2020基準＋2019ウェイト固定を維持し、2025基準は限界節の注記のみ（推奨）。根拠: 接続差≤0.06pp、基準切替は方法論変更。
- **D2** BOJ 2025改訂: 表示精度を跨ぐ（24.8→24.7）ため「記録のみ」不可。2025依存の下流を新vintageで再実行→表示値更新を推奨。AI-GPR改訂は無視可。
- **D3** 新vintageの保存: `/private/tmp` 維持が既定。dated copy を `data/raw` に足すか／worktree の `data/raw` をimmutability対象とみなすかはCodex裁定。
- **D4** 10/23 までに未完の場合: 数値据え置き＋Q&A に「データは2026-07取得版（BOJ 2025年値は2026-09に定期遡及訂正）」の1行。
- **D5** 波及範囲: GDP分母は最大。s6 6.3%／4.4%、両原稿、AGENTS.md・project CLAUDE.md の「GDP比6.3%/4.4%」、DEC-012、paper。分母を年別GDPに直す（推奨）か「2022年GDP固定比」と明記するか。両デッキ4ファイル同時更新。

## 再実行コマンド／最小適応（Stage 1 時点の提案。Stage 2 で (a) 方式を実装・実施済み）
- `trade_loss.py` は `CGPI_PATH`＝`data/raw/boj-cgpi/import_prices_extracted.csv`、`fetch_import_prices.py` は `RAW_DIR` 固定でキャッシュ優先→そのままでは新データを読めない。
  - (a) `RAW_DIR`/`CGPI_PATH` を環境変数（例 `IC_RAW_OVERRIDE`）で上書き可能にする小変更（テスト先行）。出力は一時パスか `data/processed`。
  - (b) コード無変更：worktree の `data/raw` に `/private/tmp/ic-fresh-20261022/boj/{cgpi_m_jp.zip,cgpilink1.csv}` を置き `import_prices_extracted.csv`/`domestic_cgpi.csv` を未作成にして `python -m src.analysis.trade_loss`（force=True）。※worktree内 `data/raw` がimmutability規則の対象かはCodex裁定。
  - 検算済み（読み取りのみ）: 2025中心 24.712／net 19.045／上限 30.182（`scripts/recalc_tl.py`、/private/tmp）。
- GDP: `GDP_BN_BY_YEAR = {2022: 584_501.3, 2023: 616_659.4, 2024: 636_893.3, 2025: 666_440.7}` と `trade_loss.py:414` の `GDP_BN_BY_YEAR[2022]` を行ごとの年別参照に変更（コード変更）。
- 下流（2025 CGPI 依存）: `python -m src.analysis.cost_push_panel`（force）、`quintile_impact`、`io_price_model`／`policy_simulation`、`oil_lp_prep`→（log_import_energy のみ）。`oil_lp`/`war_news_lp` は CPI・Känzig・AI-GPR が窓内不変のため、import_energy アウトカム以外は再実行不要。
- 比較スクリプトは `/private/tmp/ic-fresh-20261022/scripts/`（cmp_boj_gpr.py, cmp_cpi.py, cmp_cpi25.py, cmp_hh.py, recalc_tl.py, estat_fetch.py）。実行は `.venv/bin/python -I <script> <repo> <tmp>`。

## Stage 2 実施結果（2026-10-22・コミット前・スライド未編集）

Codex 裁定 D1–D3・D5 を実装。**D1**: 2020基準CPI＋2019固定シェアを正準維持（2025基準CPIは未使用）。**D2**: BOJ 2026-10-13 版（2025年改訂値）で依存出力を再実行。**D3**: `data/raw` 不変（実行前後で 49 ファイルの SHA-256 一致を確認）。新 vintage は `data/source-vintages/boj-cgpi-20261013/`（`MANIFEST.md`・`SHA256SUMS`・応答ヘッダ付き）。**D5**: 年別GDP分母に是正。

### 実装
- `src/data/fetch_import_prices.py`: `cgpi_dir()` / `cgpi_import_path()`（環境変数 `CGPI_SOURCE_DIR`、呼出時解決、未設定＝従来の `data/raw/boj-cgpi`）。設定時は欠落ファイルでダウンロードせず `FileNotFoundError`。
- 利用側（`trade_loss`・`cost_push_panel`・`io_price_model`・`oil_lp_prep`）は `cgpi_import_path()` 経由。`trade_loss.py`: `GDP_BN_BY_YEAR`={2022: 584,501.3, 2023: 616,659.4, 2024: 636,893.3, 2025: 666,440.7}（`gaku-mcy2622.csv` と照合済み）、`add_gdp_pct()` を追加し `trade_loss_total.csv` に `gdp_pct` 列（未登録年は NaN）。
- テスト: `tests/test_cgpi_source_override.py`（8件、実装前に全件 red を確認 → green）。全 tests 31 passed（キャッシュ旧形式の `gdp_pct` 付与テストを追加。`__main__` の GDP比表示は GDP未登録年〔2015–2021〕で NaN になる）。

### 変化した出力（`data/processed`、旧→新）
| 出力 | 変化 |
|---|---|
| trade-loss/trade_loss_total.csv | 2025 中心 24.7625→**24.7123**兆、net 19.1122→**19.0447**、上限 30.2325→**30.1824**。2015–2024 不変（\|d\|<1e-12）。`gdp_pct` 列追加（2022 6.0351／2023 4.5974／2024 4.5731／2025 3.7081） |
| trade-loss/trade_loss_by_group.csv | 2025 の5グループ（energy 12,209.86→12,173.72 bn 等）と domestic_cgpi 2025 のみ |
| trade-loss/annual_price_index.csv | 2025 の5セル（energy 218.62→218.35 ほか） |
| trade-loss/trade_loss_baseline_sensitivity_2022.csv | 新規生成（従来ファイル無し）。2015-19中心 35.28兆・**GDP比 6.0%**（旧分母 561,000 では 6.3%） |
| oil-lp/monthly_panel.csv | `log_import_energy`/`dlog_import_energy` の 2025 年 10 か月＋差分連動（22セル、max\|d\|=0.0055）。他列は完全一致。2026 の新月は CPI 範囲（〜2025-12）で切り落とし |

### 変化なし（再実行して bit 一致を確認、\|d\|<1e-12）
`panel_cost_push.csv`（パネルは 2015–19・2021–24 のみ＝2025 を含まない）、`cost_push_panel_results.csv`（β(iii)=0.3733/p=0.0891 等）、`cost_push_ic_definition_sensitivity.csv`（**β=0.6328, p=0.0009**）、`yearly_correlation_*`、`io_price_model_output.csv`／`_validation.csv`（**Koyck RMSE 10.3984→10.3984pp**＝競争的輸入財除外・2021–24）、`policy_scenario_results.csv`／`policy_comparison_2022.csv`／`sensitivity_delta.csv`（**b1: 1.560pp／44.7%／57.8%**、全 microsim）、`quintile_*`（実績CPIのみ依存）。Koyck は後ろ向きで IO 年は 2015–19・2021–24、2025 は窓外＝構成上不変。
- `oil_lp_prep` の再実行で `prep_checks.txt` も再生成（保存パスの行のみ差分）。年次クロスチェック max\|diff\|=0.0035pp。

### LP（repo 未更新・一時出力で影響確認）
`oil_lp` を `/private/tmp/ic-stage2-lp-out` へ実行（repo の `irf_results.csv` は未上書き）。変化は `log_import_energy`[full] の 25/325 行のみ（\|Δβ\|max=0.0196。例 h=9: 5.164→5.161, p_perm 0.551→0.554）。他 outcome（headline gap p=0.035 を含む）は完全一致、`historical_decomposition.csv` 一致。repo の `irf_results.csv`／`lp_summary.txt` は旧 import_energy 値のまま（要裁定）。

### 未実行／対象外
`cost_push_panel` の初回 `__main__` は `MPLBACKEND` 未設定（GUIバックエンド）で停止。`MPLBACKEND=Agg` で再実行し完走、結果CSV/tex は不変（`cost_push_panel_results.tex`・`policy_comparison_2022/2024.tex` はバイト一致）、図2枚のみ再生成。`fx_decomposition`（`RAW_DIR` を直接書込むため非実行・表示値に未使用）、`energy_chain`（2020→2022 のみ参照）、2025基準CPI下の gap（未実施）。

### 再現コマンド
```
# pytest は .venv に無い。homebrew py3.11 の pytest/pluggy/iniconfig を /private/tmp/ic-stage2-pytest に symlink して利用
PYTHONPATH=/private/tmp/ic-stage2-pytest .venv/bin/python -m pytest tests -q -p no:cacheprovider
export CGPI_SOURCE_DIR=$PWD/data/source-vintages/boj-cgpi-20261013 PYTHONPATH=$PWD MPLBACKEND=Agg
.venv/bin/python -c "from src.analysis import trade_loss as t; t.compute_total_trade_loss(force=True); t.compute_baseline_sensitivity(2022, force=True)"
.venv/bin/python -c "from src.analysis.cost_push_panel import build_panel_dataset as b; b(force=True)"
.venv/bin/python -m src.analysis.cost_push_panel
.venv/bin/python -m src.analysis.cost_push_ic_sensitivity
.venv/bin/python /private/tmp/ic-stage2-scripts/rerun_io_policy.py   # io_price_model(force)+validation+policy_simulation(force)+sensitivity_delta(force)
.venv/bin/python -m src.analysis.oil_lp_prep
```
スクリプト群・旧版 `data/processed` のバックアップ（`/private/tmp/ic-stage2-backup/`）・raw SHA 一覧（`raw-before.sha256`）はすべて repo 外。

### Codex への裁定依頼
- **J1** `data/source-vintages/` は `.gitignore` 対象外（zip＋CSV 約 1.4MB が追跡される）。追跡する／ignore するか。
- **J2** provenance: `CGPI_SOURCE_DIR` 無指定の `force=True` 再実行は `data/processed` を旧 vintage（data/raw）へ静かに戻す。`data/processed` に vintage スタンプを置く／運用で env を必須化／既定を新 vintage に切替、のいずれか。
- **J3** `oil-lp/` が不整合: `monthly_panel.csv` は新 vintage、`irf_results.csv`・`lp_summary.txt` は旧 import_energy 値。(a) `/private/tmp/ic-stage2-lp-out/{irf_results.csv,lp_summary.txt}` を反映（25/325 行変化・gap p=0.035 不変）か (b) `monthly_panel.csv` をバックアップから戻す。`war_news_lp` は同 panel を読むが import_energy 列を使わず、他列は完全一致のため影響なし。
- **J4** GDP 2015–2021 は同 CSV にあるが、指示どおり 2022–2025 のみ登録（他年は NaN）。拡張するか。
- **J5** `gaku-mcy2622.csv` 原本は /private/tmp のみ（SHA は記録済み）。`data/source-vintages/cao-gdp-qe262-2/` にミラーするか。
- **J6** `fx_decomposition` は `RAW_DIR` 固定で `import_prices_both_bases.csv` を `data/raw` へ書く設計。`CGPI_SOURCE_DIR` 下で実行すると vintage を読んで raw に書くため未実行・未修正。
- **J7** 表示値の反映範囲（スライド編集前の確認）: 2025 中心 24.8→24.7兆、net 19.1→19.0、GDP比 2022 6.3→6.0%・2025 4.4→3.7%、2023/2024 の内部値は 5.1→4.6%・5.2→4.6%。他の表示値（β=0.633・Koyck RMSE 10.40・b1 1.56pp/44.7%/57.8%・Q1–Q5 gap）は不変。

## Stage 3 実施結果（2026-10-22・コミット前）

Codex 裁定 J1–J7 を実施。記録は DEC-028。

| 裁定 | 実施 |
|---|---|
| J1 | `data/source-vintages/` を追跡対象（.gitignore 対象外のまま。boj-cgpi-20261013 と cao-gdp-qe262-2） |
| J2 | `fetch_import_prices.py` の既定を `data/source-vintages/boj-cgpi-20261013` に切替（`VINTAGE_DIR`）。旧 `data/raw/boj-cgpi` は `CGPI_SOURCE_DIR` 明示時のみ。欠落ファイルは常に `FileNotFoundError`（ダウンロードしない）。`tests/test_cgpi_source_override.py` を先に更新し red（3件）→ green。既存の override テストは維持。全 tests **34 passed** |
| J3 | 既定vintageで `oil_lp_prep`（panel は SHA `c3736123…` で Stage 2 と同一）→ `oil_lp` を再実行し `data/processed/oil-lp/` を再生成。`irf_results.csv`／`lp_summary.txt` は `/private/tmp/ic-stage2-lp-out/` と完全一致。旧版との差は `log_import_energy` 25/325行のみ、`historical_decomposition.csv` は一致、headline gap の global p=0.035 不変 |
| J4 | GDP は2022–2025のみ登録、他年 NaN（`add_gdp_pct`） |
| J5 | `data/source-vintages/cao-gdp-qe262-2/`（`gaku-mcy2622.csv`・応答ヘッダ・ESRI一覧・`MANIFEST.md`・`SHA256SUMS`・URL）。CSV の2022–2025値とコード定数の一致を確認 |
| J6 | `fx_decomposition` は未実行・未編集。`RAW_DIR` 固定で `data/raw` へ書く設計のため、新vintageでの再実行には別設計が必要（表示値に未使用） |
| J7 | 第3回・第4回の HTML と MD 原稿を同期更新（下記） |

### デッキ・原稿の変更（4ファイル）
| 項目 | 旧→新 | 箇所 |
|---|---|---|
| 2025年交易損失 | 24.8→24.7兆円（`data-count`・表示） | 両HTML s6、両原稿 |
| 棒幅 2025年 | other 70.2→70.1%、energy 34.6→34.5% | 両HTML s6 |
| GDP比（2022） | 6.3→6.0%（stat-cell `data-count`、第3回の表「約35兆円」） | 両HTML s6、s10表、両原稿 |
| GDP比（2025） | 4.4→3.7%（s6 note、原稿本文・Q&A） | 第3回HTML・原稿 |
| 食料30%補填 | 12.9→13.0%（`data-count`・表示）、バー幅87.1→87.0% | 両HTML b1 |

第3回の従来レビュー事項: s11「非有意性（β）：これも頑健」→「βの識別限界」（通常p=0.0009で有意だが財・サービス交絡で因果識別不可）、s7c／s9／原稿の「独立した（な）証拠」→相補的（互いに独立とは仮定しない）、s9「GDP集計の消費減少」→固定バスケット生活費負担、表紙日付→2026年10月23日、表紙・`<title>` の「家計消費への異質な影響」→「家計の生活費負担への異質な帰着」（第4回表紙・原稿にも同期）。第4回 s11 placeholder は無編集。

### 検証
- tests 34 passed。`data/raw` 49ファイルのSHAは Stage 2 実行前と一致（`raw-before.sha256` と突合）
- `check_slides.py`: 第4回 OK、第3回 エラー0（警告W2×2は変更前から存在）
- 実レンダ（Chrome・1280×720・全フラグメント表示）: 第3回19枚／第4回16枚で境界超過0・未表示frag 0・カウントアップ着地一致（`data-count`の書式化値＝表示値）・棒幅の実測と `--w` が一致
- 再生成成果物（`trade_loss_total.csv`: 2025 24.712／net 19.045／GDP比 6.035・4.597・4.573・3.708）と表示値を突合

### 再現手順の更新
`CGPI_SOURCE_DIR` の指定は不要（既定が新vintage）。旧版の再現のみ `CGPI_SOURCE_DIR=$PWD/data/raw/boj-cgpi`。
