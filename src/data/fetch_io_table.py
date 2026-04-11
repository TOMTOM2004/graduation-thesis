"""
Fetch Japan's 2020 Input-Output Table from e-Stat.
Downloads the producer-price transaction table (108 sectors, integrated medium classification).
"""

import os
from pathlib import Path

import httpx

# e-Stat download URLs for 2020 IO table (integrated medium classification, 108 sectors)
IO_TABLE_URLS = {
    "producer_price": {
        "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040187026&fileKind=0",
        "filename": "io2020_producer_price_108.xlsx",
        "description": "生産者価格評価表（統合中分類108部門）",
    },
    "purchaser_price": {
        "url": "https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040187031&fileKind=0",
        "filename": "io2020_purchaser_price_108.xlsx",
        "description": "購入者価格評価表（統合中分類108部門）",
    },
}

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "io-table"


def fetch_io_table(table_key: str = "producer_price") -> Path:
    """Download IO table Excel file from e-Stat."""
    info = IO_TABLE_URLS[table_key]
    dest = RAW_DIR / info["filename"]

    if dest.exists():
        print(f"Already exists: {dest}")
        return dest

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {info['description']}...")

    with httpx.Client(follow_redirects=True, timeout=120) as client:
        resp = client.get(info["url"])
        resp.raise_for_status()

    dest.write_bytes(resp.content)
    print(f"Saved to {dest} ({len(resp.content) / 1024:.0f} KB)")
    return dest


if __name__ == "__main__":
    for key in IO_TABLE_URLS:
        fetch_io_table(key)
