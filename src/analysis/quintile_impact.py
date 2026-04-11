"""
Phase 2 Step 2b: Income quintile impact analysis.

For each income quintile (Q1-Q5):
    real_consumption_change(q, t) = Σ_cat [expenditure_share(q, cat) × CPI_change(cat, t)]

This measures the effective price increase faced by each quintile,
weighted by their actual expenditure patterns.

Key hypothesis: Lower quintiles (Q1, Q2) face higher effective inflation
due to their higher share of necessities (food, energy) which have
higher import content.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.bridge_matrix import HH_CATEGORY_MAP
from src.analysis.cost_push_id import compute_cpi_changes, HH_TO_CPI_CODE

DATA_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
RESULTS_DIR = DATA_PROCESSED / "simulation-params"

QUINTILE_LABELS = {0: "平均", 1: "Q1(最低)", 2: "Q2", 3: "Q3", 4: "Q4", 5: "Q5(最高)"}


def load_expenditure_shares(year: int = 2019) -> pd.DataFrame:
    """
    Load household expenditure shares by quintile × major category from 家計調査.

    Parameters
    ----------
    year : int
        Year to use for expenditure structure (default: 2019 = pre-COVID baseline)

    Returns
    -------
    pd.DataFrame: index=quintile (0-5), columns=hh_cat_code, values=expenditure share
    """
    hh_file = DATA_RAW / "household-survey" / "household_quintile_2015_2024.csv"
    hh = pd.read_csv(hh_file)

    # Filter to target year
    hh_yr = hh[hh["time_code"] == int(f"{year}000000")].copy()

    # Total consumption expenditure (cat01_code=59) per quintile (nominal JPY/month)
    total_cons = (
        hh_yr[hh_yr["cat01_code"] == 59][["cat03_code", "value"]]
        .set_index("cat03_code")["value"]
        .to_dict()
    )

    # Extract major category expenditure
    target_codes = list(HH_CATEGORY_MAP.keys())

    rows = {}
    for q_code in range(0, 6):
        q_total = total_cons.get(q_code, np.nan)
        row = {}
        for hh_code in target_codes:
            cat_data = hh_yr[
                (hh_yr["cat01_code"] == hh_code) &
                (hh_yr["cat03_code"] == q_code)
            ]["value"]

            if cat_data.empty or pd.isna(q_total) or q_total == 0:
                row[hh_code] = np.nan
            else:
                row[hh_code] = float(cat_data.iloc[0]) / float(q_total)

        rows[q_code] = row

    df = pd.DataFrame(rows).T
    df.index.name = "quintile"
    df.columns.name = "hh_cat_code"
    return df


def compute_quintile_inflation_burden() -> pd.DataFrame:
    """
    Compute effective price increase burden by income quintile and year.

    effective_inflation(q, t) = Σ_cat [share(q, cat) × ΔCPI(cat, t)]

    Returns
    -------
    pd.DataFrame with columns: year, quintile, quintile_label, effective_inflation_pp,
                                plus per-category contributions
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = RESULTS_DIR / "quintile_inflation_burden.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    # Expenditure shares (fixed at 2019 structure)
    shares = load_expenditure_shares(year=2019)

    # CPI changes by category and year
    cpi_df = compute_cpi_changes()

    rows = []
    for year in range(2015, 2026):
        yr_cpi = cpi_df[cpi_df["year"] == year].set_index("hh_cat_code")

        for q_code in range(0, 6):
            if q_code not in shares.index:
                continue

            q_shares = shares.loc[q_code]
            total_burden = 0.0
            contributions = {}

            for hh_code in HH_CATEGORY_MAP.keys():
                share = q_shares.get(hh_code, np.nan)
                if hh_code in yr_cpi.index:
                    delta_cpi = yr_cpi.loc[hh_code, "cpi_change_vs_baseline"]
                else:
                    delta_cpi = np.nan

                if pd.notna(share) and pd.notna(delta_cpi):
                    contrib = share * delta_cpi
                    total_burden += contrib
                    contributions[f"contrib_{hh_code}"] = round(contrib, 4)

            rows.append({
                "year": year,
                "quintile": q_code,
                "quintile_label": QUINTILE_LABELS.get(q_code, str(q_code)),
                "effective_inflation_pp": round(total_burden, 4),
                **contributions,
            })

    df = pd.DataFrame(rows)
    df.to_csv(cache_path, index=False)
    print(f"Saved quintile inflation burden to {cache_path} ({len(df)} rows)")
    return df


def compute_quintile_real_income_change() -> pd.DataFrame:
    """
    Compute real income change by quintile.

    real_income_change(q, t) = nominal_income_change(q, t) - effective_inflation(q, t)

    Since we focus on the inflation burden (not nominal income tracking),
    we report the effective inflation differential: Q1 burden minus Q5 burden.

    Returns summary DataFrame showing regressive/progressive pattern.
    """
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = RESULTS_DIR / "quintile_real_income.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    burden_df = compute_quintile_inflation_burden()

    # Pivot to year × quintile
    pivot = burden_df.pivot(index="year", columns="quintile_label", values="effective_inflation_pp")

    # Regressive gap: Q1 burden - Q5 burden (positive = regressive)
    if "Q1(最低)" in pivot.columns and "Q5(最高)" in pivot.columns:
        pivot["Q1_minus_Q5_gap"] = pivot["Q1(最低)"] - pivot["Q5(最高)"]
    else:
        pivot["Q1_minus_Q5_gap"] = np.nan

    pivot.reset_index(inplace=True)
    pivot.to_csv(cache_path, index=False)
    print(f"Saved quintile real income comparison to {cache_path}")
    return pivot


if __name__ == "__main__":
    print("=== Expenditure Shares by Quintile (2019) ===")
    shares = load_expenditure_shares(2019)
    # Show major categories
    cat_names = {code: cat["name"] for code, cat in HH_CATEGORY_MAP.items()}
    shares_named = shares.rename(columns=cat_names)
    print(shares_named.round(3).to_string())

    print("\n=== Effective Inflation Burden by Quintile ===")
    burden = compute_quintile_inflation_burden()
    pivot = burden.pivot(index="year", columns="quintile_label", values="effective_inflation_pp")
    print(pivot.round(2).to_string())

    print("\n=== Regressive Gap: Q1 vs Q5 Effective Inflation ===")
    gap_df = compute_quintile_real_income_change()
    print(gap_df[["year", "Q1(最低)", "Q5(最高)", "Q1_minus_Q5_gap"]].round(2).to_string(index=False))
