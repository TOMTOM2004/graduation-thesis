"""
Phase 2 Step 2a-3: Cost-push inflation identification.

Identification strategy:
    CPI_change(cat) = α + β × import_content(cat) + ε

    β = pass-through coefficient: 1% higher import content → β% higher price increase
    This estimates the cost-push component vs. demand-pull baseline (α).

We use cross-category variation in import content as the identifying instrument:
    - If a category has higher import content, its price increase should be
      proportionately larger under a cost-push shock (supply-side)
    - Demand-pull shocks would produce more uniform price increases across categories

Data:
    - LHS: CPI change by category (e-Stat, 消費者物価指数 2020=100)
    - RHS: import content by category (bridge matrix × Leontief import content)

Sample: 2015-2025, cross-section by category × time-period
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.analysis.bridge_matrix import (
    compute_hh_category_import_content,
    classify_necessity_discretionary,
    HH_CATEGORY_MAP,
)

DATA_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
PRICE_DIR = DATA_PROCESSED / "price-indices"

# CPI cat01 codes in 家計調査 → CPI category codes
# Mapping from household survey major categories to CPI 総合指数 sub-codes
# CPI uses different classification but aligns at major category level
HH_TO_CPI_CODE: dict[int, str] = {
    60:  "食料",           # food
    102: "住居",           # housing
    107: "光熱・水道",      # energy/utilities
    112: "家具・家事用品",   # furniture
    122: "被服及び履物",     # clothing
    140: "保健医療",        # health
    145: "交通・通信",      # transport/comms
    152: "教育",           # education
    156: "教養娯楽",        # recreation
    165: "諸雑費",         # other (closest match)
}


def load_cpi_by_major_category() -> pd.DataFrame:
    """
    Load CPI data and extract annual index for each major expenditure category.

    Returns
    -------
    pd.DataFrame with columns: year, hh_cat_code, hh_cat_name, cpi_name_matched,
                                cpi_index (annual average, 2020=100)
    """
    PRICE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = PRICE_DIR / "cpi_major_categories.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    cpi_file = DATA_RAW / "cpi" / "cpi_category_2015_2025.csv"
    cpi = pd.read_csv(cpi_file)

    print("CPI columns:", cpi.columns.tolist())
    print("CPI cat01 sample:", cpi["cat01_name"].unique()[:20])

    # Parse time code to year
    cpi["year"] = cpi["time_code"].astype(str).str[:4].astype(int)

    # Filter to annual data (monthly time codes end with 01-12, annual with 00)
    # Annual codes: YYYYMM format, we want the annual-average concept
    # From fetch_cpi.py, time_from = "201500" and time_to = "202512"
    # Monthly codes are like 201501...202512, annual codes might be 201500
    # Let's filter to months and compute annual average
    monthly_mask = cpi["time_code"].astype(str).str[4:6].isin([
        "01","02","03","04","05","06","07","08","09","10","11","12"
    ])
    cpi_monthly = cpi[monthly_mask].copy()

    rows = []
    for hh_code, cpi_name in HH_TO_CPI_CODE.items():
        # Match by name
        matched = cpi_monthly[cpi_monthly["cat01_name"] == cpi_name]
        if matched.empty:
            # Try partial match
            matched = cpi_monthly[cpi_monthly["cat01_name"].str.contains(cpi_name[:3], na=False)]

        if matched.empty:
            print(f"  Warning: No CPI match for '{cpi_name}' (hh_code={hh_code})")
            continue

        # Use the first (broadest) match
        matched = matched[matched["cat01_name"] == matched["cat01_name"].iloc[0]]
        cpi_name_matched = matched["cat01_name"].iloc[0]

        # Annual average
        annual = (
            matched.groupby("year")["value"]
            .mean()
            .reset_index()
            .rename(columns={"value": "cpi_index"})
        )

        annual["hh_cat_code"] = hh_code
        annual["hh_cat_name"] = HH_CATEGORY_MAP[hh_code]["name"]
        annual["cpi_name_matched"] = cpi_name_matched
        rows.append(annual)

    df = pd.concat(rows, ignore_index=True)
    df = df[["year", "hh_cat_code", "hh_cat_name", "cpi_name_matched", "cpi_index"]]
    df.to_csv(cache_path, index=False)
    print(f"Saved CPI by major category: {cache_path} ({len(df)} rows)")
    return df


def compute_cpi_changes() -> pd.DataFrame:
    """
    Compute CPI change (%) for each category vs. 2020 base and vs. 2015-2019 average.

    Returns
    -------
    pd.DataFrame with columns: year, hh_cat_code, hh_cat_name,
                                cpi_index, cpi_change_vs_2020, cpi_change_vs_baseline
    """
    PRICE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = PRICE_DIR / "cpi_changes.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    cpi_df = load_cpi_by_major_category()

    # 2015-2019 baseline average per category
    baseline = (
        cpi_df[cpi_df["year"].between(2015, 2019)]
        .groupby("hh_cat_code")["cpi_index"]
        .mean()
        .rename("baseline_avg")
    )

    cpi_df = cpi_df.merge(baseline, on="hh_cat_code")
    cpi_df["cpi_change_vs_2020"] = cpi_df["cpi_index"] - 100.0       # vs 2020=100 base
    cpi_df["cpi_change_vs_baseline"] = cpi_df["cpi_index"] - cpi_df["baseline_avg"]  # vs 2015-2019 avg

    cpi_df.to_csv(cache_path, index=False)
    return cpi_df


def run_cost_push_regression() -> dict:
    """
    Run cross-section regression: CPI_change = α + β × import_content + ε

    Run for multiple years to track how pass-through evolved.
    Also run separately for necessity vs. discretionary categories.

    Returns
    -------
    dict: {year: regression_results_dict}
    """
    PRICE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = PRICE_DIR / "cost_push_regression.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    cpi_changes = compute_cpi_changes()
    nd_df = classify_necessity_discretionary()

    # Merge import content and necessity flag
    ic_df = compute_hh_category_import_content()
    analysis = cpi_changes.merge(
        ic_df[["hh_cat_code", "import_content"]],
        on="hh_cat_code"
    ).merge(
        nd_df[["hh_cat_code", "is_necessity"]],
        on="hh_cat_code",
        how="left"
    )

    rows = []
    for year in range(2020, 2026):
        yr_data = analysis[analysis["year"] == year].dropna(subset=["cpi_change_vs_2020", "import_content"])

        if len(yr_data) < 5:
            continue

        X = sm.add_constant(yr_data["import_content"])
        y = yr_data["cpi_change_vs_2020"]
        model = sm.OLS(y, X).fit()

        rows.append({
            "year": year,
            "n_categories": len(yr_data),
            "alpha": round(model.params.get("const", np.nan), 3),
            "beta": round(model.params.get("import_content", np.nan), 3),
            "beta_se": round(model.bse.get("import_content", np.nan), 3),
            "beta_tstat": round(model.tvalues.get("import_content", np.nan), 3),
            "r_squared": round(model.rsquared, 3),
            "p_value": round(model.pvalues.get("import_content", np.nan), 4),
        })

        # Also print summary
        print(f"\n[{year}] CPI change = α + β × import_content")
        print(f"  α={rows[-1]['alpha']:.2f}pp, β={rows[-1]['beta']:.2f}pp, "
              f"R²={rows[-1]['r_squared']:.2f}, p={rows[-1]['p_value']:.4f}")
        for _, row in yr_data.sort_values("import_content", ascending=False).iterrows():
            necessity_tag = "N" if row["is_necessity"] else "D"
            print(f"    [{necessity_tag}] {row['hh_cat_name']:12s}: IC={row['import_content']:.2f}  "
                  f"ΔCPI={row['cpi_change_vs_2020']:+.1f}pp")

    result_df = pd.DataFrame(rows)
    result_df.to_csv(cache_path, index=False)
    print(f"\nSaved regression results to {cache_path}")
    return result_df


if __name__ == "__main__":
    print("=== CPI by Major Category ===")
    cpi_df = load_cpi_by_major_category()
    pivot = cpi_df.pivot(index="year", columns="hh_cat_name", values="cpi_index")
    print(pivot.round(1).to_string())

    print("\n=== Cost-Push Identification Regression ===")
    reg_df = run_cost_push_regression()
    if not isinstance(reg_df, dict):
        print(reg_df[["year", "alpha", "beta", "beta_tstat", "r_squared", "p_value"]].to_string(index=False))
