"""
Fetch Consumer Price Index (CPI) by expenditure category from e-Stat.
"""

from pathlib import Path

import httpx

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "cpi"

# e-Stat API endpoint
ESTAT_API_BASE = "https://api.e-stat.go.jp/rest/3.0/app"


def fetch_cpi_by_category():
    """
    Download CPI data by expenditure category (費目別) from e-Stat.

    Target: 消費者物価指数 > 全国 > 中分類 > 月次
    Period: 2015-01 to latest

    CPI data is available through:
    1. e-Stat file download (Excel)
    2. e-Stat API (JSON/CSV)

    For API access, an appId is required (free registration).
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print("Consumer Price Index (消費者物価指数) - by category")
    print("=" * 60)
    print()
    print("Download from e-Stat:")
    print("  https://www.e-stat.go.jp/stat-search/files?toukei=00200573")
    print()
    print("Target:")
    print("  - 全国 > 月次 > 中分類指数")
    print("  - Period: 2015-01 to latest")
    print("  - Base year: 2020")
    print()
    print("For API access:")
    print("  Register at https://www.e-stat.go.jp/mypage/view/api")
    print("  Set ESTAT_API_KEY environment variable")
    print()
    print(f"Save files to: {RAW_DIR}/")


if __name__ == "__main__":
    fetch_cpi_by_category()
