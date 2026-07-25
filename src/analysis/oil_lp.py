"""
Jordà local projections of the Känzig oil supply news shock on Japanese CPI
and quintile effective CPI, plus a partial historical decomposition.

Motivation (DEC-013/015): cross-sectional exposure designs could not cleanly
identify cost-push from a single macro event. This module tests whether an
EXTERNALLY identified time-series instrument (Känzig 2021 oil supply news
shock, OPEC-announcement high-frequency identification) succeeds where the
exposure designs failed.

Specification
-------------
Cumulative LP, for outcome y and horizon h = 0..24:

    100*(log y_{t+h} - log y_{t-1})
        = a_h + b_h * shock_t
          + sum_{j=1..12} g_j * shock_{t-j}
          + sum_{j=1..12} f_j * 100*dlog y_{t-j} + e_{t+h}

- shock standardized to unit variance (ddof=1) over the h=0 estimation
  sample of each (outcome, sample); b_h = pp response per +1 SD shock.
- Gap outcome (Q1-Q5): "log level" = 100 * cumsum(gap_q1_q5_mom_dlog),
  i.e. the cumulated Q1-Q5 effective-inflation differential in pp. b_h is
  then the pp change of that cumulated gap per +1 SD shock.
- Inference: (a) Newey-West HAC, maxlags = h+1 (overlapping horizons);
  (b) permutation: 1000 random permutations of the (standardized) shock
  series over an extended index (sample start - 12 months .. sample end);
  shock lags are rebuilt from each permuted series; two-sided
  p = (1 + #{|b_perm| >= |b_hat|}) / (1 + N). numpy default_rng(seed=21).
- Samples: full = 2005-01..2025-12 (primary, oil_supply_news_shock);
  precovid = 2005-01..2019-12 (robustness) uses the
  oil_supply_news_shock_precovid variant, because the full-sample VAR
  shock is estimated through 2025 and its post-2019 estimation could leak
  into pre-2020 fitted values.
- log_import_energy: BOJ series starts 2015-01 -> regression sample is
  short (t from ~2016-02, shrinking with h); flagged in output. Uses the
  same full-sample-standardized shock for comparability of units.

Historical decomposition (PARTIAL attribution)
----------------------------------------------
Non-cumulative IRF b*_j obtained by differencing the cumulative one
(b*_0 = b_0, b*_j = b_j - b_{j-1}); contribution to the monthly dlog:
contribution_t = sum_{j=0..24} b*_j * shock_{t-j} (pp). This attributes
ONLY the Känzig oil supply news channel — FX, food-commodity, and
war-related non-oil channels are NOT captured. It is a linear partial
attribution, not a full structural decomposition.

Outputs (data/processed/oil-lp/)
--------------------------------
- irf_results.csv           : outcome, sample, h, beta, se_hac, p_hac,
                              p_perm, n_obs
- historical_decomposition.csv : date, actual/attributed dlog (pp) for
                              headline and the Q1-Q5 gap
- lp_summary.txt            : peak IRFs, success criteria [A]-[D],
                              attribution shares
- fig_irf_main.png, fig_irf_quintiles.png, fig_hist_decomp.png

Run: uv run python src/analysis/oil_lp.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
PANEL_CSV = ROOT / "data" / "processed" / "oil-lp" / "monthly_panel.csv"
SHOCK_CSV = ROOT / "data" / "raw" / "oil-shocks" / "oil_supply_news_monthly.csv"
OUT_DIR = ROOT / "data" / "processed" / "oil-lp"

H_MAX = 24
N_LAGS = 12
N_PERM = 1000
SEED = 21
ALPHA = 0.10  # pre-specified significance level (90%)

SAMPLES = {
    "full": ("2005-01-01", "2025-12-01", "oil_supply_news_shock"),
    "precovid": ("2005-01-01", "2019-12-01", "oil_supply_news_shock_precovid"),
}

# outcome -> (panel column of the log-level object, label, is_gap)
OUTCOMES_FULL = [
    "cpi_headline",
    "cpi_food",
    "cpi_energy_utilities",
    "eff_cpi_q1",
    "eff_cpi_q2",
    "eff_cpi_q3",
    "eff_cpi_q4",
    "eff_cpi_q5",
    "gap_q1_q5",
    "log_import_energy",
]
OUTCOMES_PRECOVID = ["cpi_headline", "cpi_energy_utilities", "gap_q1_q5"]

LABELS = {
    "cpi_headline": "CPI総合",
    "cpi_food": "CPI食料",
    "cpi_energy_utilities": "CPI光熱・水道",
    "eff_cpi_q1": "実効CPI Q1",
    "eff_cpi_q2": "実効CPI Q2",
    "eff_cpi_q3": "実効CPI Q3",
    "eff_cpi_q4": "実効CPI Q4",
    "eff_cpi_q5": "実効CPI Q5",
    "gap_q1_q5": "Q1−Q5実効インフレ格差",
    "log_import_energy": "輸入エネルギー価格(日銀・2015+短サンプル)",
}


# ---------------------------------------------------------------- data loading

def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = pd.read_csv(PANEL_CSV, parse_dates=["date"]).set_index("date")
    shocks = pd.read_csv(SHOCK_CSV, parse_dates=["date"]).set_index("date")
    return panel, shocks


def build_level(panel: pd.DataFrame, outcome: str) -> pd.Series:
    """100*log level object per outcome (gap: 100*cumsum of the MoM dlog gap,
    units = cumulated pp differential)."""
    if outcome == "gap_q1_q5":
        g = panel["gap_q1_q5_mom_dlog"]
        # first month is NaN (diff); cumulate over non-NaN support
        lvl = (g.fillna(0.0).cumsum() * 100.0).where(g.notna().cummax())
        return lvl.rename(outcome)
    if outcome == "log_import_energy":
        return (panel["log_import_energy"] * 100.0).rename(outcome)
    return (np.log(panel[outcome].astype(float)) * 100.0).rename(outcome)


# ------------------------------------------------------------- LP estimation

def lp_frames(
    level: pd.Series, shock: pd.Series, start: str, end: str
) -> dict:
    """Precompute per-horizon regression pieces.

    Returns dict with, per h: dep vector, shock-block dates, fixed control
    matrix (const + 12 dly lags), valid t index. Shock lags come from the
    full shock history (pre-2005 values exist), standardized later.
    """
    dly = level.diff()
    idx = level.index
    pieces = {}
    for h in range(H_MAX + 1):
        df = pd.DataFrame(index=idx)
        df["dep"] = level.shift(-h) - level.shift(1)
        df["shock0"] = shock.reindex(idx)
        # shock lags directly from full history (robust at sample edges)
        for j in range(1, N_LAGS + 1):
            df[f"shock_l{j}"] = shock.shift(j).reindex(idx)
        for j in range(1, N_LAGS + 1):
            df[f"dly_l{j}"] = dly.shift(j)
        df = df.loc[start:end].dropna()
        pieces[h] = df
    return pieces


def standardize_shock(shock: pd.Series, h0_index: pd.DatetimeIndex) -> tuple[pd.Series, float]:
    sd = float(shock.reindex(h0_index).std(ddof=1))
    return shock / sd, sd


def run_lp(
    level: pd.Series,
    shock_raw: pd.Series,
    start: str,
    end: str,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Estimate the cumulative LP with HAC + permutation inference."""
    pieces0 = lp_frames(level, shock_raw, start, end)
    if len(pieces0[0]) == 0:
        raise RuntimeError("empty h=0 estimation sample")
    shock, sd = standardize_shock(shock_raw, pieces0[0].index)
    pieces = lp_frames(level, shock, start, end)

    shock_cols = ["shock0"] + [f"shock_l{j}" for j in range(1, N_LAGS + 1)]
    ctrl_cols = [f"dly_l{j}" for j in range(1, N_LAGS + 1)]

    # --- HAC point estimates
    rows = []
    for h in range(H_MAX + 1):
        df = pieces[h]
        X = sm.add_constant(df[shock_cols + ctrl_cols])
        res = sm.OLS(df["dep"], X).fit(
            cov_type="HAC", cov_kwds={"maxlags": h + 1}
        )
        rows.append(
            {
                "h": h,
                "beta": res.params["shock0"],
                "se_hac": res.bse["shock0"],
                "p_hac": res.pvalues["shock0"],
                "n_obs": int(res.nobs),
            }
        )
    out = pd.DataFrame(rows)

    # --- permutation inference: permute the standardized shock over an
    # extended index (min t - 12 months .. max t), rebuild lags, re-estimate.
    t_min = min(pieces[h].index.min() for h in pieces)
    t_max = max(pieces[h].index.max() for h in pieces)
    ext_idx = pd.date_range(
        t_min - pd.DateOffset(months=N_LAGS), t_max, freq="MS"
    )
    s_ext = shock.reindex(ext_idx).to_numpy()
    assert not np.isnan(s_ext).any(), "shock series has gaps on extended index"
    pos = {d: i for i, d in enumerate(ext_idx)}

    # fixed pieces per horizon
    fixed = {}
    for h in range(H_MAX + 1):
        df = pieces[h]
        C = np.column_stack(
            [np.ones(len(df)), df[ctrl_cols].to_numpy()]
        )
        d = df["dep"].to_numpy()
        p = np.array([pos[t] for t in df.index])
        fixed[h] = (d, C, p)

    m = len(s_ext)
    exceed = np.zeros(H_MAX + 1)
    beta_hat = out["beta"].to_numpy()
    for _ in range(N_PERM):
        sp = s_ext[rng.permutation(m)]
        # lag matrix over ext index: col j = sp shifted by j
        L = np.full((m, N_LAGS + 1), np.nan)
        for j in range(N_LAGS + 1):
            L[j:, j] = sp[: m - j] if j else sp
        for h in range(H_MAX + 1):
            d, C, p = fixed[h]
            X = np.hstack([L[p], C])
            coef, *_ = np.linalg.lstsq(X, d, rcond=None)
            if abs(coef[0]) >= abs(beta_hat[h]):
                exceed[h] += 1
    out["p_perm"] = (1.0 + exceed) / (1.0 + N_PERM)
    out.attrs["shock_sd"] = sd
    return out


# ---------------------------------------------------- historical decomposition

def historical_decomposition(
    irf: pd.DataFrame,
    level: pd.Series,
    shock_std: pd.Series,
) -> pd.Series:
    """contribution_t = sum_j b*_j * shock_{t-j}, b* = differenced cumulative
    IRF. Returns pp contribution to the monthly dlog on the panel index."""
    beta = irf.sort_values("h")["beta"].to_numpy()
    b_star = np.diff(beta, prepend=0.0)  # b*_0 = beta_0
    contrib = pd.Series(0.0, index=level.index)
    for j in range(H_MAX + 1):
        contrib = contrib + b_star[j] * shock_std.shift(j).reindex(level.index)
    return contrib.rename("oil_attributed_dlog")


def attribution_block(
    name: str,
    level: pd.Series,
    contrib: pd.Series,
    lines: list[str],
) -> None:
    def _win(a: str, b: str, pre: str) -> tuple[float, float]:
        actual = float(level.loc[b] - level.loc[pre])
        attr = float(contrib.loc[a:b].sum())
        return actual, attr

    for label, (a, b, pre) in {
        "2021-01..2025-12 cumulative": ("2021-01-01", "2025-12-01", "2020-12-01"),
        "2022 calendar year": ("2022-01-01", "2022-12-01", "2021-12-01"),
    }.items():
        actual, attr = _win(a, b, pre)
        share = attr / actual if actual != 0 else np.nan
        lines.append(
            f"  {name} {label}: actual {actual:+.2f}pp, "
            f"oil-attributed {attr:+.2f}pp (share {share:.1%})"
        )


# ------------------------------------------------------------------- figures

def _style():
    import matplotlib

    matplotlib.use("Agg")
    import japanize_matplotlib  # noqa: F401
    import matplotlib.pyplot as plt

    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 100
    return plt


C_LINE = "#1f5fbf"
C_BAND = "#1f5fbf"
C_ACT = "#333333"
C_ATTR = "#c2591b"


def _plot_irf(ax, sub: pd.DataFrame, title: str, ylab: str) -> None:
    h = sub["h"]
    ax.fill_between(
        h,
        sub["beta"] - 1.645 * sub["se_hac"],
        sub["beta"] + 1.645 * sub["se_hac"],
        color=C_BAND,
        alpha=0.18,
        lw=0,
        label="90% HAC帯",
    )
    ax.plot(h, sub["beta"], color=C_LINE, lw=2)
    ax.axhline(0, color="#888", lw=0.8, ls=":")
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("ホライズン（月）", fontsize=9)
    ax.set_ylabel(ylab, fontsize=9)
    ax.tick_params(labelsize=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def make_figures(
    irf: pd.DataFrame,
    hd: pd.DataFrame,
) -> None:
    plt = _style()
    full = irf[irf["sample"] == "full"]

    # --- main 2x2
    fig, axes = plt.subplots(2, 2, figsize=(10, 7.5))
    for ax, oc in zip(
        axes.ravel(),
        ["cpi_headline", "cpi_energy_utilities", "cpi_food", "log_import_energy"],
    ):
        sub = full[full["outcome"] == oc].sort_values("h")
        _plot_irf(ax, sub, LABELS[oc], "累積反応（pp, +1SDショック）")
    axes[0, 0].legend(fontsize=8, frameon=False, loc="upper left")
    fig.suptitle(
        "オイル供給ニュースショック（Känzig）への累積反応 2005–2025", fontsize=13
    )
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT_DIR / "fig_irf_main.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- quintiles 2x3
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.5))
    ocs = [f"eff_cpi_q{q}" for q in range(1, 6)] + ["gap_q1_q5"]
    for ax, oc in zip(axes.ravel(), ocs):
        sub = full[full["outcome"] == oc].sort_values("h")
        ylab = (
            "累積格差変化（pp, +1SD）"
            if oc == "gap_q1_q5"
            else "累積反応（pp, +1SD）"
        )
        _plot_irf(ax, sub, LABELS[oc], ylab)
    axes[0, 0].legend(fontsize=8, frameon=False, loc="upper left")
    fig.suptitle("五分位実効CPIの累積反応（2019年固定シェア）", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUT_DIR / "fig_irf_quintiles.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- historical decomposition (cumulative from 2019-01, zoom 2019-2025)
    z = hd.loc["2019-01-01":].copy()
    fig, axes = plt.subplots(2, 1, figsize=(10, 7.5), sharex=True)
    panels = [
        ("headline", "CPI総合インフレ（2019年1月起点の累積, pp）"),
        ("gap", "Q1−Q5実効インフレ格差（2019年1月起点の累積, pp）"),
    ]
    for ax, (key, title) in zip(axes, panels):
        act = z[f"actual_dlog_{key}"].cumsum()
        att = z[f"oil_attributed_dlog_{key}"].cumsum()
        ax.plot(z.index, act, color=C_ACT, lw=2, label="実績")
        ax.plot(
            z.index, att, color=C_ATTR, lw=2, ls="--",
            label="オイルショック帰属分（部分帰属）",
        )
        ax.axhline(0, color="#888", lw=0.8, ls=":")
        ax.set_title(title, fontsize=11)
        ax.tick_params(labelsize=8)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axes[0].legend(fontsize=9, frameon=False, loc="upper left")
    fig.suptitle(
        "ヒストリカル分解（部分帰属: オイル供給ニュースのみ・為替/食料経路は含まず）",
        fontsize=12,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUT_DIR / "fig_hist_decomp.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# -------------------------------------------------------------------- summary

def peak_row(sub: pd.DataFrame) -> pd.Series:
    return sub.loc[sub["beta"].abs().idxmax()]


def build_summary(irf: pd.DataFrame, panel: pd.DataFrame, hd: pd.DataFrame,
                  levels: dict[str, pd.Series]) -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("Oil supply news shock (Känzig) — local projection summary")
    lines.append(
        f"Cumulative LP h=0..{H_MAX}, controls: 12 shock lags + 12 dlog-y "
        f"lags; units = pp per +1 SD shock; HAC maxlags=h+1; "
        f"permutation N={N_PERM}, seed={SEED}."
    )
    lines.append("=" * 72)

    lines.append("\n[Peak IRFs — full sample 2005-01..2025-12]")
    lines.append(
        f"{'outcome':<26} {'h*':>3} {'beta':>8} {'p_hac':>7} {'p_perm':>7} "
        f"{'n_obs(h*)':>9}"
    )
    for oc in OUTCOMES_FULL:
        sub = irf[(irf["outcome"] == oc) & (irf["sample"] == "full")]
        pk = peak_row(sub)
        lines.append(
            f"{oc:<26} {int(pk['h']):>3} {pk['beta']:>8.3f} "
            f"{pk['p_hac']:>7.3f} {pk['p_perm']:>7.3f} {int(pk['n_obs']):>9}"
        )
    lines.append(
        "note: log_import_energy uses the 2015+ BOJ sample only "
        "(n_obs above; short sample, wide bands)."
    )

    lines.append("\n[Pre-COVID robustness 2005-01..2019-12 "
                 "(precovid shock variant — avoids post-2019 VAR leakage)]")
    lines.append(
        f"{'outcome':<26} {'h*':>3} {'beta':>8} {'p_hac':>7} {'p_perm':>7} "
        f"{'n_obs(h*)':>9}"
    )
    for oc in OUTCOMES_PRECOVID:
        sub = irf[(irf["outcome"] == oc) & (irf["sample"] == "precovid")]
        pk = peak_row(sub)
        lines.append(
            f"{oc:<26} {int(pk['h']):>3} {pk['beta']:>8.3f} "
            f"{pk['p_hac']:>7.3f} {pk['p_perm']:>7.3f} {int(pk['n_obs']):>9}"
        )

    # --- success criteria
    def _sig_pos(oc: str, sample: str) -> tuple[bool, pd.DataFrame]:
        sub = irf[(irf["outcome"] == oc) & (irf["sample"] == sample)]
        hit = sub[(sub["beta"] > 0) & (sub["p_hac"] < ALPHA)]
        return len(hit) > 0, hit

    lines.append(f"\n[Success criteria — significance = p_hac < {ALPHA}]")

    ok_a, hit_a = _sig_pos("log_import_energy", "full")
    lines.append(
        f"[A] import_energy IRF positive & significant at some horizon: "
        f"{'PASS' if ok_a else 'FAIL'}"
        + (
            f" (h={sorted(hit_a['h'].astype(int).tolist())})"
            if ok_a
            else ""
        )
    )
    ok_b, hit_b = _sig_pos("cpi_headline", "full")
    lines.append(
        f"[B] headline CPI IRF positive & significant: "
        f"{'PASS' if ok_b else 'FAIL'}"
        + (f" (h={sorted(hit_b['h'].astype(int).tolist())})" if ok_b else "")
    )
    sub_g = irf[(irf["outcome"] == "gap_q1_q5") & (irf["sample"] == "full")]
    pk_g = peak_row(sub_g)
    sig_g = sub_g[sub_g["p_hac"] < ALPHA]
    lines.append(
        f"[C] gap (Q1-Q5) IRF: peak h={int(pk_g['h'])} "
        f"beta={pk_g['beta']:+.3f}pp (p_hac={pk_g['p_hac']:.3f}, "
        f"p_perm={pk_g['p_perm']:.3f}); "
        f"{len(sig_g)} of {len(sub_g)} horizons with p_hac<{ALPHA} "
        f"(h={sorted(sig_g['h'].astype(int).tolist())})"
    )
    d_ok = []
    for oc in OUTCOMES_PRECOVID:
        f_pk = peak_row(
            irf[(irf["outcome"] == oc) & (irf["sample"] == "full")]
        )
        p_pk = peak_row(
            irf[(irf["outcome"] == oc) & (irf["sample"] == "precovid")]
        )
        same = np.sign(f_pk["beta"]) == np.sign(p_pk["beta"])
        d_ok.append(same)
        lines.append(
            f"    [D detail] {oc}: full peak {f_pk['beta']:+.3f} vs "
            f"precovid peak {p_pk['beta']:+.3f} -> "
            f"{'same sign' if same else 'SIGN FLIP'}"
        )
    lines.append(
        f"[D] pre-COVID subsample same signs (peak, all of "
        f"{OUTCOMES_PRECOVID}): {'PASS' if all(d_ok) else 'FAIL'}"
    )

    # --- attribution
    lines.append(
        "\n[Historical decomposition — PARTIAL attribution "
        "(oil supply news only; FX / food-commodity / war non-oil channels "
        "NOT captured)]"
    )
    attribution_block("headline", levels["cpi_headline"],
                      hd["oil_attributed_dlog_headline"], lines)
    attribution_block("gap", levels["gap_q1_q5"],
                      hd["oil_attributed_dlog_gap"], lines)

    lines.append("\n[Decisions / deviations]")
    lines.append(
        "- shock standardized by its ddof=1 SD over each (outcome,sample) "
        "h=0 estimation sample; betas are pp per +1 SD."
    )
    lines.append(
        "- gap outcome cumulates gap_q1_q5_mom_dlog*100 (pp) as the level "
        "object; its beta = pp change of the cumulated Q1-Q5 differential."
    )
    lines.append(
        "- precovid sample uses oil_supply_news_shock_precovid (VAR "
        "estimated through 2019-12) to avoid post-2019 estimation leakage."
    )
    lines.append(
        "- permutation permutes the shock over sample-start-12m..sample-end "
        "and rebuilds all shock lags; n_obs fixed across permutations."
    )
    lines.append(
        "- historical decomposition uses full-sample point IRFs "
        "(differenced cumulative betas); linear partial attribution only."
    )
    return "\n".join(lines)


# ----------------------------------------------------------------------- main

def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    panel, shocks = load_data()

    levels = {oc: build_level(panel, oc) for oc in OUTCOMES_FULL}

    results = []
    for sample, (start, end, shock_col) in SAMPLES.items():
        shock_raw = shocks[shock_col].dropna()
        ocs = OUTCOMES_FULL if sample == "full" else OUTCOMES_PRECOVID
        for oc in ocs:
            print(f"LP: {oc} [{sample}] ...", flush=True)
            res = run_lp(levels[oc], shock_raw, start, end, rng)
            res.insert(0, "sample", sample)
            res.insert(0, "outcome", oc)
            print(
                f"  shock SD={res.attrs['shock_sd']:.3f}, "
                f"n_obs h0/h{H_MAX}: {res['n_obs'].iloc[0]}/"
                f"{res['n_obs'].iloc[-1]}"
            )
            results.append(res)
    irf = pd.concat(results, ignore_index=True)[
        ["outcome", "sample", "h", "beta", "se_hac", "p_hac", "p_perm", "n_obs"]
    ]
    irf.to_csv(OUT_DIR / "irf_results.csv", index=False)

    # historical decomposition (full-sample IRFs, standardized full shock)
    shock_full = shocks["oil_supply_news_shock"].dropna()
    hd_cols = {}
    for key, oc in [("headline", "cpi_headline"), ("gap", "gap_q1_q5")]:
        sub = irf[(irf["outcome"] == oc) & (irf["sample"] == "full")]
        pieces0 = lp_frames(levels[oc], shock_full, *SAMPLES["full"][:2])
        shock_std, _ = standardize_shock(shock_full, pieces0[0].index)
        hd_cols[f"actual_dlog_{key}"] = levels[oc].diff()
        hd_cols[f"oil_attributed_dlog_{key}"] = historical_decomposition(
            sub, levels[oc], shock_std
        )
    hd = pd.DataFrame(hd_cols)
    hd.index.name = "date"
    hd.reset_index().assign(
        date=lambda d: d["date"].dt.strftime("%Y-%m-01")
    ).to_csv(OUT_DIR / "historical_decomposition.csv", index=False)

    summary = build_summary(irf, panel, hd, levels)
    print("\n" + summary)
    (OUT_DIR / "lp_summary.txt").write_text(summary + "\n", encoding="utf-8")

    make_figures(irf, hd)
    print(f"\nSaved outputs to {OUT_DIR}")


if __name__ == "__main__":
    main()
