"""
Phase 1 Step 1-3: Trade loss (terms of trade loss) estimation.

Trade loss = the additional yen cost of the same import volume due to price increases.
Formula: ΔTL_g(t) = M_g(2020) × (P_g(t) / P_g(base) - 1)

Where:
    M_g(2020)   = IO table import value for group g (2020 snapshot, 100mn JPY)
    P_g(t)      = BOJ CGPI import price index for group g at time t (2020=100)
    P_g(base)   = Baseline index (2020=100 by definition for this series)
"""

from pathlib import Path

import pandas as pd
import numpy as np

from src.analysis.import_content import (
    compute_group_import_content,
    GROUPS,
    GROUP_JA,
)

DATA_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
TRADE_LOSS_DIR = DATA_PROCESSED / "trade-loss"

CGPI_PATH = DATA_RAW / "boj-cgpi" / "import_prices_extracted.csv"

# Baseline period: 2020 (= 100 by BOJ definition for this series)
# Since BOJ CGPI only starts from 2020, we use 2020 as base year.
# We compare:
#   - Trough: 2020 average (≈100 by construction)
#   - Pre-shock reference: 2021 (first full post-COVID year)
#   - Peak shock: 2022-2023
#   - Recent: 2024
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


def compute_trade_loss() -> pd.DataFrame:
    """
    Estimate trade loss (所得流出額) by group and year.

    Trade loss = import_value_2020 × (price_index_t / 100 - 1)

    Positive value = income outflow from Japan (Japan pays more for same imports).

    Returns
    -------
    pd.DataFrame with columns:
        year, group, group_ja,
        price_index,          : BOJ CGPI annual average (2020=100)
        price_change_pct,     : price change vs 2020 base (%)
        import_value_base,    : 2020 IO import value (100mn JPY)
        trade_loss_100mn_jpy, : estimated trade loss (100mn JPY)
        trade_loss_bn_jpy,    : estimated trade loss (bn JPY)
    """
    TRADE_LOSS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = TRADE_LOSS_DIR / "trade_loss_by_group.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    annual_price = compute_annual_price_index()
    group_io = compute_group_import_content()

    # IO import values by group (billion JPY = 十億円)
    group_import_map = dict(
        zip(group_io["group"], group_io["import_value_total"])
    )

    rows = []
    for _, row in annual_price.iterrows():
        group = row["group"]
        year = int(row["year"])
        price_idx = row["price_index"]

        base_value = group_import_map.get(group, 0.0)  # billion JPY
        price_change_pct = price_idx - 100.0  # vs 2020=100 base
        trade_loss_bn = base_value * (price_change_pct / 100.0)  # billion JPY

        rows.append({
            "year": year,
            "group": group,
            "group_ja": row["group_ja"],
            "price_index": round(price_idx, 2),
            "price_change_pct": round(price_change_pct, 2),
            "import_value_base_bn_jpy": round(base_value, 2),
            "trade_loss_bn_jpy": round(trade_loss_bn, 2),
            "trade_loss_tn_jpy": round(trade_loss_bn / 1000, 4),
        })

    df = pd.DataFrame(rows).sort_values(["group", "year"]).reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    print(f"Saved trade loss estimates to {cache_path} ({len(df)} rows)")
    return df


def compute_total_trade_loss() -> pd.DataFrame:
    """
    Aggregate trade loss across all 5 groups by year.

    Returns
    -------
    pd.DataFrame with columns: year, total_trade_loss_100mn_jpy, total_trade_loss_bn_jpy,
                                total_trade_loss_tn_jpy (兆円)
    """
    TRADE_LOSS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = TRADE_LOSS_DIR / "trade_loss_total.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    group_loss = compute_trade_loss()

    total = (
        group_loss.groupby("year")["trade_loss_bn_jpy"]
        .sum()
        .reset_index()
        .rename(columns={"trade_loss_bn_jpy": "total_trade_loss_bn_jpy"})
    )

    total["total_trade_loss_tn_jpy"] = total["total_trade_loss_bn_jpy"] / 1000

    # Add group breakdown (billion JPY)
    group_pivot = group_loss.pivot(index="year", columns="group", values="trade_loss_bn_jpy")
    group_pivot.columns = [f"{c}_bn_jpy" for c in group_pivot.columns]
    total = total.merge(group_pivot.reset_index(), on="year")

    total.to_csv(cache_path, index=False)
    print(f"Saved total trade loss to {cache_path}")
    return total


if __name__ == "__main__":
    print("=== Annual Import Price Index (2020=100) ===")
    annual_px = compute_annual_price_index()
    pivot = annual_px.pivot(index="year", columns="group_ja", values="price_index")
    print(pivot.round(1).to_string())

    print("\n=== Trade Loss by Group (bn JPY, 十億円) ===")
    print("Note: Upper bound — assumes 2020 import volumes held constant.")
    loss_df = compute_trade_loss()

    for year in sorted(loss_df["year"].unique()):
        year_data = loss_df[loss_df["year"] == year]
        total_bn = year_data["trade_loss_bn_jpy"].sum()
        print(f"\n[{year}] Total: {total_bn:,.0f} bn JPY ({total_bn/1000:.2f} tn JPY)")
        for _, row in year_data.sort_values("trade_loss_bn_jpy", ascending=False).iterrows():
            bar = "#" * max(0, int(row["trade_loss_bn_jpy"] / 500))
            print(f"  {row['group_ja']:24s}: {row['price_change_pct']:+6.1f}%  "
                  f"loss={row['trade_loss_bn_jpy']:8,.0f} bn JPY  {bar}")

    print("\n=== Total Trade Loss by Year ===")
    total_df = compute_total_trade_loss()
    print(total_df[["year", "total_trade_loss_bn_jpy", "total_trade_loss_tn_jpy"]].to_string(index=False))

    # Contextual comparison: as % of Japan's nominal GDP
    # Japan nominal GDP 2020 ≈ 537 tn JPY = 537,000 bn JPY
    GDP_2020_BN = 537_000
    print("\n=== Trade Loss as % of Japan GDP (2020) ===")
    for _, row in total_df.iterrows():
        pct = row["total_trade_loss_bn_jpy"] / GDP_2020_BN * 100
        print(f"  {int(row['year'])}: {row['total_trade_loss_tn_jpy']:.1f} tn JPY  "
              f"({pct:.1f}% of 2020 GDP)")

    print("\nNote: IO table unit = billion JPY (十億円). 2020 base year = 100.")
    print("Trade loss = import_value_2020 × (price_index_t / 100 - 1). Upper bound (fixed 2020 volumes).")
