"""
Phase 3 Step 3-1: IO価格モデル（レオンチェフ価格方程式）。

レオンチェフ価格方程式:
    p = (I - A^T)^{-1} * m

    p_i: 産業 i の生産者価格変化率（pp, 2020=100 基準）
    A  : 投入係数行列（108 x 108）
    m_i: 産業 i の直接輸入コスト変化 = direct_import_ratio_i × ΔP_group(i)

5グループ別の輸入価格変化を直接輸入係数経由で各産業に割り当て、
レオンチェフ逆行列で間接波及を含む生産者価格変化を求める。
その後ブリッジ行列でCPI中分類消費費目別の価格変化に変換する。

2仕様で並列実装:
    (i)  β=1.0: レオンチェフ原形（完全転嫁）
    (ii) β=BETA_EMPIRICAL（cost_push_panel_results.csv spec iii から読込・≈0.43）: 実証スケーリング（Phase 2a-3 パネルOLS 推定値）

競争的輸入財（衣料・履物）は転嫁係数を 0 に設定（DEC-010）。
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.io_utils import (
    load_io_table,
    compute_input_coefficients,
    compute_leontief_inverse,
)
from src.analysis.import_content import SECTOR_GROUP_MAP, GROUPS
from src.analysis.bridge_matrix_mid import CPI_MID_CATEGORY_MAP

DATA_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
SIM_DIR = DATA_PROCESSED / "simulation-params"

def _load_beta_empirical() -> float:
    """Phase 2a-3 パネルOLS spec(iii) の β を結果CSVから読む（DEC-019: 結果数値のハードコード禁止・回帰再実行に自動追随）"""
    results_csv = DATA_PROCESSED / "price-indices" / "cost_push_panel_results.csv"
    if not results_csv.exists():
        raise RuntimeError(
            f"{results_csv} が存在しない。先に `python -m src.analysis.cost_push_panel` を実行すること"
            "（README「再現手順」参照。本モジュールは import 時に β を読み込む）"
        )
    df = pd.read_csv(results_csv)
    row = df[df["仕様"].str.contains("競争的輸入財除外", na=False)]
    if len(row) != 1:
        raise RuntimeError("spec (iii) が cost_push_panel_results.csv に見つからない。先に src/analysis/cost_push_panel.py を実行すること")
    return float(row["β"].iloc[0])

# Empirical pass-through coefficient (Phase 2a-3 panel OLS, spec iii)
BETA_EMPIRICAL = _load_beta_empirical()

# Koyck partial adjustment: annual pass-through rate
# δ=0.55 は calibration（推定値ではない）。独立グリッド探索では RMSE 最小は δ≈0.60、
# ただし RMSE 曲面は [0.5, 0.7] でほぼ平坦（弱識別）— design-review C-3 / DEC-020。
# Economic interpretation: 55% of import cost increase is passed through within one year
# Half-life ≈ 10.4 months. Sensitivity range: 0.4, 0.55, 0.7, 1.0
DELTA_KOYCK = 0.55

# CPI categories with near-zero pass-through (competitive imports, DEC-010)
COMPETITIVE_IMPORT_CATEGORIES = {"衣料", "履物類"}


# --------------------------------------------------------------------------- #
# 1. Import price shock vector                                                 #
# --------------------------------------------------------------------------- #

def build_import_price_shock_vector(
    year: int,
    base_year: int = 2020,
) -> pd.Series:
    """
    Construct sectoral import price shock vector m (108 sectors).

    m_i = direct_import_ratio_i × (P_group(i) / P_group(i, base) - 1)
        = direct_import_ratio_i × ΔP_group(i)   [as fraction, not pp]

    For sectors not in the 5 groups, use the aggregate total import price change.

    Returns
    -------
    pd.Series index=sector_code, values=m_i (fractional change)
    """
    # Load CGPI group-level annual averages
    cgpi = pd.read_csv(DATA_RAW / "boj-cgpi" / "import_prices_extracted.csv", parse_dates=["date"])
    cgpi["year"] = cgpi["date"].dt.year
    annual = (
        cgpi.groupby(["year", "group"])["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "price_index"})
    )

    # Extract base-year and target-year indices
    def _get_index(grp: str, yr: int) -> float:
        row = annual[(annual["group"] == grp) & (annual["year"] == yr)]
        if row.empty:
            return np.nan
        return row["price_index"].iloc[0]

    base_indices = {g: _get_index(g, base_year) for g in GROUPS + ["total"]}
    target_indices = {g: _get_index(g, year) for g in GROUPS + ["total"]}

    # Fractional change per group: (P_t / P_base - 1)
    group_change: dict[str, float] = {}
    for g in GROUPS + ["total"]:
        b = base_indices[g]
        t = target_indices[g]
        if b and b > 0 and t:
            group_change[g] = (t / b) - 1.0
        else:
            group_change[g] = 0.0

    # Load sector-level data for direct import ratio
    ic_df = pd.read_csv(DATA_PROCESSED / "import-content" / "sector_import_content.csv")
    # sector_code is stored as integer (e.g. 11); normalize to 3-digit zero-padded string
    ic_df["sector_code"] = ic_df["sector_code"].astype(str).str.zfill(3)
    ic_df = ic_df.set_index("sector_code")

    # Load IO table for sector list completeness
    io_data = load_io_table()
    sector_codes = io_data["sector_codes"]

    m = pd.Series(0.0, index=sector_codes, name=f"m_{year}")
    for code in sector_codes:
        if code in ic_df.index:
            group = ic_df.loc[code, "group"]
            direct_ratio = ic_df.loc[code, "direct_import_ratio"]
            if pd.isna(direct_ratio):
                direct_ratio = 0.0
            delta_p = group_change.get(group, group_change["total"])
        else:
            direct_ratio = 0.0
            delta_p = group_change["total"]
        m[code] = direct_ratio * delta_p

    return m


# --------------------------------------------------------------------------- #
# 2. Leontief price model: sector-level producer price changes                #
# --------------------------------------------------------------------------- #

def run_leontief_price_model(
    year: int,
    base_year: int = 2020,
) -> pd.DataFrame:
    """
    Apply Leontief price equations to compute sector-level producer price changes.

    Producer price change vector:
        p = (I - A^T)^{-1} * m

    Returns
    -------
    pd.DataFrame with columns:
        sector_code, sector_name, group,
        m_i          : direct import shock (fraction)
        p_leontief   : Leontief full pass-through (fraction, β=1)
        p_empirical  : Empirically scaled (fraction, β=BETA_EMPIRICAL)
        p_leontief_pp: pp change (×100)
        p_empirical_pp: pp change (×100)
    """
    io_data = load_io_table()
    A = compute_input_coefficients(io_data)
    L = compute_leontief_inverse(A)

    m = build_import_price_shock_vector(year, base_year)
    # Align m to A's index (should match, but ensure)
    m = m.reindex(A.index, fill_value=0.0)

    # Leontief price equation: p = (I - A^T)^{-1} * m = L^T * m
    # Note: L = (I - A)^{-1}, so L^T = ((I - A)^T)^{-1} = (I - A^T)^{-1}
    p_leontief = pd.Series(
        L.values.T @ m.values,
        index=io_data["sector_codes"],
        name="p_leontief",
    )

    p_empirical = p_leontief * BETA_EMPIRICAL

    # Compile results
    ic_df = pd.read_csv(DATA_PROCESSED / "import-content" / "sector_import_content.csv")
    ic_df["sector_code"] = ic_df["sector_code"].astype(str).str.zfill(3)
    ic_df = ic_df.set_index("sector_code")

    rows = []
    for code in io_data["sector_codes"]:
        sector_name = io_data["sector_names"][io_data["sector_codes"].index(code)]
        group = ic_df.loc[code, "group"] if code in ic_df.index else "other"
        rows.append({
            "sector_code": code,
            "sector_name": sector_name,
            "group": group,
            "m_i": m[code],
            "p_leontief": p_leontief[code],
            "p_empirical": p_empirical[code],
            "p_leontief_pp": p_leontief[code] * 100,
            "p_empirical_pp": p_empirical[code] * 100,
        })

    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# 3. Bridge to CPI mid-category consumer prices                               #
# --------------------------------------------------------------------------- #

def map_to_cpi_categories(
    sector_price_df: pd.DataFrame,
    year: int,
) -> pd.DataFrame:
    """
    Convert sector-level producer price changes to CPI mid-category price changes
    using the bridge matrix (consumption-weighted average).

    For competitive import categories (衣料・履物): set pass-through to 0 (DEC-010).

    Returns
    -------
    pd.DataFrame with columns:
        cpi_mid_name, cpi_code, group,
        is_competitive_import,
        delta_cpi_leontief_pp  : Leontief full pass-through
        delta_cpi_empirical_pp : Empirically scaled (β=BETA_EMPIRICAL)
        delta_cpi_zero_pp      : For competitive imports (always 0)
    """
    bridge = pd.read_csv(
        DATA_PROCESSED / "bridge-matrix" / "bridge_matrix_mid.csv",
        index_col=0,
    )

    # Producer price series (indexed by sector code)
    p_leontief = sector_price_df.set_index("sector_code")["p_leontief_pp"]
    p_empirical = sector_price_df.set_index("sector_code")["p_empirical_pp"]

    rows = []
    for cat_name, cat_info in CPI_MID_CATEGORY_MAP.items():
        cpi_code = cat_info["cpi_code"]
        is_comp = cat_info.get("is_competitive_import", False)

        if cat_name not in bridge.index:
            continue

        weights = bridge.loc[cat_name]
        # Only sectors present in sector_price_df
        common = weights.index.intersection(p_leontief.index)
        w = weights[common]
        w_sum = w.sum()

        if w_sum > 0 and not is_comp:
            delta_leontief = (w * p_leontief[common]).sum() / w_sum
            delta_empirical = (w * p_empirical[common]).sum() / w_sum
        else:
            # Competitive imports: near-zero pass-through (DEC-010)
            delta_leontief = 0.0
            delta_empirical = 0.0

        rows.append({
            "cpi_mid_name": cat_name,
            "cpi_code": cpi_code,
            "group": cat_info.get("group", "other"),
            "is_competitive_import": is_comp,
            "delta_cpi_leontief_pp": delta_leontief,
            "delta_cpi_empirical_pp": delta_empirical,
        })

    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #
# 4. Koyck partial adjustment lag                                              #
# --------------------------------------------------------------------------- #

def apply_koyck_lag(
    shock_by_year: dict[int, pd.Series],
    delta: float = DELTA_KOYCK,
) -> dict[int, pd.Series]:
    """
    Apply Koyck partial adjustment to the sectoral import shock series.

    m_eff(t) = δ × m(t) + (1-δ) × m_eff(t-1)

    Converts instantaneous annual shocks into lagged effective shocks that
    better approximate the delayed consumer price pass-through observed in data.

    Parameters
    ----------
    shock_by_year : dict mapping year (int) → sectoral shock vector (pd.Series)
    delta : annual pass-through rate (0 < δ ≤ 1).
            δ=0.55 is the RMSE-minimizing estimate from 2021-2024 validation data.
            δ=1.0 reduces to the static (instantaneous) model.

    Returns
    -------
    dict mapping year → Koyck-adjusted shock vector
    """
    years_sorted = sorted(shock_by_year.keys())
    m_eff_prev = pd.Series(0.0, index=shock_by_year[years_sorted[0]].index)
    result: dict[int, pd.Series] = {}
    for yr in years_sorted:
        m_t = shock_by_year[yr]
        m_eff = delta * m_t + (1 - delta) * m_eff_prev
        result[yr] = m_eff
        m_eff_prev = m_eff
    return result


# --------------------------------------------------------------------------- #
# 5. Multi-year run + cache                                                    #
# --------------------------------------------------------------------------- #

def run_io_price_model_all_years(
    years: list[int] | None = None,
    base_year: int = 2020,
    koyck: bool = True,
    delta: float = DELTA_KOYCK,
    force: bool = False,
) -> pd.DataFrame:
    """
    Run the IO price model for all analysis years and return CPI-category-level
    price changes.

    Parameters
    ----------
    years : list of years to run. Default: 2015-2019, 2021-2024.
    base_year : reference year for price index (default 2020).
    koyck : if True, apply Koyck partial adjustment (δ=delta) before Leontief.
            Adds delta_cpi_koyck_pp column to output.
    delta : Koyck annual pass-through rate (only used when koyck=True).
    force : recompute even if cache exists.

    Returns
    -------
    pd.DataFrame with columns:
        year, cpi_mid_name, cpi_code, group, is_competitive_import,
        delta_cpi_leontief_pp, delta_cpi_empirical_pp[, delta_cpi_koyck_pp]
    Cache: data/processed/simulation-params/io_price_model_output.csv
    """
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = SIM_DIR / "io_price_model_output.csv"

    if cache_path.exists() and not force:
        df = pd.read_csv(cache_path)
        # Recompute Koyck column if missing (backward compat)
        if koyck and "delta_cpi_koyck_pp" not in df.columns:
            print("Cache missing delta_cpi_koyck_pp — recomputing...")
        else:
            print(f"Loading cached: {cache_path}")
            return df

    if years is None:
        years = [2015, 2016, 2017, 2018, 2019, 2021, 2022, 2023, 2024]

    # Build raw per-year sector shocks (before Koyck)
    raw_shocks: dict[int, pd.Series] = {}
    for yr in years:
        raw_shocks[yr] = build_import_price_shock_vector(yr, base_year)

    # Apply Koyck adjustment if requested
    koyck_shocks = apply_koyck_lag(raw_shocks, delta=delta) if koyck else raw_shocks

    all_rows = []
    for yr in years:
        print(f"Running IO price model: year={yr}, base={base_year}")

        # Instantaneous specs (δ=1)
        sector_df = run_leontief_price_model(yr, base_year)
        cpi_df = map_to_cpi_categories(sector_df, yr)
        cpi_df["year"] = yr

        # Koyck-adjusted spec: re-run Leontief with adjusted shock
        if koyck:
            from src.utils.io_utils import compute_input_coefficients, compute_leontief_inverse
            io_data = load_io_table()
            A = compute_input_coefficients(io_data)
            L = compute_leontief_inverse(A)
            m_k = koyck_shocks[yr].reindex(A.index, fill_value=0.0)
            p_koyck = pd.Series(
                L.values.T @ m_k.values,
                index=io_data["sector_codes"],
            ) * BETA_EMPIRICAL  # apply empirical scaling

            # Bridge Koyck sector prices to CPI categories
            bridge = pd.read_csv(
                DATA_PROCESSED / "bridge-matrix" / "bridge_matrix_mid.csv",
                index_col=0,
            )
            p_koyck_pp = p_koyck * 100
            koyck_vals: list[float] = []
            for cat_name in cpi_df["cpi_mid_name"]:
                cat_info = CPI_MID_CATEGORY_MAP.get(cat_name, {})
                is_comp = cat_info.get("is_competitive_import", False)
                if cat_name in bridge.index and not is_comp:
                    w = bridge.loc[cat_name]
                    common = w.index.intersection(p_koyck_pp.index)
                    w_sum = w[common].sum()
                    val = (w[common] * p_koyck_pp[common]).sum() / w_sum if w_sum > 0 else 0.0
                else:
                    val = 0.0
                koyck_vals.append(val)
            cpi_df["delta_cpi_koyck_pp"] = koyck_vals

        all_rows.append(cpi_df)

    result = pd.concat(all_rows, ignore_index=True)
    cols = ["year", "cpi_mid_name", "cpi_code", "group", "is_competitive_import",
            "delta_cpi_leontief_pp", "delta_cpi_empirical_pp"]
    if koyck:
        cols.append("delta_cpi_koyck_pp")
    result = result[cols]
    result.to_csv(cache_path, index=False)
    print(f"Saved: {cache_path} ({len(result)} rows)")
    return result


# --------------------------------------------------------------------------- #
# 5. Validation: compare with actual CPI                                       #
# --------------------------------------------------------------------------- #

def validate_against_actual_cpi(
    model_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compare model-predicted CPI category changes with actual CPI data.

    Uses panel_cost_push.csv (already built with actual ΔCPI and IC values).

    Returns
    -------
    pd.DataFrame with columns:
        year, cpi_mid_name, cpi_code,
        delta_cpi_actual_pp,
        delta_cpi_leontief_pp, delta_cpi_empirical_pp,
        err_leontief_pp, err_empirical_pp
    Cache: data/processed/simulation-params/io_price_model_validation.csv
    """
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = SIM_DIR / "io_price_model_validation.csv"

    panel = pd.read_csv(DATA_PROCESSED / "price-indices" / "panel_cost_push.csv")
    panel = panel[["year", "cpi_mid_name", "cpi_code", "delta_cpi"]].copy()
    panel = panel.rename(columns={"delta_cpi": "delta_cpi_actual_pp"})
    # Normalize cpi_code to 4-digit string for consistent merge
    panel["cpi_code"] = panel["cpi_code"].astype(str).str.zfill(4)

    model_df = model_df.copy()
    model_df["cpi_code"] = model_df["cpi_code"].astype(str).str.zfill(4)

    merged = model_df.merge(
        panel, on=["year", "cpi_mid_name", "cpi_code"], how="left"
    )
    merged["err_leontief_pp"] = merged["delta_cpi_leontief_pp"] - merged["delta_cpi_actual_pp"]
    merged["err_empirical_pp"] = merged["delta_cpi_empirical_pp"] - merged["delta_cpi_actual_pp"]

    merged.to_csv(cache_path, index=False)
    print(f"Saved: {cache_path} ({len(merged)} rows)")
    return merged


def print_validation_summary(val_df: pd.DataFrame) -> None:
    """Print model vs actual CPI comparison summary."""
    shock_years = [2021, 2022, 2023, 2024]
    placebo_years = [2015, 2016, 2017, 2018, 2019]

    print("\n=== IO価格モデル検証: モデル予測 vs 実績CPI ===")
    print(f"\n{'年':>6}  {'実績ΔCPI(pp)':>14}  {'Leontief予測':>14}  {'実証スケール予測':>16}  {'誤差(Leontief)':>14}  {'誤差(実証)':>12}")
    print("-" * 90)

    for period_label, years in [("ショック期", shock_years), ("プラセボ期", placebo_years)]:
        print(f"\n[{period_label}]")
        sub = val_df[val_df["year"].isin(years)].copy()
        sub_excl = sub[~sub["is_competitive_import"]]

        # Year-level average (excluding competitive imports)
        for yr in years:
            yr_df = sub_excl[sub_excl["year"] == yr]
            if yr_df.empty:
                continue
            avg_actual = yr_df["delta_cpi_actual_pp"].mean()
            avg_leontief = yr_df["delta_cpi_leontief_pp"].mean()
            avg_empirical = yr_df["delta_cpi_empirical_pp"].mean()
            err_l = avg_leontief - avg_actual
            err_e = avg_empirical - avg_actual
            print(
                f"  {yr}  {avg_actual:>14.2f}  {avg_leontief:>14.2f}  {avg_empirical:>16.2f}  "
                f"{err_l:>+14.2f}  {err_e:>+12.2f}"
            )

    # Overall RMSE
    sub_shock = val_df[val_df["year"].isin(shock_years) & ~val_df["is_competitive_import"]].copy()
    sub_shock = sub_shock.dropna(subset=["delta_cpi_actual_pp"])
    rmse_l = np.sqrt((sub_shock["err_leontief_pp"] ** 2).mean())
    rmse_e = np.sqrt((sub_shock["err_empirical_pp"] ** 2).mean())
    print(f"\n  ショック期 RMSE — Leontief: {rmse_l:.3f}pp / 実証スケール: {rmse_e:.3f}pp")
    print(f"  → {f'実証スケール (β={BETA_EMPIRICAL:.3f})' if rmse_e < rmse_l else 'Leontief (β=1.0)'} のほうが実績CPI に近い")


# --------------------------------------------------------------------------- #
# 6. Visualization                                                             #
# --------------------------------------------------------------------------- #

def plot_model_vs_actual(
    val_df: pd.DataFrame,
    output_path: Path | None = None,
) -> None:
    """
    2-panel figure:
      Left : Year-level average — Leontief vs actual CPI (bar+line)
      Right: Category scatter — model predicted vs actual ΔCPI (shock years)
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import japanize_matplotlib

    if output_path is None:
        output_path = SIM_DIR / "fig_io_price_model_validation.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    shock_years = [2021, 2022, 2023, 2024]
    placebo_years = [2015, 2016, 2017, 2018, 2019]
    all_years = placebo_years + shock_years

    # Year averages (excl. competitive imports)
    sub = val_df[~val_df["is_competitive_import"]].copy()
    yearly = (
        sub.groupby("year")[["delta_cpi_actual_pp", "delta_cpi_leontief_pp", "delta_cpi_empirical_pp"]]
        .mean()
        .reset_index()
    )
    yearly = yearly[yearly["year"].isin(all_years)].sort_values("year")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "IO価格モデル検証: モデル予測 vs 実績CPI\n"
        f"β=1.0（レオンチェフ原形）vs β={BETA_EMPIRICAL:.3f}（実証スケーリング、Phase 2a-3）",
        fontsize=12, fontweight="bold",
    )

    # ---- Left panel: year-level average ----
    ax = axes[0]
    x = range(len(yearly))
    colors = ["#c0392b" if y in shock_years else "#2980b9" for y in yearly["year"]]

    ax.bar(x, yearly["delta_cpi_actual_pp"], color=colors, alpha=0.4, label="実績CPI（平均）")
    ax.plot(x, yearly["delta_cpi_leontief_pp"], "s--", color="#27ae60",
            linewidth=1.8, markersize=7, label="Leontief β=1.0")
    ax.plot(x, yearly["delta_cpi_empirical_pp"], "o-", color="#e67e22",
            linewidth=1.8, markersize=7, label=f"実証スケール β={BETA_EMPIRICAL:.3f}")

    ax.set_xticks(list(x))
    ax.set_xticklabels(yearly["year"].tolist(), rotation=45, fontsize=9)
    ax.set_ylabel("ΔCPI（pp、2020基準）", fontsize=10)
    ax.set_title("年次平均（競争的輸入財除外）", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)

    # ---- Right panel: category scatter (shock years, excl. competitive imports) ----
    ax = axes[1]
    shock_df = sub[sub["year"].isin(shock_years)].dropna(subset=["delta_cpi_actual_pp"])
    year_colors = {2021: "#f39c12", 2022: "#c0392b", 2023: "#8e44ad", 2024: "#2980b9"}
    for yr, grp in shock_df.groupby("year"):
        ax.scatter(
            grp["delta_cpi_actual_pp"], grp["delta_cpi_empirical_pp"],
            color=year_colors.get(yr, "gray"), alpha=0.7, s=40, label=str(yr),
        )
    # 45-degree line
    lims = [shock_df["delta_cpi_actual_pp"].min() - 1, shock_df["delta_cpi_actual_pp"].max() + 1]
    ax.plot(lims, lims, "k--", linewidth=1, alpha=0.5, label="45度線（完全一致）")
    ax.set_xlabel("実績ΔCPI（pp）", fontsize=10)
    ax.set_ylabel(f"モデル予測ΔCPI（pp, β={BETA_EMPIRICAL:.3f}）", fontsize=10)
    ax.set_title("費目別: モデル vs 実績（ショック期 2021-2024）", fontsize=11)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


# --------------------------------------------------------------------------- #
# 7. Entry point                                                               #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    print("=== Phase 3 Step 3-1: IO価格モデル ===\n")

    # Run model for all years
    model_df = run_io_price_model_all_years(force=False)

    print(f"\nModel output: {len(model_df)} rows, {model_df['year'].nunique()} years")
    print("\n--- ショック期 費目別予測（上位/下位 5件、2022年） ---")
    y2022 = model_df[model_df["year"] == 2022].sort_values("delta_cpi_empirical_pp", ascending=False)
    print(y2022[["cpi_mid_name", "group", "delta_cpi_leontief_pp", "delta_cpi_empirical_pp"]].to_string(index=False))

    # Validate against actual CPI
    val_df = validate_against_actual_cpi(model_df)
    print_validation_summary(val_df)

    # Plot
    plot_model_vs_actual(val_df)
