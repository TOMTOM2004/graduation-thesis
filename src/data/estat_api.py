"""
e-Stat API client for fetching Japanese government statistics.
"""

import os
import json
from pathlib import Path

import httpx
import pandas as pd

ESTAT_API_BASE = "https://api.e-stat.go.jp/rest/3.0/app"


def get_api_key() -> str:
    """Load e-Stat API key from .env file or environment variable."""
    key = os.environ.get("ESTAT_API_KEY")
    if key:
        return key

    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if line.startswith("ESTAT_API_KEY="):
                return line.split("=", 1)[1].strip()

    raise ValueError("ESTAT_API_KEY not found. Set it in .env or environment.")


def search_stats(keyword: str, limit: int = 10) -> list[dict]:
    """Search for statistical tables by keyword."""
    api_key = get_api_key()
    url = f"{ESTAT_API_BASE}/json/getStatsList"
    params = {
        "appId": api_key,
        "searchWord": keyword,
        "limit": limit,
        "lang": "J",
    }

    with httpx.Client(timeout=30) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()

    data = resp.json()
    result = data.get("GET_STATS_LIST", {}).get("DATALIST_INF", {})
    tables = result.get("TABLE_INF", [])

    if isinstance(tables, dict):
        tables = [tables]

    return tables


def get_stats_data(
    stats_data_id: str,
    section_header_flg: int = 2,
    **kwargs,
) -> pd.DataFrame:
    """
    Fetch statistical data from e-Stat API.

    Parameters
    ----------
    stats_data_id : str
        The table ID (統計表ID) to fetch.
    section_header_flg : int
        1=include section headers, 2=exclude (default)
    **kwargs
        Additional API parameters (cdCat01, cdTime, etc.)

    Returns
    -------
    pd.DataFrame
    """
    api_key = get_api_key()
    url = f"{ESTAT_API_BASE}/json/getStatsData"
    params = {
        "appId": api_key,
        "statsDataId": stats_data_id,
        "sectionHeaderFlg": section_header_flg,
        "lang": "J",
        **kwargs,
    }

    with httpx.Client(timeout=60) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()

    data = resp.json()

    stat_data = data.get("GET_STATS_DATA", {})
    if "RESULT" in stat_data and stat_data["RESULT"]["STATUS"] != 0:
        error_msg = stat_data["RESULT"].get("ERROR_MSG", "Unknown error")
        raise ValueError(f"e-Stat API error: {error_msg}")

    # Parse class information (metadata for each dimension)
    class_info = stat_data.get("STATISTICAL_DATA", {}).get("CLASS_INF", {}).get("CLASS_OBJ", [])
    if isinstance(class_info, dict):
        class_info = [class_info]

    class_map = {}
    for cls in class_info:
        cls_id = cls["@id"]
        codes = cls.get("CLASS", [])
        if isinstance(codes, dict):
            codes = [codes]
        class_map[cls_id] = {c["@code"]: c.get("@name", c["@code"]) for c in codes}

    # Parse data values
    values = stat_data.get("STATISTICAL_DATA", {}).get("DATA_INF", {}).get("VALUE", [])
    if isinstance(values, dict):
        values = [values]

    rows = []
    for v in values:
        row = {}
        for key, val in v.items():
            if key == "$":
                row["value"] = val
            elif key.startswith("@"):
                dim_id = key[1:]
                code = val
                row[f"{dim_id}_code"] = code
                if dim_id in class_map and code in class_map[dim_id]:
                    row[f"{dim_id}_name"] = class_map[dim_id][code]
        rows.append(row)

    df = pd.DataFrame(rows)

    # Convert value column to numeric
    if "value" in df.columns:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")

    return df


if __name__ == "__main__":
    # Test: search for household survey tables
    print("Testing e-Stat API connection...")
    tables = search_stats("家計調査 五分位", limit=5)
    for t in tables:
        print(f"  ID: {t.get('@id', 'N/A')}")
        title = t.get("TITLE", {})
        if isinstance(title, dict):
            print(f"  Title: {title.get('$', 'N/A')}")
        else:
            print(f"  Title: {title}")
        print()
