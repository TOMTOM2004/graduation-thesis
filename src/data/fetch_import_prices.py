"""
Fetch BOJ Corporate Goods Price Index (CGPI) - Import Price Index.
Uses BOJ bulk CSV download (all CGPI data in one ZIP).
"""

import io
import zipfile
from pathlib import Path

import httpx
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "boj-cgpi"

# BOJ bulk download: all CGPI monthly data
CGPI_BULK_URL = "https://www.stat-search.boj.or.jp/info/cgpi_m_jp.zip"

# Import price index series codes (yen basis, 2020 base, category level)
IMPORT_PRICE_SERIES = {
    "total": {"code": "PRCG20_2600000000", "name": "輸入物価指数 総平均"},
    "food": {"code": "PRCG20_2600120001", "name": "飲食料品・食料用農水産物"},
    "textiles": {"code": "PRCG20_2600220001", "name": "繊維品"},
    "metals": {"code": "PRCG20_2600320001", "name": "金属・同製品"},
    "wood": {"code": "PRCG20_2600420001", "name": "木材・木製品・林産物"},
    "energy": {"code": "PRCG20_2600520001", "name": "石油・石炭・天然ガス"},
    "chemicals": {"code": "PRCG20_2600620001", "name": "化学製品"},
    "general_machinery": {"code": "PRCG20_2600720001", "name": "はん用・生産用・業務用機器"},
    "electronics": {"code": "PRCG20_2600820001", "name": "電気・電子機器"},
    "transport": {"code": "PRCG20_2600920001", "name": "輸送用機器"},
    "other": {"code": "PRCG20_2601020001", "name": "その他産品・製品"},
}

# Our 5 analysis groups
FIVE_GROUPS = ["energy", "metals", "chemicals", "food", "wood"]

# Domestic CGPI series code for net terms-of-trade calculation
DOMESTIC_CGPI_CODE = "PRCG20_2200000000"
DOMESTIC_CGPI_NAME = "国内企業物価指数 総平均"


def fetch_cgpi_bulk() -> Path:
    """Download BOJ CGPI bulk CSV (ZIP)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "cgpi_m_jp.zip"

    if zip_path.exists():
        print(f"Already exists: {zip_path}")
        return zip_path

    print("Downloading BOJ CGPI bulk data...")
    with httpx.Client(follow_redirects=True, timeout=120) as client:
        resp = client.get(CGPI_BULK_URL)
        resp.raise_for_status()

    zip_path.write_bytes(resp.content)
    print(f"Saved to {zip_path} ({len(resp.content) / 1024 / 1024:.1f} MB)")
    return zip_path


def load_cgpi_raw() -> pd.DataFrame:
    """Load raw CGPI data from bulk ZIP."""
    zip_path = fetch_cgpi_bulk()

    with zipfile.ZipFile(zip_path) as zf:
        csv_name = [n for n in zf.namelist() if n.endswith(".csv")][0]
        with zf.open(csv_name) as f:
            content = f.read()

    df = pd.read_csv(io.BytesIO(content), encoding="shift_jis", low_memory=False)
    return df


def extract_import_prices() -> pd.DataFrame:
    """
    Extract import price indices for all commodity groups.

    Returns
    -------
    pd.DataFrame with columns: date, group, group_ja, value (index, 2020=100)
    """
    cache_path = RAW_DIR / "import_prices_extracted.csv"
    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path, parse_dates=["date"])

    raw = load_cgpi_raw()

    # Column structure: col0=code, col1=description, col2=category, col3+=monthly data
    code_col = raw.columns[0]
    date_cols = [c for c in raw.columns[3:] if str(c).isdigit() and len(str(c)) == 6]

    # Filter to import price series
    target_codes = {v["code"]: k for k, v in IMPORT_PRICE_SERIES.items()}
    mask = raw[code_col].isin(target_codes.keys())
    filtered = raw.loc[mask].copy()

    # Melt to long format
    rows = []
    for _, row in filtered.iterrows():
        code = row[code_col]
        group = target_codes[code]
        group_ja = IMPORT_PRICE_SERIES[group]["name"]

        for date_str in date_cols:
            val = row.get(date_str)
            if pd.notna(val):
                year = int(str(date_str)[:4])
                month = int(str(date_str)[4:6])
                rows.append({
                    "date": pd.Timestamp(year, month, 1),
                    "group": group,
                    "group_ja": group_ja,
                    "value": float(val),
                })

    result = pd.DataFrame(rows)
    result = result.sort_values(["group", "date"]).reset_index(drop=True)

    result.to_csv(cache_path, index=False)
    print(f"Saved to {cache_path} ({len(result)} rows)")
    return result


def extract_domestic_cgpi() -> pd.DataFrame:
    """
    Extract domestic CGPI total average (国内企業物価指数 総平均) from bulk ZIP.

    Used as the reference price for computing net terms-of-trade loss:
        net_change = P_import - P_domestic

    Returns
    -------
    pd.DataFrame with columns: date, value (index, 2020=100)
    """
    cache_path = RAW_DIR / "domestic_cgpi.csv"
    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path, parse_dates=["date"])

    raw = load_cgpi_raw()
    code_col = raw.columns[0]
    date_cols = [c for c in raw.columns[3:] if str(c).isdigit() and len(str(c)) == 6]

    mask = raw[code_col] == DOMESTIC_CGPI_CODE
    row = raw.loc[mask]
    if row.empty:
        raise ValueError(f"Domestic CGPI code {DOMESTIC_CGPI_CODE} not found in bulk data")
    row = row.iloc[0]

    rows = []
    for date_str in date_cols:
        val = row.get(date_str)
        if pd.notna(val):
            year = int(str(date_str)[:4])
            month = int(str(date_str)[4:6])
            rows.append({
                "date": pd.Timestamp(year, month, 1),
                "value": float(val),
            })

    result = pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
    result.to_csv(cache_path, index=False)
    print(f"Saved domestic CGPI to {cache_path} ({len(result)} rows)")
    return result


if __name__ == "__main__":
    df = extract_import_prices()
    print(f"\nTotal rows: {len(df)}")
    print(f"Groups: {df['group'].unique().tolist()}")
    print(f"Date range: {df['date'].min()} to {df['date'].max()}")

    print("\n5 analysis groups (2020=100):")
    for g in FIVE_GROUPS:
        sub = df[df["group"] == g]
        if not sub.empty:
            v2020 = sub[sub["date"].dt.year == 2020]["value"].mean()
            v2023 = sub[sub["date"].dt.year == 2023]["value"].mean()
            v2024 = sub[sub["date"].dt.year == 2024]["value"].mean()
            name = IMPORT_PRICE_SERIES[g]["name"]
            print(f"  {name}: 2020={v2020:.1f}, 2023={v2023:.1f}, 2024={v2024:.1f}")
