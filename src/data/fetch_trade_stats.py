"""
Fetch trade statistics (import values by commodity) from e-Stat API.
Uses the summary commodity classification (概況品別表).
"""

from pathlib import Path

import pandas as pd

from .estat_api import search_stats, get_stats_data

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "trade-stats"


def find_trade_table() -> None:
    """Search for trade statistics tables on e-Stat."""
    tables = search_stats("貿易統計 概況品 輸入 月次", limit=20)
    for t in tables:
        tid = t.get("@id", "N/A")
        title = t.get("TITLE", {})
        if isinstance(title, dict):
            tname = title.get("$", "N/A")
        else:
            tname = str(title)
        cycle = t.get("CYCLE", "N/A")
        print(f"ID: {tid} | Cycle: {cycle} | {tname}")


def fetch_trade_imports(
    stats_data_id: str,
    years: tuple[int, int] = (2015, 2025),
) -> pd.DataFrame:
    """
    Fetch import values by commodity group from e-Stat.

    Parameters
    ----------
    stats_data_id : str
        e-Stat table ID for trade statistics.
    years : tuple
        (start_year, end_year) inclusive.

    Returns
    -------
    pd.DataFrame
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = RAW_DIR / f"trade_imports_{years[0]}_{years[1]}.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    print(f"Fetching trade statistics ({years[0]}-{years[1]})...")

    time_from = f"{years[0]}01"
    time_to = f"{years[1]}12"

    df = get_stats_data(
        stats_data_id,
        cdTimeFrom=time_from,
        cdTimeTo=time_to,
    )

    if df.empty:
        print("Warning: No data returned")
        return df

    df.to_csv(cache_path, index=False)
    print(f"Saved to {cache_path} ({len(df)} rows)")
    return df


if __name__ == "__main__":
    print("Searching for trade statistics tables...")
    find_trade_table()
