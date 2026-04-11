"""
Fetch Consumer Price Index (CPI) by expenditure category from e-Stat API.
"""

from pathlib import Path

import pandas as pd

from .estat_api import search_stats, get_stats_data

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "cpi"

# 消費者物価指数（2020年基準）
CPI_2020_TABLE = "0003427113"


def find_cpi_table() -> str:
    """Search for the CPI monthly table by category."""
    tables = search_stats("消費者物価指数 全国 月次 中分類", limit=20)
    for t in tables:
        tid = t.get("@id", "N/A")
        title = t.get("TITLE", {})
        if isinstance(title, dict):
            tname = title.get("$", "N/A")
        else:
            tname = title
        cycle = t.get("CYCLE", "N/A")
        print(f"ID: {tid} | Cycle: {cycle} | Title: {tname}")
    return ""


def fetch_cpi_by_category(years: tuple[int, int] = (2015, 2025)) -> pd.DataFrame:
    """
    Fetch CPI data by expenditure category (monthly).

    Parameters
    ----------
    years : tuple
        (start_year, end_year) inclusive.

    Returns
    -------
    pd.DataFrame
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = RAW_DIR / f"cpi_category_{years[0]}_{years[1]}.csv"

    if cache_path.exists():
        print(f"Loading cached data: {cache_path}")
        return pd.read_csv(cache_path)

    print(f"Fetching CPI data ({years[0]}-{years[1]})...")

    time_from = f"{years[0]}00"
    time_to = f"{years[1]}12"

    df = get_stats_data(
        CPI_2020_TABLE,
        cdArea="00000",  # 全国
        cdTimeFrom=time_from,
        cdTimeTo=time_to,
    )

    if df.empty:
        print("Warning: No data returned. Try find_cpi_table() to get correct table ID.")
        return df

    df.to_csv(cache_path, index=False)
    print(f"Saved to {cache_path} ({len(df)} rows)")
    return df


if __name__ == "__main__":
    print("Searching for CPI tables...")
    find_cpi_table()
