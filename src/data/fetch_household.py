"""
Fetch household survey data from e-Stat API.
- Family Income and Expenditure Survey (家計調査): income quintile x expenditure category
"""

from pathlib import Path

import pandas as pd

from .estat_api import get_stats_data

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "household-survey"

# Table IDs
HOUSEHOLD_QUINTILE_YEARLY = "0002070005"  # 用途分類（年間収入五分位階級別）年次
HOUSEHOLD_QUANTITY_MONTHLY = "0003343670"  # 品目別 数量（月次・全国・二人以上世帯・2000年～）


def fetch_household_quantity_monthly() -> pd.DataFrame:
    """
    Fetch monthly physical-quantity by item for two-or-more-person households.

    Used for the Shapiro (2024) supply/demand decomposition (DEC-016, layer 1):
    item-level price (CPI) x quantity (this table) comovement. Pulls the full
    2000-2024 monthly history (residualization needs a long series; 60 months
    would be fragile -- DEC-016 pre-registration). Restricts to cat02=03
    (二人以上の世帯), matching the Phase 2b household universe (DEC-011).

    Returns
    -------
    pd.DataFrame with e-Stat dimension columns (cat01=item, time=month, value).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = RAW_DIR / "household_quantity_monthly_2000_2024.csv"

    if cache_path.exists():
        print(f"Loading cached data: {cache_path}")
        return pd.read_csv(cache_path)

    print("Fetching household survey (monthly quantity, 2000-2024, two-or-more-person)...")
    df = get_stats_data(
        HOUSEHOLD_QUANTITY_MONTHLY,
        cdCat02="03",  # 二人以上の世帯（2000年～）
    )

    if df.empty:
        print("Warning: No data returned from API")
        return df

    df.to_csv(cache_path, index=False)
    print(f"Saved to {cache_path} ({len(df)} rows)")
    return df


def fetch_household_quintile(years: tuple[int, int] = (2015, 2024)) -> pd.DataFrame:
    """
    Fetch household expenditure by income quintile and expenditure category.

    Parameters
    ----------
    years : tuple
        (start_year, end_year) inclusive.

    Returns
    -------
    pd.DataFrame with columns: year, quintile, category, value
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = RAW_DIR / f"household_quintile_{years[0]}_{years[1]}.csv"

    if cache_path.exists():
        print(f"Loading cached data: {cache_path}")
        return pd.read_csv(cache_path)

    print(f"Fetching household survey (quintile, {years[0]}-{years[1]})...")

    # Build time code filter
    time_from = f"{years[0]}000000"
    time_to = f"{years[1]}000000"

    df = get_stats_data(
        HOUSEHOLD_QUINTILE_YEARLY,
        cdTab="01",  # 金額
        cdTimeFrom=time_from,
        cdTimeTo=time_to,
    )

    if df.empty:
        print("Warning: No data returned from API")
        return df

    # Save raw data
    df.to_csv(cache_path, index=False)
    print(f"Saved to {cache_path} ({len(df)} rows)")

    return df


if __name__ == "__main__":
    df = fetch_household_quintile()
    print(f"\nTotal rows: {len(df)}")
    print(f"\nQuintile categories (cat03):")
    if "cat03_name" in df.columns:
        for name in df["cat03_name"].unique():
            print(f"  {name}")
    print(f"\nExpenditure categories (cat01, first 20):")
    if "cat01_name" in df.columns:
        for name in df["cat01_name"].unique()[:20]:
            print(f"  {name}")
