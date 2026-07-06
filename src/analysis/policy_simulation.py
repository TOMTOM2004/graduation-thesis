"""
Phase 3 Step 3-4: Policy scenario simulation.

Applies policy subsidies to the IO price model's Koyck-adjusted CPI predictions,
then runs quintile microsimulation to evaluate distributional effects.

Three scenarios (derived from Phase 2b Q1 burden decomposition):
  baseline      : no policy intervention
  energy_subsidy: 50% subsidy on electricity and gas price rises (光熱・水道)
  food_support  : 30% subsidy on food price rises (食料全品目)
  combined      : energy_subsidy + food_support simultaneously

Assumption: Comparative statics (ceteris paribus). No general equilibrium effects.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.quintile_impact import run_microsimulation, QUINTILE_LABELS
from src.analysis.io_price_model import DELTA_KOYCK, BETA_EMPIRICAL

DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
SIM_DIR = DATA_PROCESSED / "simulation-params"

# --------------------------------------------------------------------------- #
# Policy scenario definitions                                                  #
# --------------------------------------------------------------------------- #

# CPI mid-category codes targeted by each scenario
_ENERGY_CODES = {"0056", "0057", "0058", "0059"}   # 電気代・ガス代・他の光熱・上下水道料
_FOOD_CODES = {
    "0003", "0008", "0013", "0016", "0021", "0027",
    "0030", "0033", "0034", "0037", "0041", "0042",
}

# Subsidy rates: fraction of the price rise that is offset by policy
# energy_subsidy 50%: calibrated to the 2022 電力・ガス激変緩和措置 scale
#   (actual: ~15-20%, 50% represents a 2.5-3x larger intervention for sensitivity)
# food_support 30%: equivalent to applying reduced consumption tax rate
POLICY_SCENARIOS: dict[str, dict] = {
    "baseline": {
        "target_codes": set(),
        "subsidy_rate": 0.0,
        "label": "ベースライン（政策なし）",
    },
    "energy_subsidy": {
        "target_codes": _ENERGY_CODES,
        "subsidy_rate": 0.5,
        "label": "エネルギー補助（光熱50%補填）",
    },
    "food_support": {
        "target_codes": _FOOD_CODES,
        "subsidy_rate": 0.3,
        "label": "食料価格支援（食料30%補填）",
    },
    "combined": {
        "target_codes": _ENERGY_CODES | _FOOD_CODES,
        "subsidy_rate": {"energy": 0.5, "food": 0.3},
        "label": "複合介入（エネルギー50% + 食料30%）",
    },
}

# Default analysis years (shock period, benchmark year = 2022)
DEFAULT_YEARS = [2021, 2022, 2023, 2024]
BENCHMARK_YEAR = 2022   # cost-push dominant year


# --------------------------------------------------------------------------- #
# Core functions                                                               #
# --------------------------------------------------------------------------- #

def apply_policy_shock(
    model_output: pd.DataFrame,
    scenario_name: str,
    year: int,
) -> pd.DataFrame:
    """
    Apply a policy subsidy to the IO model's predicted CPI changes for a given year.

    Modifies delta_cpi_koyck_pp for targeted categories:
        adjusted_delta = delta_cpi_koyck_pp × (1 - subsidy_rate)

    For the 'combined' scenario, energy and food categories use their respective rates.

    Parameters
    ----------
    model_output : pd.DataFrame
        IO price model output with delta_cpi_koyck_pp column.
        columns: [year, cpi_mid_name, cpi_code, delta_cpi_koyck_pp, ...]
    scenario_name : str
        Key into POLICY_SCENARIOS.
    year : int
        Target year to apply policy to.

    Returns
    -------
    pd.DataFrame with column delta_cpi_pp = Koyck-adjusted + policy-modified price change.
    """
    scenario = POLICY_SCENARIOS[scenario_name]
    yr_df = model_output[model_output["year"] == year].copy()

    # Ensure cpi_code is 4-digit string
    yr_df["cpi_code"] = yr_df["cpi_code"].astype(str).str.zfill(4)
    yr_df["delta_cpi_pp"] = yr_df["delta_cpi_koyck_pp"].copy()

    if scenario["subsidy_rate"] == 0.0:
        # baseline: no change
        return yr_df[["year", "cpi_mid_name", "cpi_code", "delta_cpi_pp"]]

    target_codes = scenario["target_codes"]

    if scenario_name == "combined":
        # Different rates for energy vs food
        energy_rate = scenario["subsidy_rate"]["energy"]
        food_rate = scenario["subsidy_rate"]["food"]
        for idx, row in yr_df.iterrows():
            code = row["cpi_code"]
            if code in _ENERGY_CODES:
                yr_df.at[idx, "delta_cpi_pp"] = row["delta_cpi_koyck_pp"] * (1 - energy_rate)
            elif code in _FOOD_CODES:
                yr_df.at[idx, "delta_cpi_pp"] = row["delta_cpi_koyck_pp"] * (1 - food_rate)
    else:
        rate = scenario["subsidy_rate"]
        mask = yr_df["cpi_code"].isin(target_codes)
        yr_df.loc[mask, "delta_cpi_pp"] = yr_df.loc[mask, "delta_cpi_koyck_pp"] * (1 - rate)

    return yr_df[["year", "cpi_mid_name", "cpi_code", "delta_cpi_pp"]]


def run_all_scenarios(
    years: list[int] | None = None,
    delta_col: str = "delta_cpi_koyck_pp",
    force: bool = False,
) -> pd.DataFrame:
    """
    Run all 4 policy scenarios × all years through the microsimulation.

    Parameters
    ----------
    years : list of years to simulate. Default: DEFAULT_YEARS = [2021-2024].
    delta_col : column in IO model output to use as baseline CPI change.
    force : recompute even if cache exists.

    Returns
    -------
    pd.DataFrame with columns:
        year, quintile, quintile_label, scenario,
        effective_inflation_pp, q1_q5_gap_pp, gdp_avg_pp,
        gap_vs_baseline_pp   (effective_inflation relative to baseline scenario)
    Cache: data/processed/simulation-params/policy_scenario_results.csv
    """
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = SIM_DIR / "policy_scenario_results.csv"

    if cache_path.exists() and not force:
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    if years is None:
        years = DEFAULT_YEARS

    # Load IO model output (must contain delta_cpi_koyck_pp)
    model_df = pd.read_csv(SIM_DIR / "io_price_model_output.csv")
    if delta_col not in model_df.columns:
        raise ValueError(
            f"Column '{delta_col}' not found in io_price_model_output.csv. "
            "Rerun run_io_price_model_all_years(koyck=True, force=True) first."
        )

    all_scenario_dfs = []
    for scenario_name in POLICY_SCENARIOS:
        print(f"Running scenario: {scenario_name}")
        # Build adjusted cpi_changes DataFrame for all years
        adjusted_frames = []
        for yr in years:
            yr_adjusted = apply_policy_shock(model_df, scenario_name, yr)
            adjusted_frames.append(yr_adjusted)
        cpi_input = pd.concat(adjusted_frames, ignore_index=True)

        # Remove per-scenario cache to force recompute each call
        per_cache = SIM_DIR / f"microsim_{scenario_name}.csv"
        per_cache.unlink(missing_ok=True)

        sim_df = run_microsimulation(cpi_input, scenario_label=scenario_name)
        all_scenario_dfs.append(sim_df)

    combined = pd.concat(all_scenario_dfs, ignore_index=True)

    # Compute gap vs baseline
    baseline_df = combined[combined["scenario"] == "baseline"][
        ["year", "quintile", "effective_inflation_pp"]
    ].rename(columns={"effective_inflation_pp": "baseline_pp"})

    combined = combined.merge(baseline_df, on=["year", "quintile"], how="left")
    combined["gap_vs_baseline_pp"] = combined["effective_inflation_pp"] - combined["baseline_pp"]
    combined = combined.drop(columns=["baseline_pp"])

    combined.to_csv(cache_path, index=False)
    print(f"Saved: {cache_path} ({len(combined)} rows)")
    return combined


def make_policy_comparison_table(
    results: pd.DataFrame,
    year: int = BENCHMARK_YEAR,
) -> pd.DataFrame:
    """
    Build comparison table for a given year across all scenarios.

    Rows: scenarios. Columns: GDP avg, Q1, Q5, Q1-Q5 gap, gap reduction rate.

    Returns
    -------
    pd.DataFrame (also saves CSV + LaTeX)
    Cache: data/processed/simulation-params/policy_comparison_{year}.csv
    """
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = SIM_DIR / f"policy_comparison_{year}.csv"

    yr_df = results[results["year"] == year].copy()
    rows = []
    for scenario_name, scenario_info in POLICY_SCENARIOS.items():
        s_df = yr_df[yr_df["scenario"] == scenario_name]
        q1 = s_df[s_df["quintile"] == 1]["effective_inflation_pp"].values
        q5 = s_df[s_df["quintile"] == 5]["effective_inflation_pp"].values
        avg = s_df[s_df["quintile"] == 0]["effective_inflation_pp"].values
        gap = s_df[s_df["quintile"] == 1]["q1_q5_gap_pp"].values

        rows.append({
            "scenario": scenario_name,
            "label": scenario_info["label"],
            "gdp_avg_pp": round(avg[0], 3) if len(avg) else np.nan,
            "q1_pp": round(q1[0], 3) if len(q1) else np.nan,
            "q5_pp": round(q5[0], 3) if len(q5) else np.nan,
            "q1_q5_gap_pp": round(gap[0], 3) if len(gap) else np.nan,
        })

    table = pd.DataFrame(rows)

    # Compute gap reduction relative to baseline
    baseline_gap = table.loc[table["scenario"] == "baseline", "q1_q5_gap_pp"].values[0]
    table["gap_reduction_pp"] = baseline_gap - table["q1_q5_gap_pp"]
    table["gap_reduction_pct"] = (
        table["gap_reduction_pp"] / abs(baseline_gap) * 100
    ).round(1)

    table.to_csv(cache_path, index=False)

    # LaTeX tabular
    latex_path = SIM_DIR / f"policy_comparison_{year}.tex"
    _write_latex_table(table, latex_path, year)

    print(f"Saved: {cache_path}, {latex_path}")
    return table


def _write_latex_table(table: pd.DataFrame, path: Path, year: int) -> None:
    """Write LaTeX tabular for policy comparison table."""
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        rf"\caption{{政策シナリオ比較（{year}年、コストプッシュ主導期）}}",
        r"\label{tab:policy_comparison}",
        r"\begin{tabular}{lcccccc}",
        r"\toprule",
        r"シナリオ & GDP平均(pp) & Q1(pp) & Q5(pp) & Q1-Q5格差(pp) & 格差削減(pp) & 削減率(\%) \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(
            f"{row['label']} & {row['gdp_avg_pp']:.3f} & {row['q1_pp']:.3f} & "
            f"{row['q5_pp']:.3f} & {row['q1_q5_gap_pp']:.3f} & "
            f"{row['gap_reduction_pp']:.3f} & {row['gap_reduction_pct']:.1f}\\% \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabular}",
        r"\end{table}",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def plot_policy_scenarios(
    results: pd.DataFrame,
    output_path: Path | None = None,
) -> None:
    """
    2-panel figure:
      Left : Q1-Q5 gap by year across all scenarios (line chart)
      Right: Quintile effective inflation in BENCHMARK_YEAR (bar chart × 4 scenarios)

    Output: data/processed/simulation-params/fig_policy_scenarios.png
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import japanize_matplotlib

    if output_path is None:
        output_path = SIM_DIR / "fig_policy_scenarios.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    scenario_colors = {
        "baseline": "#7f8c8d",
        "energy_subsidy": "#e67e22",
        "food_support": "#27ae60",
        "combined": "#c0392b",
    }
    scenario_labels = {k: v["label"] for k, v in POLICY_SCENARIOS.items()}

    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(
        "政策シナリオ評価: エネルギー補助・食料価格支援の所得階層別分配効果\n"
        f"IOモデル（Koyckラグ δ={DELTA_KOYCK}）+ 五分位マイクロシミュレーション",
        fontsize=12, fontweight="bold",
    )

    # --- Left: Q1-Q5 gap by year ---
    ax = axes[0]
    years = sorted(results["year"].unique())

    for scenario_name in POLICY_SCENARIOS:
        s_df = results[results["scenario"] == scenario_name]
        gaps = []
        for yr in years:
            yr_row = s_df[s_df["year"] == yr]
            q1_gap = yr_row[yr_row["quintile"] == 1]["q1_q5_gap_pp"].values
            gaps.append(q1_gap[0] if len(q1_gap) else np.nan)

        ls = "--" if scenario_name == "baseline" else "-"
        ax.plot(years, gaps,
                marker="o", linewidth=2, linestyle=ls,
                color=scenario_colors[scenario_name],
                label=scenario_labels[scenario_name])

    ax.axhline(0, color="gray", linewidth=0.8, alpha=0.5)
    ax.set_xlabel("年", fontsize=10)
    ax.set_ylabel("Q1-Q5 インフレ格差（pp）", fontsize=10)
    ax.set_title("Q1-Q5インフレ格差の年次推移（シナリオ別）", fontsize=11)
    ax.legend(fontsize=8, loc="upper left")
    ax.set_xticks(years)
    ax.grid(axis="y", alpha=0.25)

    # --- Right: quintile effective inflation in BENCHMARK_YEAR ---
    ax = axes[1]
    benchmark_df = results[results["year"] == BENCHMARK_YEAR]

    quintiles = [1, 2, 3, 4, 5]
    quintile_labels_short = ["Q1", "Q2", "Q3", "Q4", "Q5"]
    n_scenarios = len(POLICY_SCENARIOS)
    x = np.arange(len(quintiles))
    width = 0.8 / n_scenarios

    for i, (scenario_name, scenario_info) in enumerate(POLICY_SCENARIOS.items()):
        s_df = benchmark_df[benchmark_df["scenario"] == scenario_name]
        vals = []
        for q in quintiles:
            row = s_df[s_df["quintile"] == q]["effective_inflation_pp"].values
            vals.append(row[0] if len(row) else np.nan)

        offset = (i - n_scenarios / 2 + 0.5) * width
        bars = ax.bar(
            x + offset, vals, width * 0.9,
            color=scenario_colors[scenario_name],
            alpha=0.8,
            label=scenario_labels[scenario_name],
        )

    ax.set_xlabel("所得五分位", fontsize=10)
    ax.set_ylabel("有効インフレ負担（pp）", fontsize=10)
    ax.set_title(f"{BENCHMARK_YEAR}年: 五分位別有効インフレ（シナリオ比較）", fontsize=11)
    ax.set_xticks(x)
    ax.set_xticklabels(quintile_labels_short)
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(axis="y", alpha=0.25)

    fig.text(
        0.5, -0.04,
        f"注: {BENCHMARK_YEAR}年（コストプッシュ主導期）を基準年として比較。"
        "補助率: エネルギー50%・食料30%。ceteris paribus（一般均衡効果なし）の前提。"
        f"Koyck δ={DELTA_KOYCK}（輸入コスト上昇の年内転嫁率{DELTA_KOYCK:.0%}）。",
        ha="center", fontsize=8, color="gray",
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def sensitivity_analysis_delta(
    deltas: list[float] | None = None,
    year: int = BENCHMARK_YEAR,
) -> pd.DataFrame:
    """
    Assess robustness of policy effects across different Koyck δ values.

    Computes the IO-Koyck model inline for each δ without touching the main cache.

    Parameters
    ----------
    deltas : Koyck δ values to test. Default: [0.4, 0.55, 0.7, 1.0].
    year : benchmark year for comparison.

    Returns
    -------
    pd.DataFrame with columns: delta, scenario, year, gdp_avg_pp, q1_pp, q5_pp, q1_q5_gap_pp
    Cache: data/processed/simulation-params/sensitivity_delta.csv
    """
    SIM_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = SIM_DIR / "sensitivity_delta.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    if deltas is None:
        deltas = [0.4, 0.55, 0.7, 1.0]

    from src.analysis.io_price_model import (
        apply_koyck_lag,
        build_import_price_shock_vector,
        BETA_EMPIRICAL,
    )
    from src.analysis.bridge_matrix_mid import CPI_MID_CATEGORY_MAP
    from src.utils.io_utils import load_io_table, compute_input_coefficients, compute_leontief_inverse

    # Load IO table and bridge matrix once
    io_data = load_io_table()
    A = compute_input_coefficients(io_data)
    L = compute_leontief_inverse(A)
    bridge = pd.read_csv(
        DATA_PROCESSED / "bridge-matrix" / "bridge_matrix_mid.csv",
        index_col=0,
    )

    def _build_koyck_cpi(delta: float) -> pd.DataFrame:
        """Build Koyck-adjusted CPI mid-category predictions for the target year."""
        raw_shock = {year: build_import_price_shock_vector(year)}
        koyck_shock = apply_koyck_lag(raw_shock, delta=delta)
        m_k = koyck_shock[year].reindex(A.index, fill_value=0.0)
        p_koyck_pp = (
            pd.Series(L.values.T @ m_k.values, index=io_data["sector_codes"])
            * BETA_EMPIRICAL * 100
        )

        cat_names, cpi_codes, koyck_vals = [], [], []
        for cat_name, cat_info in CPI_MID_CATEGORY_MAP.items():
            cat_names.append(cat_name)
            cpi_codes.append(str(cat_info["cpi_code"]).zfill(4))
            is_comp = cat_info.get("is_competitive_import", False)
            if cat_name in bridge.index and not is_comp:
                w = bridge.loc[cat_name]
                common = w.index.intersection(p_koyck_pp.index)
                w_sum = w[common].sum()
                val = (w[common] * p_koyck_pp[common]).sum() / w_sum if w_sum > 0 else 0.0
            else:
                val = 0.0
            koyck_vals.append(val)

        return pd.DataFrame({
            "year": year,
            "cpi_mid_name": cat_names,
            "cpi_code": cpi_codes,
            "delta_cpi_koyck_pp": koyck_vals,
        })

    def _apply_policy(base_df: pd.DataFrame, scenario_name: str) -> pd.DataFrame:
        """Apply policy subsidy to a per-year CPI DataFrame."""
        yr_df = base_df.copy()
        yr_df["delta_cpi_pp"] = yr_df["delta_cpi_koyck_pp"].copy()
        scenario_info = POLICY_SCENARIOS[scenario_name]
        if scenario_info["subsidy_rate"] == 0.0:
            return yr_df[["year", "cpi_mid_name", "cpi_code", "delta_cpi_pp"]]
        if scenario_name == "combined":
            energy_mask = yr_df["cpi_code"].isin(_ENERGY_CODES)
            food_mask = yr_df["cpi_code"].isin(_FOOD_CODES)
            yr_df.loc[energy_mask, "delta_cpi_pp"] *= 1 - 0.5
            yr_df.loc[food_mask, "delta_cpi_pp"] *= 1 - 0.3
        else:
            rate = scenario_info["subsidy_rate"]
            mask = yr_df["cpi_code"].isin(scenario_info["target_codes"])
            yr_df.loc[mask, "delta_cpi_pp"] *= 1 - rate
        return yr_df[["year", "cpi_mid_name", "cpi_code", "delta_cpi_pp"]]

    rows = []
    for delta in deltas:
        print(f"\n=== Sensitivity: δ={delta} ===")
        base_df = _build_koyck_cpi(delta)

        for scenario_name in POLICY_SCENARIOS:
            cpi_input = _apply_policy(base_df, scenario_name)
            lbl = f"sens_d{str(delta).replace('.', '')}__{scenario_name}"
            (SIM_DIR / f"microsim_{lbl}.csv").unlink(missing_ok=True)

            sim_df = run_microsimulation(cpi_input, scenario_label=lbl)
            yr_sim = sim_df[sim_df["year"] == year]

            q1 = yr_sim[yr_sim["quintile"] == 1]["effective_inflation_pp"].values
            q5 = yr_sim[yr_sim["quintile"] == 5]["effective_inflation_pp"].values
            avg = yr_sim[yr_sim["quintile"] == 0]["effective_inflation_pp"].values
            gap = float(q1[0] - q5[0]) if len(q1) and len(q5) else np.nan

            rows.append({
                "delta": delta,
                "scenario": scenario_name,
                "year": year,
                "gdp_avg_pp": round(float(avg[0]), 4) if len(avg) else np.nan,
                "q1_pp": round(float(q1[0]), 4) if len(q1) else np.nan,
                "q5_pp": round(float(q5[0]), 4) if len(q5) else np.nan,
                "q1_q5_gap_pp": round(gap, 4) if pd.notna(gap) else np.nan,
            })

    result = pd.DataFrame(rows)
    result.to_csv(cache_path, index=False)
    print(f"\nSaved: {cache_path}")
    return result


def print_policy_summary(results: pd.DataFrame, year: int = BENCHMARK_YEAR) -> None:
    """Print policy comparison table for a given year."""
    print(f"\n=== 政策シナリオ評価（{year}年基準） ===")
    yr_df = results[results["year"] == year]

    print(f"\n{'シナリオ':>30}  {'GDP平均':>8}  {'Q1':>7}  {'Q5':>7}  {'Q1-Q5格差':>10}  {'格差削減':>8}")
    print("-" * 80)

    baseline_gap = None
    for scenario_name, scenario_info in POLICY_SCENARIOS.items():
        s_df = yr_df[yr_df["scenario"] == scenario_name]
        q1 = s_df[s_df["quintile"] == 1]["effective_inflation_pp"].values
        q5 = s_df[s_df["quintile"] == 5]["effective_inflation_pp"].values
        avg = s_df[s_df["quintile"] == 0]["effective_inflation_pp"].values
        gap_vals = s_df[s_df["quintile"] == 1]["q1_q5_gap_pp"].values

        q1_val = q1[0] if len(q1) else np.nan
        q5_val = q5[0] if len(q5) else np.nan
        avg_val = avg[0] if len(avg) else np.nan
        gap_val = gap_vals[0] if len(gap_vals) else np.nan

        if scenario_name == "baseline":
            baseline_gap = gap_val
            gap_reduction = "—"
        else:
            if baseline_gap and pd.notna(gap_val):
                gap_reduction = f"{baseline_gap - gap_val:+.3f}pp"
            else:
                gap_reduction = "N/A"

        print(
            f"  {scenario_info['label']:>30}  "
            f"{avg_val:>7.3f}pp  {q1_val:>6.3f}pp  {q5_val:>6.3f}pp  "
            f"{gap_val:>9.3f}pp  {gap_reduction:>8}"
        )


if __name__ == "__main__":
    print("=== Step 3-4: Policy Scenario Evaluation ===")

    results = run_all_scenarios()
    print_policy_summary(results, year=BENCHMARK_YEAR)

    table = make_policy_comparison_table(results, year=BENCHMARK_YEAR)
    print("\n--- Policy Comparison Table ---")
    print(table.to_string(index=False))

    plot_policy_scenarios(results)

    print("\n=== Sensitivity Analysis (δ variation) ===")
    sens = sensitivity_analysis_delta()
    print(sens.to_string(index=False))
