"""Russia→Ukraine geopolitical-news innovations and Japanese cost-of-living LPs.

This module deliberately separates two gates:

1. data feasibility: the public directed bilateral AI-GPR series is long enough
   to estimate the same monthly LP used for the Känzig oil-news shock;
2. causal identification: the bilateral news index is a measured news-intensity
   series, not a published high-frequency identified structural shock.

Consequently, the war-news LP is an exploratory comparison.  It must not be
described as the total causal effect of the 2022 invasion.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.oil_lp import (
    LABELS,
    OUTCOMES_PRECOVID,
    build_level,
    peak_row,
    run_lp,
)

ROOT = Path(__file__).resolve().parents[2]
GPR_CSV = ROOT / "data" / "raw" / "war-news" / "ai_gpr_bilateral_monthly.csv"
PANEL_CSV = ROOT / "data" / "processed" / "oil-lp" / "monthly_panel.csv"
OIL_SHOCK_CSV = (
    ROOT / "data" / "raw" / "oil-shocks" / "oil_supply_news_monthly.csv"
)
OIL_IRF_CSV = ROOT / "data" / "processed" / "oil-lp" / "irf_results.csv"
OUT_DIR = ROOT / "data" / "processed" / "war-news-lp"

WAR_COLUMN = "Russia|Ukraine"
WAR_SHOCK_NAME = "russia_ukraine_news_innovation"
H_MAX = 24
N_LAGS = 12
SEED = 31

OUTCOMES = [
    "cpi_headline",
    "cpi_food",
    "cpi_energy_utilities",
    "eff_cpi_q1",
    "eff_cpi_q5",
    "gap_q1_q5",
]


def recursive_ar_innovation(
    level: pd.Series,
    *,
    lags: int = N_LAGS,
    min_train: int = 60,
) -> pd.Series:
    """Return one-sided expanding-window AR forecast errors of ``log1p(level)``.

    Each innovation at month t is computed using coefficients fitted only with
    observations dated t-1 or earlier.  This prevents the 2022 invasion spike
    from changing innovations assigned to earlier months.
    """
    if lags < 1:
        raise ValueError("lags must be positive")
    if min_train <= lags:
        raise ValueError("min_train must exceed lags")

    series = pd.Series(level, copy=True).astype(float).sort_index()
    if not isinstance(series.index, pd.DatetimeIndex):
        raise TypeError("level must use a DatetimeIndex")
    if series.index.has_duplicates:
        raise ValueError("level index must be unique")
    expected = pd.date_range(series.index.min(), series.index.max(), freq="MS")
    if not series.index.equals(expected):
        raise ValueError("level must be a complete monthly-start series")
    if series.isna().any() or (series < 0).any():
        raise ValueError("level must be non-negative and complete")

    y = np.log1p(series.to_numpy())
    innovations = np.full(len(y), np.nan)
    first_forecast = lags + min_train

    for t in range(first_forecast, len(y)):
        train_t = np.arange(lags, t)
        x_train = np.column_stack(
            [
                np.ones(len(train_t)),
                *[y[train_t - lag] for lag in range(1, lags + 1)],
            ]
        )
        coefficients, *_ = np.linalg.lstsq(x_train, y[train_t], rcond=None)
        x_t = np.array([1.0, *[y[t - lag] for lag in range(1, lags + 1)]])
        innovations[t] = y[t] - float(x_t @ coefficients)

    return pd.Series(
        innovations,
        index=series.index,
        name=WAR_SHOCK_NAME,
    )


def prepare_war_news_shock(
    bilateral: pd.DataFrame,
    *,
    lags: int = N_LAGS,
    min_train: int = 60,
) -> pd.Series:
    """Construct the directed Russia→Ukraine news innovation.

    The reverse Ukraine→Russia index is intentionally excluded.  The source
    paper defines the columns as initiator→respondent and identifies the
    Russia→Ukraine direction as the one corresponding to the 2022 invasion.
    """
    required = {"Date", WAR_COLUMN}
    missing = required.difference(bilateral.columns)
    if missing:
        raise ValueError(f"missing AI-GPR columns: {sorted(missing)}")

    frame = bilateral.loc[:, ["Date", WAR_COLUMN]].copy()
    frame["Date"] = pd.to_datetime(frame["Date"])
    frame = frame.sort_values("Date").set_index("Date")
    return recursive_ar_innovation(
        frame[WAR_COLUMN],
        lags=lags,
        min_train=min_train,
    )


def feasibility_gate(
    shock: pd.Series,
    *,
    identified_externally: bool,
    min_observations: int = 120,
) -> dict[str, object]:
    """Separate mechanical estimability from structural identification."""
    usable = pd.Series(shock).dropna()
    data_pass = len(usable) >= min_observations
    causal_pass = data_pass and identified_externally
    if not data_pass:
        tier = "descriptive_only"
    elif causal_pass:
        tier = "causal_candidate"
    else:
        tier = "exploratory"
    return {
        "data_gate": "PASS" if data_pass else "FAIL",
        "causal_gate": "PASS" if causal_pass else "FAIL",
        "analysis_tier": tier,
        "n_observations": int(len(usable)),
        "start": usable.index.min() if len(usable) else pd.NaT,
        "end": usable.index.max() if len(usable) else pd.NaT,
        "autocorrelation_1": float(usable.autocorr()) if len(usable) > 1 else np.nan,
    }


def shock_concentration(shock: pd.Series) -> dict[str, float | int]:
    """Measure how many months effectively identify the news response."""
    usable = pd.Series(shock).dropna().astype(float)
    squared = usable.pow(2)
    total = float(squared.sum())
    if total <= 0:
        return {
            "n_months": int(len(usable)),
            "top1_squared_share": np.nan,
            "top5_squared_share": np.nan,
            "effective_event_count": 0.0,
        }
    weights = squared / total
    return {
        "n_months": int(len(usable)),
        "top1_squared_share": float(weights.nlargest(1).sum()),
        "top5_squared_share": float(weights.nlargest(5).sum()),
        "effective_event_count": float(1.0 / weights.pow(2).sum()),
    }


def run_joint_lp(
    level: pd.Series,
    shocks: dict[str, pd.Series],
    *,
    start: str,
    end: str,
    h_max: int = H_MAX,
    n_lags: int = N_LAGS,
    standardize: bool = True,
) -> pd.DataFrame:
    """Joint cumulative LP with HAC inference for sensitivity analysis.

    This function estimates partial coefficients conditional on the other news
    series.  It does not turn the war-news index into an identified shock and
    does not decompose a total war effect into oil and non-oil components.
    """
    import statsmodels.api as sm

    if len(shocks) < 2:
        raise ValueError("joint LP requires at least two shocks")
    if h_max < 0 or n_lags < 0:
        raise ValueError("h_max and n_lags must be non-negative")

    aligned: dict[str, pd.Series] = {}
    for name, shock in shocks.items():
        s = pd.Series(shock, copy=True).astype(float).reindex(level.index)
        if standardize:
            sd = float(s.loc[start:end].std(ddof=1))
            if not np.isfinite(sd) or sd <= 0:
                raise ValueError(f"shock {name} has no usable variance")
            s = s / sd
        aligned[name] = s

    dly = level.diff()
    rows: list[dict[str, float | int]] = []
    for h in range(h_max + 1):
        frame = pd.DataFrame(index=level.index)
        frame["dep"] = level.shift(-h) - level.shift(1)
        regressors: list[str] = []
        for name, shock in aligned.items():
            frame[f"{name}_0"] = shock
            regressors.append(f"{name}_0")
            for lag in range(1, n_lags + 1):
                column = f"{name}_l{lag}"
                frame[column] = shock.shift(lag)
                regressors.append(column)
        for lag in range(1, n_lags + 1):
            column = f"dly_l{lag}"
            frame[column] = dly.shift(lag)
            regressors.append(column)

        frame = frame.loc[start:end].dropna()
        fit = sm.OLS(
            frame["dep"],
            sm.add_constant(frame[regressors]),
        ).fit(cov_type="HAC", cov_kwds={"maxlags": h + 1})
        row: dict[str, float | int] = {"h": h, "n_obs": int(fit.nobs)}
        for name in aligned:
            row[f"beta_{name}"] = float(fit.params[f"{name}_0"])
            row[f"se_{name}"] = float(fit.bse[f"{name}_0"])
            row[f"p_{name}"] = float(fit.pvalues[f"{name}_0"])
        rows.append(row)
    return pd.DataFrame(rows)


def _format_peak(sub: pd.DataFrame) -> str:
    row = peak_row(sub)
    return (
        f"h={int(row['h'])}, beta={row['beta']:+.3f}, "
        f"p_HAC={row['p_hac']:.3f}, p_FWER={row['p_perm_fwer']:.3f}, "
        f"global_p={row['global_p_perm']:.3f}"
    )


def build_summary(
    war_irf: pd.DataFrame,
    joint_irf: pd.DataFrame,
    oil_irf: pd.DataFrame,
    gate: dict[str, object],
    correlation: float,
    concentration: dict[str, float | int],
) -> str:
    lines = [
        "Russia→Ukraine AI-GPR news innovation × fixed-basket LP",
        "=" * 68,
        (
            f"Data gate: {gate['data_gate']} (n={gate['n_observations']}, "
            f"{gate['start']}..{gate['end']}, ac1={gate['autocorrelation_1']:.3f})"
        ),
        (
            f"Causal gate: {gate['causal_gate']} — tier={gate['analysis_tier']}. "
            "The bilateral AI-GPR index is externally measured but is not a "
            "published high-frequency identified structural shock."
        ),
        f"Correlation with Känzig oil-news shock: {correlation:+.3f}",
        (
            "Shock concentration: "
            f"effective events={concentration['effective_event_count']:.1f}, "
            f"top1 squared share={concentration['top1_squared_share']:.1%}, "
            f"top5={concentration['top5_squared_share']:.1%}"
        ),
        "",
        "[Separate LP peak responses, full sample]",
    ]
    for outcome in OUTCOMES:
        war = war_irf[
            (war_irf["sample"] == "full") & (war_irf["outcome"] == outcome)
        ]
        oil = oil_irf[
            (oil_irf["sample"] == "full") & (oil_irf["outcome"] == outcome)
        ]
        lines.append(f"{outcome}:")
        lines.append(f"  war-news exploratory: {_format_peak(war)}")
        lines.append(f"  oil-news identified:  {_format_peak(oil)}")

    war_pre = war_irf[
        (war_irf["sample"] == "precovid")
        & (war_irf["outcome"] == "gap_q1_q5")
    ]
    lines.extend(
        [
            "",
            "[Pre-COVID war-news gap robustness]",
            f"gap_q1_q5: {_format_peak(war_pre)}",
        ]
    )

    lines.extend(["", "[Joint LP sensitivity — HAC only]"])
    for outcome in OUTCOMES:
        sub = joint_irf[joint_irf["outcome"] == outcome]
        war_row = sub.loc[sub["beta_war"].abs().idxmax()]
        oil_row = sub.loc[sub["beta_oil"].abs().idxmax()]
        lines.append(
            f"{outcome}: war peak h={int(war_row['h'])} "
            f"{war_row['beta_war']:+.3f} (p={war_row['p_war']:.3f}); "
            f"oil peak h={int(oil_row['h'])} "
            f"{oil_row['beta_oil']:+.3f} (p={oil_row['p_oil']:.3f})"
        )

    lines.extend(
        [
            "",
            "[Claim ceiling]",
            "The war-news estimates are exploratory associations with one-sided "
            "news innovations. They do not identify the total causal effect of "
            "the 2022 invasion. The Känzig oil-news LP remains the causal leg.",
        ]
    )
    return "\n".join(lines) + "\n"


def make_gap_comparison_figure(
    war_irf: pd.DataFrame,
    oil_irf: pd.DataFrame,
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import japanize_matplotlib  # noqa: F401
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    panels = [
        (
            axes[0],
            oil_irf[
                (oil_irf["sample"] == "full")
                & (oil_irf["outcome"] == "gap_q1_q5")
            ],
            "原油供給ニュース（識別済み）",
        ),
        (
            axes[1],
            war_irf[
                (war_irf["sample"] == "full")
                & (war_irf["outcome"] == "gap_q1_q5")
            ],
            "露→宇ニュース革新（探索的）",
        ),
    ]
    for ax, sub, title in panels:
        sub = sub.sort_values("h")
        ax.fill_between(
            sub["h"],
            sub["uniform_lower"],
            sub["uniform_upper"],
            color="#1f5fbf",
            alpha=0.18,
        )
        ax.plot(sub["h"], sub["beta"], color="#1f5fbf", lw=2)
        ax.axhline(0, color="#777", lw=0.8, ls=":")
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("ホライズン（月）")
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    axes[0].set_ylabel("Q1−Q5累積格差反応（pp / +1SD）")
    fig.suptitle("固定バスケット生活費格差：ショック系列別比較", fontsize=12)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_gap_oil_war_comparison.png", dpi=150)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    bilateral = pd.read_csv(GPR_CSV)
    war_shock = prepare_war_news_shock(bilateral)
    panel = pd.read_csv(PANEL_CSV, parse_dates=["date"]).set_index("date")
    oil_shocks = pd.read_csv(
        OIL_SHOCK_CSV,
        parse_dates=["date"],
    ).set_index("date")
    oil = oil_shocks["oil_supply_news_shock"]

    aligned_war = war_shock.reindex(panel.index)
    gate = feasibility_gate(
        aligned_war,
        identified_externally=False,
        min_observations=120,
    )
    if gate["data_gate"] != "PASS":
        raise RuntimeError(f"war-news LP data gate failed: {gate}")

    correlation = float(
        pd.concat(
            [aligned_war.rename("war"), oil.rename("oil")],
            axis=1,
            sort=False,
        )
        .dropna()
        .corr()
        .loc["war", "oil"]
    )

    rng = np.random.default_rng(SEED)
    war_parts: list[pd.DataFrame] = []
    joint_parts: list[pd.DataFrame] = []
    for outcome in OUTCOMES:
        level = build_level(panel, outcome)
        for sample, (start, end) in {
            "full": ("2005-01-01", "2025-12-01"),
            "precovid": ("2005-01-01", "2019-12-01"),
        }.items():
            result = run_lp(level, war_shock, start, end, rng)
            result.insert(0, "sample", sample)
            result.insert(0, "outcome", outcome)
            war_parts.append(result)

        joint = run_joint_lp(
            level,
            {"oil": oil, "war": war_shock},
            start="2005-01-01",
            end="2025-12-01",
        )
        joint.insert(0, "outcome", outcome)
        joint_parts.append(joint)

    war_irf = pd.concat(war_parts, ignore_index=True)
    joint_irf = pd.concat(joint_parts, ignore_index=True)
    oil_irf = pd.read_csv(OIL_IRF_CSV)
    concentration = shock_concentration(aligned_war)

    war_irf.to_csv(OUT_DIR / "war_irf_results.csv", index=False)
    joint_irf.to_csv(OUT_DIR / "joint_irf_sensitivity.csv", index=False)
    summary = build_summary(
        war_irf,
        joint_irf,
        oil_irf,
        gate,
        correlation,
        concentration,
    )
    (OUT_DIR / "comparison_summary.txt").write_text(summary, encoding="utf-8")
    make_gap_comparison_figure(war_irf, oil_irf)
    print(summary)


if __name__ == "__main__":
    main()
