"""
Phase 1 Step 1-3: Trade loss (terms of trade loss) estimation.

Three estimates are computed (DEC-012):

(C) Baseline-corrected — CENTRAL estimate（中心推計）:
    ΔTL_g(t) = M_g(2020) × (P_import_g(t) − P_ref_g) / 100
    P_ref_g = グループ別の参照期（2015-2019）平均輸入物価。
    2020年はCOVIDで輸入物価が異常な底値（特にエネルギー: 2020=100 に対し
    2015-19平均=128.5）。2020比だと「ショック」に「COVID価格暴落からの回復」が
    混入し過大評価する。中心推計は 2015-19（識別のプラセボ期と同一窓）の
    正常水準比で測る。2022年合計 ≈ 35兆円。

(A) Upper-bound — 上限:
    ΔTL_g(t) = M_g(2020) × (P_import_g(t) / 100 − 1)
    2020比の輸入コスト増。2020がトラフのため上限。2022年合計 ≈ 40.7兆円。

(B) Net (relative to domestic CGPI) — 相対価格変種:
    ΔTL_g(t) = M_g(2020) × (P_import_g(t) − P_domestic(t)) / 100
    輸入物価上昇のうち国内一般物価を上回った分。後年マイナスになり得る相対価格
    指標（フロー概念でない）。中心推計(C ≈35兆)を裏打ちする参考値。2022年 ≈ 34.6兆円。

Where:
    M_g(2020)      = IO table import value for group g (2020, billion JPY)
    P_import_g(t)  = BOJ CGPI import price index for group g (2020=100)
    P_ref_g        = group g の 2015-2019 平均輸入物価（中心推計の参照水準, DEC-012）
    P_domestic(t)  = BOJ CGPI domestic price index total (2020=100)

参照期に複数年平均（2015-19）を使う理由（DEC-012）:
  - 単年は石油サイクルの一点を拾い恣意的（2016=底91.8, 2018=山154.1）。
  - 2015-19 は両極を含むサイクル中立で、識別のプラセボ期と同一窓＝「正常」を論文で
    一回だけ定義できる。compute_baseline_sensitivity() で単年・3年平均との頑健性を出力。

--- 内閣府推計との定義の違い（論文注記用） ---

本研究の推計（B）と内閣府「交易利得・損失」（SNA付属表）には以下の定義差がある:

  内閣府:  ΔTL = (輸出価格上昇による利得) − (輸入価格上昇による損失)
           → 輸出企業が受け取る価格プレミアムを差し引いた「ネット」概念
           → 2022年推計: 約△12〜16兆円（GDP比△2〜3%）

  本研究:  ΔTL = 輸入コスト増加分のみ（輸出価格上昇分を控除しない）
           → 「家計・企業が負担する輸入コスト増加」の粗推計
           → 2022年中心推計(C, 2015-19基準): 約△35兆円 / 上限(A, 2020基準): 約△40.7兆円

本研究が大きくなる主因:
  1. 輸出側の交易利得（特に自動車・半導体等の輸出価格上昇分）を控除していない
  2. 対象5グループはエネルギー・金属・化学・食料・木材のみ（輸出財を含まない）
  3. 固定ボリューム仮定（2020年IO輸入額固定＝Laspeyres、実際の輸入量変化を反映しない）
     → 数量反応を織り込む Paasche/Fisher 化は財務省貿易統計の数量データ取得後の課題（未実施）

本研究の位置づけ: 「輸入コスト増加が日本の家計・産業部門に課す負担の粗推計」であり、
内閣府の交易損失（輸出相殺後）とは補完的な概念。両者を並記することで分析の透明性を確保する。
なお (C) は基準年を 2020 トラフから 2015-19 正常水準に補正済み（主因1・2は残置、3は今後の課題）。
"""

from pathlib import Path

import pandas as pd
import numpy as np

from src.analysis.import_content import (
    compute_group_import_content,
    GROUPS,
    GROUP_JA,
)
from src.data.fetch_import_prices import extract_domestic_cgpi

DATA_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
TRADE_LOSS_DIR = DATA_PROCESSED / "trade-loss"

CGPI_PATH = DATA_RAW / "boj-cgpi" / "import_prices_extracted.csv"
BASE_YEAR = 2020
# 中心推計の参照期（DEC-012）: 2015-2019 平均（識別のプラセボ期と同一窓・サイクル中立）
REF_BASELINE = (2015, 2019)

# 名目GDP（十億円）。出典: 内閣府「国民経済計算」名目暦年GDP（2022年 ≈561兆円・取得時点の推計値）
# TODO(DEC-019): 確報改定で値が動くため、論文確定時に vintage（公表回）を明記して更新する
GDP_BN_BY_YEAR = {2022: 561_000}


def load_import_prices() -> pd.DataFrame:
    """Load BOJ CGPI import price indices (2020=100)."""
    df = pd.read_csv(CGPI_PATH, parse_dates=["date"])
    return df


def compute_annual_price_index(force: bool = False) -> pd.DataFrame:
    """
    Compute annual average import price index for each of the 5 groups.

    force: キャッシュを無視して再計算（再現性検証用）

    Returns
    -------
    pd.DataFrame with columns: year, group, group_ja, price_index (annual avg, 2020=100)
    """
    TRADE_LOSS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = TRADE_LOSS_DIR / "annual_price_index.csv"

    if cache_path.exists() and not force:
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    prices = load_import_prices()
    prices["year"] = prices["date"].dt.year

    # Filter to 5 groups
    prices = prices[prices["group"].isin(GROUPS)].copy()

    annual = (
        prices.groupby(["year", "group", "group_ja"])["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "price_index"})
    )

    annual.to_csv(cache_path, index=False)
    print(f"Saved annual price index to {cache_path}")
    return annual


def compute_domestic_annual_index() -> pd.DataFrame:
    """
    Compute annual average of domestic CGPI total index.

    Returns
    -------
    pd.DataFrame with columns: year, domestic_cgpi
    """
    dom = extract_domestic_cgpi()
    dom["year"] = dom["date"].dt.year
    return (
        dom.groupby("year")["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "domestic_cgpi"})
    )


def compute_group_baseline_prices(ref_period: tuple = REF_BASELINE) -> dict:
    """
    各グループの参照期（既定 2015-2019）平均輸入物価 P_ref_g を返す（中心推計の基準）。

    2020 は COVID で輸入物価が異常な底値（特にエネルギー）。中心推計(C)は 2020 比でなく
    2015-19（プラセボ期と同一窓）の正常水準比で測る（DEC-012）。

    Returns
    -------
    dict: {group: P_ref_g (2020=100 スケールの参照期平均)}
    """
    annual = compute_annual_price_index()
    ref = annual[annual["year"].between(ref_period[0], ref_period[1])]
    ref_map = ref.groupby("group")["price_index"].mean().to_dict()
    missing = set(GROUPS) - set(ref_map)
    if missing:
        raise ValueError(
            f"参照期 {ref_period} の価格が無いグループ: {missing}。"
            f"annual_price_index のキャッシュが古い可能性（要再生成）。"
        )
    return ref_map


def compute_trade_loss(force: bool = False) -> pd.DataFrame:
    """
    Estimate trade loss (輸入コスト負担増) by group and year.

    Three estimates (DEC-012):
    - trade_loss_corrected_bn_jpy : CENTRAL — vs 2015-19 normal baseline
        = M_2020 × (P_import − P_ref_g) / 100   （P_ref_g = グループ別 2015-19 平均）
    - trade_loss_ub_bn_jpy : upper bound — vs 2020 trough
        = M_2020 × (P_import − 100) / 100
    - trade_loss_net_bn_jpy : relative-price variant — vs domestic CGPI
        = M_2020 × (P_import − P_domestic) / 100

    Positive value = import cost burden / income outflow from Japan.

    force: キャッシュを無視して再計算（再現性検証用）

    Returns
    -------
    pd.DataFrame with columns:
        year, group, group_ja,
        import_price_index,       : group-level BOJ CGPI import (2020=100)
        domestic_cgpi,            : domestic CGPI total (2020=100)
        net_price_diff,           : P_import − P_domestic (pp)
        import_value_base_bn_jpy, : 2020 IO import value (billion JPY)
        trade_loss_ub_bn_jpy,     : upper-bound trade loss (billion JPY)
        trade_loss_net_bn_jpy,    : net trade loss — preferred estimate (billion JPY)
    """
    TRADE_LOSS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = TRADE_LOSS_DIR / "trade_loss_by_group.csv"

    if cache_path.exists() and not force:
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    annual_price = compute_annual_price_index(force=force)
    group_io = compute_group_import_content(force=force)
    domestic = compute_domestic_annual_index()
    baseline_prices = compute_group_baseline_prices()  # P_ref_g (2015-19 平均)

    # IO import values by group (billion JPY = 十億円)
    group_import_map = dict(
        zip(group_io["group"], group_io["import_value_total"])
    )

    # Merge domestic CGPI into annual price table
    annual_price = annual_price.merge(domestic, on="year", how="left")

    rows = []
    for _, row in annual_price.iterrows():
        group = row["group"]
        year = int(row["year"])
        p_import = row["price_index"]
        p_domestic = row["domestic_cgpi"]

        base_value = group_import_map.get(group, 0.0)  # billion JPY
        p_ref = baseline_prices.get(group, 100.0)  # P_ref_g (2015-19 平均)

        # (C) Central: vs 2015-19 normal baseline
        trade_loss_corrected_bn = base_value * (p_import - p_ref) / 100.0

        # (A) Upper bound: vs 2020 trough
        trade_loss_ub_bn = base_value * (p_import - 100.0) / 100.0

        # (B) Net (relative-price variant): import price - domestic price
        net_diff = p_import - p_domestic if pd.notna(p_domestic) else np.nan
        trade_loss_net_bn = base_value * net_diff / 100.0 if pd.notna(net_diff) else np.nan

        rows.append({
            "year": year,
            "group": group,
            "group_ja": row["group_ja"],
            "import_price_index": round(p_import, 2),
            "import_price_baseline": round(p_ref, 2),       # P_ref_g (2015-19 平均)
            "domestic_cgpi": round(p_domestic, 2) if pd.notna(p_domestic) else np.nan,
            "net_price_diff": round(net_diff, 2) if pd.notna(net_diff) else np.nan,
            "import_value_base_bn_jpy": round(base_value, 2),
            "trade_loss_corrected_bn_jpy": round(trade_loss_corrected_bn, 2),
            "trade_loss_corrected_tn_jpy": round(trade_loss_corrected_bn / 1000, 4),
            "trade_loss_ub_bn_jpy": round(trade_loss_ub_bn, 2),
            "trade_loss_ub_tn_jpy": round(trade_loss_ub_bn / 1000, 4),
            "trade_loss_net_bn_jpy": round(trade_loss_net_bn, 2) if pd.notna(trade_loss_net_bn) else np.nan,
            "trade_loss_net_tn_jpy": round(trade_loss_net_bn / 1000, 4) if pd.notna(trade_loss_net_bn) else np.nan,
        })

    df = pd.DataFrame(rows).sort_values(["group", "year"]).reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    print(f"Saved trade loss estimates to {cache_path} ({len(df)} rows)")
    return df


def compute_total_trade_loss(force: bool = False) -> pd.DataFrame:
    """
    Aggregate trade loss across all 5 groups by year.

    Returns both upper-bound and net estimates.

    force: キャッシュを無視して再計算（再現性検証用）

    Returns
    -------
    pd.DataFrame with columns:
        year,
        total_ub_bn_jpy, total_ub_tn_jpy,     : upper bound aggregate
        total_net_bn_jpy, total_net_tn_jpy,    : net income transfer aggregate (preferred)
        plus per-group breakdown columns
    """
    TRADE_LOSS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = TRADE_LOSS_DIR / "trade_loss_total.csv"

    if cache_path.exists() and not force:
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    group_loss = compute_trade_loss(force=force)

    agg = group_loss.groupby("year").agg(
        total_corrected_bn_jpy=("trade_loss_corrected_bn_jpy", "sum"),
        total_ub_bn_jpy=("trade_loss_ub_bn_jpy", "sum"),
        total_net_bn_jpy=("trade_loss_net_bn_jpy", "sum"),
    ).reset_index()

    agg["total_corrected_tn_jpy"] = agg["total_corrected_bn_jpy"] / 1000
    agg["total_ub_tn_jpy"] = agg["total_ub_bn_jpy"] / 1000
    agg["total_net_tn_jpy"] = agg["total_net_bn_jpy"] / 1000

    # Per-group breakdown (central / upper-bound / net)
    corr_pivot = group_loss.pivot(index="year", columns="group", values="trade_loss_corrected_bn_jpy")
    corr_pivot.columns = [f"{c}_corrected_bn_jpy" for c in corr_pivot.columns]

    ub_pivot = group_loss.pivot(index="year", columns="group", values="trade_loss_ub_bn_jpy")
    ub_pivot.columns = [f"{c}_ub_bn_jpy" for c in ub_pivot.columns]

    net_pivot = group_loss.pivot(index="year", columns="group", values="trade_loss_net_bn_jpy")
    net_pivot.columns = [f"{c}_net_bn_jpy" for c in net_pivot.columns]

    total = (
        agg.merge(corr_pivot.reset_index(), on="year")
        .merge(ub_pivot.reset_index(), on="year")
        .merge(net_pivot.reset_index(), on="year")
    )
    total.to_csv(cache_path, index=False)
    print(f"Saved total trade loss to {cache_path}")
    return total


def compute_baseline_sensitivity(year: int = 2022, force: bool = False) -> pd.DataFrame:
    """
    参照期の選択に対する合計交易損失の感度（恣意性チェック用、DEC-012）。

    単年（2015/2016/2018/2019/2020）と複数年平均（2015-19=中心 / 2017-19）を比較。
    単年は石油サイクルの一点を拾い 30.6〜42.7兆と振れるが、複数年平均は ~34-35兆で頑健。

    force: キャッシュを無視して再計算（再現性検証用）

    Returns
    -------
    pd.DataFrame: columns = baseline, total_tn_jpy, gdp_pct, energy_share_pct
    """
    annual = compute_annual_price_index(force=force)
    group_io = compute_group_import_content(force=force)
    m0 = dict(zip(group_io["group"], group_io["import_value_total"]))
    p_t = annual[annual["year"] == year].set_index("group")["price_index"].to_dict()
    if year not in GDP_BN_BY_YEAR:
        raise KeyError(
            f"GDP_BN_BY_YEAR に {year} 年のGDPが未登録。trade_loss.py 冒頭の GDP_BN_BY_YEAR に追加せよ"
        )
    gdp_bn = GDP_BN_BY_YEAR[year]

    specs = {
        "2020 単年（上限）": ("year", 2020),
        "2015 単年": ("year", 2015),
        "2016 単年": ("year", 2016),
        "2018 単年": ("year", 2018),
        "2019 単年": ("year", 2019),
        "2015-19 平均（中心）": ("range", REF_BASELINE),
        "2017-19 平均": ("range", (2017, 2019)),
    }

    rows = []
    for label, (kind, spec) in specs.items():
        total = energy = 0.0
        for g in GROUPS:
            sub = annual[annual["group"] == g]
            if kind == "year":
                p_ref = sub[sub["year"] == spec]["price_index"].mean()
            else:
                p_ref = sub[sub["year"].between(*spec)]["price_index"].mean()
            v = m0.get(g, 0.0) * (p_t.get(g, 100.0) - p_ref) / 100.0
            total += v
            if g == "energy":
                energy = v
        rows.append({
            "baseline": label,
            "total_tn_jpy": round(total / 1000, 2),
            "gdp_pct": round(100 * total / gdp_bn, 1),
            "energy_share_pct": round(100 * energy / total, 1) if total else np.nan,
        })

    df = pd.DataFrame(rows)
    cache_path = TRADE_LOSS_DIR / f"trade_loss_baseline_sensitivity_{year}.csv"
    df.to_csv(cache_path, index=False)
    print(f"Saved baseline sensitivity ({year}) to {cache_path}")
    return df


if __name__ == "__main__":
    print("=== Annual Import Price Index (2020=100) ===")
    annual_px = compute_annual_price_index()
    pivot = annual_px.pivot(index="year", columns="group_ja", values="price_index")
    print(pivot.round(1).to_string())

    print("\n=== Domestic CGPI Annual Average (2020=100) ===")
    dom = compute_domestic_annual_index()
    print(dom.to_string(index=False))

    print("\n=== Baseline P_ref (2015-19 平均, 2020=100) ===")
    for g, p in compute_group_baseline_prices().items():
        print(f"  {g:10s}: {p:6.1f}")

    print("\n=== Trade Loss by Group (bn JPY) ===")
    loss_df = compute_trade_loss()

    for year in sorted(loss_df["year"].unique()):
        year_data = loss_df[loss_df["year"] == year]
        total_corr = year_data["trade_loss_corrected_bn_jpy"].sum()
        total_ub = year_data["trade_loss_ub_bn_jpy"].sum()
        total_net = year_data["trade_loss_net_bn_jpy"].sum()
        print(f"\n[{year}]  中心C(2015-19基準): {total_corr/1000:.1f} tn  "
              f"上限A(2020基準): {total_ub/1000:.1f} tn  net B(対国内): {total_net/1000:.1f} tn")
        for _, row in year_data.sort_values("trade_loss_corrected_bn_jpy", ascending=False).iterrows():
            print(f"  {row['group_ja']:24s}: "
                  f"P_imp={row['import_price_index']:6.1f}  "
                  f"P_ref={row['import_price_baseline']:6.1f}  "
                  f"中心={row['trade_loss_corrected_bn_jpy']:7,.0f} bn JPY")

    print("\n=== Total Trade Loss by Year（中心C / 上限A / net B）===")
    total_df = compute_total_trade_loss()
    print(f"\n{'Year':>6}  {'中心C(tn)':>11}  {'上限A(tn)':>11}  {'net B(tn)':>11}  {'中心%GDP':>9}")
    for _, row in total_df.iterrows():
        pct = row["total_corrected_bn_jpy"] / GDP_BN_BY_YEAR[2022] * 100
        print(f"  {int(row['year'])}: {row['total_corrected_tn_jpy']:9.1f}    "
              f"{row['total_ub_tn_jpy']:9.1f}    {row['total_net_tn_jpy']:9.1f}    {pct:7.1f}%")

    print("\n=== Baseline Sensitivity (2022, 恣意性チェック) ===")
    sens = compute_baseline_sensitivity(2022)
    print(sens.to_string(index=False))

    print("\nNote: 中心推計C = 輸入物価 − 2015-19平均（正常水準）。2020はCOVIDトラフのため上限A。")
    print("net B = 輸入物価 − 国内CGPI（相対価格・参考）。内閣府交易損失（輸出相殺後）とは別概念。")
