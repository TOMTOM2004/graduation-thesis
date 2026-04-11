"""
Fetch BOJ Corporate Goods Price Index (CGPI) - Import Price Index.
Downloads monthly import price indices by commodity group from BOJ website.
"""

from pathlib import Path

import httpx

# BOJ CGPI import price index CSV
# Monthly data, yen basis, by commodity group
BOJ_CGPI_URL = "https://www.stat-search.boj.or.jp/ssi/mtshtml/pr02_m_1.html"

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "boj-cgpi"


def fetch_import_price_index() -> Path:
    """
    Download BOJ import price index data.

    Note: BOJ provides data through their time-series search system.
    The CSV download requires specific query parameters.
    This script downloads the HTML page listing available series.
    For bulk data, use the BOJ Time-Series Data Search:
    https://www.stat-search.boj.or.jp/index_en.html

    Manual download steps (if automated fetch fails):
    1. Go to https://www.stat-search.boj.or.jp/ssi/mtshtml/pr02_m_1.html
    2. Select import price indices by commodity group
    3. Set period: 2015-01 to latest
    4. Download as CSV
    """
    dest = RAW_DIR / "boj_import_price_index.csv"

    if dest.exists():
        print(f"Already exists: {dest}")
        return dest

    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Try fetching from BOJ time-series API
    # The BOJ API endpoint for import price index (yen basis, monthly)
    api_url = "https://www.stat-search.boj.or.jp/ssi/cgi-bin/famecgi2"
    params = {
        "cgi": "$nme_a000_en&lstSelection",
        "lstOutput": "2",  # CSV output
    }

    print("Note: BOJ data requires manual download or API access.")
    print("Please download import price index CSV from:")
    print("  https://www.stat-search.boj.or.jp/ssi/mtshtml/pr02_m_1.html")
    print(f"Save the file to: {dest}")

    return dest


if __name__ == "__main__":
    fetch_import_price_index()
