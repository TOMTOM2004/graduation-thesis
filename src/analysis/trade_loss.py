"""
Phase 1 Step 1-3: Trade loss (terms of trade loss) estimation.

Two estimates are computed:

(A) Upper-bound (absolute):
    ΔTL_g(t) = M_g(2020) × (P_import_g(t) / 100 − 1)
    Measures the additional import cost vs. 2020. Overestimates income outflow
    because it ignores the rise in domestic prices (inflation neutralizes part of
    the increase in nominal import costs).

(B) Net income transfer (preferred):
    ΔTL_g(t) = M_g(2020) × (P_import_g(t) − P_domestic(t)) / 100
    Measures only the excess price increase relative to domestic inflation — the
    portion that represents a real income transfer to foreign exporters.
    Comparable to Cabinet Office 交易利得（損失）in the SNA.

Where:
    M_g(2020)      = IO table import value for group g (2020, billion JPY)
    P_import_g(t)  = BOJ CGPI import price index for group g (2020=100)
    P_domestic(t)  = BOJ CGPI domestic price index total (2020=100)

--- 内閣府推計との定義の違い（論文注記用） ---

本研究の推計（B）と内閣府「交易利得・損失」（SNA付属表）には以下の定義差がある:

  内閣府:  ΔTL = (輸出価格上昇による利得) − (輸入価格上昇による損失)
           → 輸出企業が受け取る価格プレミアムを差し引いた「ネット」概念
           → 2022年推計: 約△12〜16兆円（GDP比△2〜3%）

  本研究:  ΔTL = 輸入コスト増加分のみ（輸出価格上昇分を控除しない）
           → 「家計・企業が負担する輸入コスト増加」の粗推計
           → 2022年推計: 約△34.6兆円（net B）

本研究が大きくなる主因:
  1. 輸出側の交易利得（特に自動車・半導体等の輸出価格上昇分）を控除していない
  2. 対象5グループはエネルギー・金属・化学・食料・木材のみ（輸出財を含まない）
  3. 2020年基準IO表の固定ボリューム仮定（実際の輸入量変化を反映しない）

本研究の位置づけ: 「輸入コスト増加が日本の家計・産業部門に課す負担の粗推計」であり、
内閣府の交易損失（輸出相殺後）とは補完的な概念。両者を並記することで分析の透明性を確保する。
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


def load_import_prices() -> pd.DataFrame:
    """Load BOJ CGPI import price indices (2020=100)."""
    df = pd.read_csv(CGPI_PATH, parse_dates=["date"])
    return df


def compute_annual_price_index() -> pd.DataFrame:
    """
    Compute annual average import price index for each of the 5 groups.

    Returns
    -------
    pd.DataFrame with columns: year, group, group_ja, price_index (annual avg, 2020=100)
    """
    TRADE_LOSS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = TRADE_LOSS_DIR / "annual_price_index.csv"

    if cache_path.exists():
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


def compute_trade_loss() -> pd.DataFrame:
    """
    Estimate trade loss (所得流出額) by group and year.

    Two estimates:
    - trade_loss_ub_bn_jpy : upper bound — absolute import price change
        = M_2020 × (P_import − 100) / 100
    - trade_loss_net_bn_jpy : net income transfer (preferred, comparable to Cabinet Office)
        = M_2020 × (P_import − P_domestic) / 100

    Positive value = income outflow from Japan (Japan pays more than domestic prices rise).

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

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    annual_price = compute_annual_price_index()
    group_io = compute_group_import_content()
    domestic = compute_domestic_annual_index()

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

        # (A) Upper bound: absolute import price change
        trade_loss_ub_bn = base_value * (p_import - 100.0) / 100.0

        # (B) Net income transfer: import price - domestic price
        net_diff = p_import - p_domestic if pd.notna(p_domestic) else np.nan
        trade_loss_net_bn = base_value * net_diff / 100.0 if pd.notna(net_diff) else np.nan

        rows.append({
            "year": year,
            "group": group,
            "group_ja": row["group_ja"],
            "import_price_index": round(p_import, 2),
            "domestic_cgpi": round(p_domestic, 2) if pd.notna(p_domestic) else np.nan,
            "net_price_diff": round(net_diff, 2) if pd.notna(net_diff) else np.nan,
            "import_value_base_bn_jpy": round(base_value, 2),
            "trade_loss_ub_bn_jpy": round(trade_loss_ub_bn, 2),
            "trade_loss_ub_tn_jpy": round(trade_loss_ub_bn / 1000, 4),
            "trade_loss_net_bn_jpy": round(trade_loss_net_bn, 2) if pd.notna(trade_loss_net_bn) else np.nan,
            "trade_loss_net_tn_jpy": round(trade_loss_net_bn / 1000, 4) if pd.notna(trade_loss_net_bn) else np.nan,
        })

    df = pd.DataFrame(rows).sort_values(["group", "year"]).reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    print(f"Saved trade loss estimates to {cache_path} ({len(df)} rows)")
    return df


def compute_total_trade_loss() -> pd.DataFrame:
    """
    Aggregate trade loss across all 5 groups by year.

    Returns both upper-bound and net estimates.

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

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    group_loss = compute_trade_loss()

    agg = group_loss.groupby("year").agg(
        total_ub_bn_jpy=("trade_loss_ub_bn_jpy", "sum"),
        total_net_bn_jpy=("trade_loss_net_bn_jpy", "sum"),
    ).reset_index()

    agg["total_ub_tn_jpy"] = agg["total_ub_bn_jpy"] / 1000
    agg["total_net_tn_jpy"] = agg["total_net_bn_jpy"] / 1000

    # Per-group upper-bound breakdown
    ub_pivot = group_loss.pivot(index="year", columns="group", values="trade_loss_ub_bn_jpy")
    ub_pivot.columns = [f"{c}_ub_bn_jpy" for c in ub_pivot.columns]

    # Per-group net breakdown
    net_pivot = group_loss.pivot(index="year", columns="group", values="trade_loss_net_bn_jpy")
    net_pivot.columns = [f"{c}_net_bn_jpy" for c in net_pivot.columns]

    total = agg.merge(ub_pivot.reset_index(), on="year").merge(net_pivot.reset_index(), on="year")
    total.to_csv(cache_path, index=False)
    print(f"Saved total trade loss to {cache_path}")
    return total


if __name__ == "__main__":
    print("=== Annual Import Price Index (2020=100) ===")
    annual_px = compute_annual_price_index()
    pivot = annual_px.pivot(index="year", columns="group_ja", values="price_index")
    print(pivot.round(1).to_string())

    print("\n=== Domestic CGPI Annual Average (2020=100) ===")
    dom = compute_domestic_annual_index()
    print(dom.to_string(index=False))

    print("\n=== Trade Loss by Group (bn JPY) ===")
    loss_df = compute_trade_loss()

    for year in sorted(loss_df["year"].unique()):
        year_data = loss_df[loss_df["year"] == year]
        total_ub = year_data["trade_loss_ub_bn_jpy"].sum()
        total_net = year_data["trade_loss_net_bn_jpy"].sum()
        print(f"\n[{year}]  Upper bound: {total_ub/1000:.1f} tn JPY   Net transfer: {total_net/1000:.1f} tn JPY")
        for _, row in year_data.sort_values("trade_loss_net_bn_jpy", ascending=False).iterrows():
            print(f"  {row['group_ja']:24s}: "
                  f"P_import={row['import_price_index']:6.1f}  "
                  f"P_dom={row['domestic_cgpi']:6.1f}  "
                  f"diff={row['net_price_diff']:+6.1f}pp  "
                  f"net={row['trade_loss_net_bn_jpy']:7,.0f} bn JPY")

    print("\n=== Total Trade Loss by Year ===")
    total_df = compute_total_trade_loss()
    GDP_2020_BN = 537_000
    print(f"\n{'Year':>6}  {'UB (tn)':>9}  {'Net (tn)':>9}  {'Net % GDP':>10}")
    for _, row in total_df.iterrows():
        pct = row["total_net_bn_jpy"] / GDP_2020_BN * 100
        print(f"  {int(row['year'])}: UB={row['total_ub_tn_jpy']:6.1f} tn  "
              f"Net={row['total_net_tn_jpy']:6.1f} tn  ({pct:.1f}% of GDP)")

    print("\nNote: Net estimate = import price rise minus domestic inflation.")
    print("Comparable to Cabinet Office 交易利得（損失）. Upper bound = absolute import cost increase.")
