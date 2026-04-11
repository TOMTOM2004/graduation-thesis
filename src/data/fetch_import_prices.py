"""
Fetch BOJ Corporate Goods Price Index (CGPI) - Import Price Index.
Uses two BOJ bulk files to cover the full 2015-present range:

- cgpilink1.csv : linked index (1960/01–2019/12), 2020=100 rebased
- cgpi_m_jp.zip : original 2020-base data (2020/01–present)

Both files use identical PRCG20_XXXX series codes, so they can be
concatenated directly to produce a continuous monthly series.
"""

import io
import zipfile
from pathlib import Path

import httpx
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "boj-cgpi"

# BOJ bulk download: all CGPI monthly data (2020/01–present)
CGPI_BULK_URL = "https://www.stat-search.boj.or.jp/info/cgpi_m_jp.zip"

# BOJ linked index: historical chain-linked data (1960/01–2019/12, 2020=100 scale)
CGPI_LINK_URL = "https://www.stat-search.boj.or.jp/info/cgpilink1.csv"

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
    """Download BOJ CGPI bulk CSV (ZIP, 2020/01–present)."""
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


def fetch_cgpi_link() -> Path:
    """Download BOJ CGPI linked index CSV (1960/01–2019/12, 2020=100 scale)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RAW_DIR / "cgpilink1.csv"

    if csv_path.exists():
        print(f"Already exists: {csv_path}")
        return csv_path

    print("Downloading BOJ CGPI linked index...")
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        resp = client.get(CGPI_LINK_URL)
        resp.raise_for_status()

    csv_path.write_bytes(resp.content)
    print(f"Saved to {csv_path} ({len(resp.content) / 1024:.0f} KB)")
    return csv_path


def load_cgpi_raw() -> pd.DataFrame:
    """Load raw CGPI data from bulk ZIP (2020/01–present)."""
    zip_path = fetch_cgpi_bulk()

    with zipfile.ZipFile(zip_path) as zf:
        csv_name = [n for n in zf.namelist() if n.endswith(".csv")][0]
        with zf.open(csv_name) as f:
            content = f.read()

    df = pd.read_csv(io.BytesIO(content), encoding="shift_jis", low_memory=False)
    return df


def load_cgpi_link_raw() -> pd.DataFrame:
    """Load BOJ CGPI linked index CSV (1960/01–2019/12)."""
    csv_path = fetch_cgpi_link()
    df = pd.read_csv(csv_path, encoding="shift_jis", low_memory=False)
    return df


def _melt_cgpi_df(df: pd.DataFrame, target_codes: dict[str, str]) -> pd.DataFrame:
    """
    Common helper: melt a wide-format CGPI DataFrame into long format.

    Parameters
    ----------
    df : wide-format CGPI DataFrame (col0=code, col1=desc, col2=cat, col3+=yyyymm values)
    target_codes : {series_code: group_name}

    Returns long DataFrame with columns: date, group, group_ja, value
    """
    code_col = df.columns[0]
    date_cols = [c for c in df.columns[3:] if str(c).isdigit() and len(str(c)) == 6]

    mask = df[code_col].isin(target_codes.keys())
    filtered = df.loc[mask].copy()

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

    return pd.DataFrame(rows)


def extract_import_prices() -> pd.DataFrame:
    """
    Extract import price indices for all commodity groups.

    Combines two BOJ sources for a continuous 2015–present series (2020=100):
    - cgpilink1.csv : 2015/01–2019/12 (linked, chain-spliced to 2020=100)
    - cgpi_m_jp.zip : 2020/01–present (original 2020-base)

    Returns
    -------
    pd.DataFrame with columns: date, group, group_ja, value (index, 2020=100)
    """
    cache_path = RAW_DIR / "import_prices_extracted.csv"
    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path, parse_dates=["date"])

    target_codes = {v["code"]: k for k, v in IMPORT_PRICE_SERIES.items()}

    # --- Part 1: 2020-present from ZIP ---
    raw_zip = load_cgpi_raw()
    df_zip = _melt_cgpi_df(raw_zip, target_codes)

    # --- Part 2: 2015-2019 from linked index CSV ---
    raw_link = load_cgpi_link_raw()
    df_link = _melt_cgpi_df(raw_link, target_codes)
    df_link = df_link[df_link["date"].dt.year.between(2015, 2019)]

    # --- Combine: link (pre-2020) + zip (2020+) ---
    result = (
        pd.concat([df_link, df_zip], ignore_index=True)
        .sort_values(["group", "date"])
        .drop_duplicates(subset=["group", "date"])
        .reset_index(drop=True)
    )

    result.to_csv(cache_path, index=False)
    print(f"Saved to {cache_path} ({len(result)} rows, "
          f"{result['date'].min().date()} – {result['date'].max().date()})")
    return result


def extract_domestic_cgpi() -> pd.DataFrame:
    """
    Extract domestic CGPI total average (国内企業物価指数 総平均).

    Combines cgpilink1.csv (2015-2019) and cgpi_m_jp.zip (2020-present).

    Returns
    -------
    pd.DataFrame with columns: date, value (index, 2020=100)
    """
    cache_path = RAW_DIR / "domestic_cgpi.csv"
    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path, parse_dates=["date"])

    def _extract_single(df: pd.DataFrame, filter_years=None) -> pd.DataFrame:
        code_col = df.columns[0]
        date_cols = [c for c in df.columns[3:] if str(c).isdigit() and len(str(c)) == 6]
        mask = df[code_col] == DOMESTIC_CGPI_CODE
        row = df.loc[mask]
        if row.empty:
            return pd.DataFrame(columns=["date", "value"])
        row = row.iloc[0]
        rows = []
        for date_str in date_cols:
            val = row.get(date_str)
            if pd.notna(val):
                year = int(str(date_str)[:4])
                month = int(str(date_str)[4:6])
                if filter_years and year not in filter_years:
                    continue
                rows.append({"date": pd.Timestamp(year, month, 1), "value": float(val)})
        return pd.DataFrame(rows)

    df_link = _extract_single(load_cgpi_link_raw(), filter_years=range(2015, 2020))
    df_zip = _extract_single(load_cgpi_raw())

    result = (
        pd.concat([df_link, df_zip], ignore_index=True)
        .sort_values("date")
        .drop_duplicates(subset=["date"])
        .reset_index(drop=True)
    )

    result.to_csv(cache_path, index=False)
    print(f"Saved domestic CGPI to {cache_path} ({len(result)} rows, "
          f"{result['date'].min().date()} – {result['date'].max().date()})")
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
