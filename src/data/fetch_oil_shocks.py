"""
Fetch the Känzig (2021 AER) oil supply news shock series.

Citation:
    Känzig, Diego R. (2021), "The Macroeconomic Effects of Oil Supply News:
    Evidence from OPEC Announcements", American Economic Review 111(4),
    pp. 1092-1125. Data licensed CC-BY 4.0.

Source: GitHub repo dkaenzig/oilsupplynews (default branch: master).
Latest vintage xlsx (oilSupplyNewsShocks_2025M12.xlsx) contains 4 sheets:

- "Daily"             : daily oil futures price surprises around OPEC
                        announcements (Front, 1M-12M contracts, PC = first
                        principal component), full sample.
- "Monthly"           : monthly aggregates — "Oil supply surprise series"
                        (monthly sum of the daily futures surprises) and
                        "Oil supply news shock" (structural shock extracted
                        from the VAR, instrumented by the surprise series),
                        1975M01-present.
- "Daily (pre-Covid)" : same as "Daily" but PC estimated on the pre-Covid
                        sample (through 2019).
- "Monthly (pre-Covid)": same as "Monthly", pre-Covid-estimated variant.

This script downloads the raw xlsx unchanged to data/raw/oil-shocks/ and
tidies the two MONTHLY sheets into a single CSV
(data/raw/oil-shocks/oil_supply_news_monthly.csv) with columns:

- date                              : YYYY-MM-01
- oil_supply_surprise               : monthly futures-price surprise (full sample)
- oil_supply_news_shock             : VAR-extracted structural news shock (full sample)
- oil_supply_surprise_precovid      : pre-Covid-estimated variant of the surprise
- oil_supply_news_shock_precovid    : pre-Covid-estimated variant of the news shock
"""

import json
from pathlib import Path

import httpx
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "oil-shocks"

GITHUB_REPO = "dkaenzig/oilsupplynews"
LATEST_VINTAGE = "oilSupplyNewsShocks_2025M12.xlsx"
# NOTE: the repo's default branch is "master", not "main"
RAW_URL_TEMPLATE = "https://raw.githubusercontent.com/{repo}/master/{fname}"
API_CONTENTS_URL = "https://api.github.com/repos/{repo}/contents/"

# Sheet name -> column suffix for the tidy CSV
MONTHLY_SHEETS = {
    "Monthly": "",
    "Monthly (pre-Covid)": "_precovid",
}

# Original xlsx column -> snake_case base name
COLUMN_MAP = {
    "Oil supply surprise series": "oil_supply_surprise",
    "Oil supply news shock": "oil_supply_news_shock",
}


def _find_latest_vintage(client: httpx.Client) -> str:
    """List the repo contents via the GitHub API and pick the latest vintage."""
    resp = client.get(API_CONTENTS_URL.format(repo=GITHUB_REPO))
    resp.raise_for_status()
    names = [
        item["name"]
        for item in json.loads(resp.text)
        if item["name"].startswith("oilSupplyNewsShocks_")
        and item["name"].endswith(".xlsx")
    ]
    if not names:
        raise RuntimeError(f"No oilSupplyNewsShocks_*.xlsx found in {GITHUB_REPO}")
    # Vintage tag YYYYMmm sorts lexicographically
    return sorted(names)[-1]


def fetch_oil_shocks_xlsx() -> Path:
    """Download the latest-vintage shock xlsx (idempotent: skip if cached)."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # If any vintage is already cached, reuse the newest cached one
    cached = sorted(RAW_DIR.glob("oilSupplyNewsShocks_*.xlsx"))
    if cached:
        print(f"Already exists: {cached[-1]}")
        return cached[-1]

    with httpx.Client(follow_redirects=True, timeout=60) as client:
        fname = LATEST_VINTAGE
        url = RAW_URL_TEMPLATE.format(repo=GITHUB_REPO, fname=fname)
        print(f"Downloading {url} ...")
        resp = client.get(url)
        if resp.status_code == 404:
            print("404 — listing repo contents to find the latest vintage...")
            fname = _find_latest_vintage(client)
            url = RAW_URL_TEMPLATE.format(repo=GITHUB_REPO, fname=fname)
            print(f"Downloading {url} ...")
            resp = client.get(url)
        resp.raise_for_status()

    xlsx_path = RAW_DIR / fname
    xlsx_path.write_bytes(resp.content)
    print(f"Saved to {xlsx_path} ({len(resp.content) / 1024:.0f} KB)")
    return xlsx_path


def tidy_monthly_shocks() -> pd.DataFrame:
    """
    Parse the monthly sheets into a tidy DataFrame.

    Returns
    -------
    pd.DataFrame with columns: date (YYYY-MM-01), oil_supply_surprise,
    oil_supply_news_shock, and their _precovid variants.
    """
    xlsx_path = fetch_oil_shocks_xlsx()
    xl = pd.ExcelFile(xlsx_path)
    print(f"Sheets found: {xl.sheet_names}")

    frames = []
    for sheet, suffix in MONTHLY_SHEETS.items():
        if sheet not in xl.sheet_names:
            raise RuntimeError(f"Expected sheet '{sheet}' not in {xl.sheet_names}")
        df = xl.parse(sheet)
        # Date column formatted "1975M01" -> Timestamp(1975, 1, 1)
        df["date"] = pd.to_datetime(df["Date"].astype(str), format="%YM%m")
        df = df.rename(columns={k: v + suffix for k, v in COLUMN_MAP.items()})
        frames.append(df.set_index("date")[[v + suffix for v in COLUMN_MAP.values()]])

    result = frames[0].join(frames[1:], how="outer").sort_index().reset_index()

    out_path = RAW_DIR / "oil_supply_news_monthly.csv"
    result.to_csv(out_path, index=False, date_format="%Y-%m-%d")
    print(f"Saved tidy CSV to {out_path}")
    return result


if __name__ == "__main__":
    df = tidy_monthly_shocks()

    print(f"\nColumns: {df.columns.tolist()}")
    print(f"n_obs: {len(df)}")
    print(f"Period: {df['date'].min().date()} – {df['date'].max().date()}")

    value_cols = [c for c in df.columns if c != "date"]
    all_nan = [c for c in value_cols if df[c].isna().all()]
    print(f"All-NaN columns: {all_nan or 'none'}")

    print("\nBasic stats:")
    print(df[value_cols].describe().round(3).to_string())

    tail = df[df["date"] >= "2021-01-01"]
    print(f"\n2021-01 onward ({len(tail)} rows):")
    with pd.option_context("display.max_rows", None, "display.width", 200):
        print(tail.to_string(index=False))
