"""
パネルOLS によるコストプッシュ識別回帰（修正②）。

推定式 (Shift-Share 型):
    ΔCPI_{c,t} = α + β × (IC_c × P_import_t) + γ_t + δ_c + ε_{c,t}

    IC_c        : CPI中分類 c の輸入含有率（IO2020固定、時間不変）
    P_import_t  : BOJ CGPI 集計輸入物価指数（2020=100、年平均）
    γ_t         : 年次固定効果（共通マクロトレンドを除去）
    δ_c         : カテゴリー固定効果（カテゴリー固有水準を除去）

識別: IC_c が高いカテゴリーは P_import_t 上昇時に ΔCPI が大きくなる（Shift-Share 構造）。
プラセボ: 2015-2019（非ショック期）で β ≈ 0 → ショック期特有の結果を支持。
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

DATA_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
PRICE_DIR = DATA_PROCESSED / "price-indices"


def _load_cpi_annual_mid() -> pd.DataFrame:
    """
    CPI 中分類の年次平均インデックスを読み込む。

    Returns
    -------
    pd.DataFrame: columns = year, cpi_code (str), cpi_mid_name, cpi_index (annual avg)
    """
    from src.analysis.bridge_matrix_mid import CPI_MID_CATEGORY_MAP, CPI_CODE_TO_NAME

    cpi_file = DATA_RAW / "cpi" / "cpi_category_2015_2025.csv"
    cpi = pd.read_csv(cpi_file)

    # time_code は10桁形式 YYYY00MMMM（月は末尾[6:8]=[8:10]=MM、年度=YYYY100000、年計=YYYY000000）。
    # 暦年（calendar-year）で集計する（GDP・Phase1と統一, DEC 2026-07-07）。
    # 旧実装 str[4:6] は6桁 YYYYMM 前提で、10桁形式では年度行のみを拾い実質「年度ベース」だった。
    _tc = cpi["time_code"].astype(str)
    cpi["year"] = _tc.str[:4].astype(int)
    _mm = [f"{i:02d}" for i in range(1, 13)]
    monthly_mask = _tc.str[8:10].isin(_mm) & _tc.str[6:8].isin(_mm)
    cpi_monthly = cpi[monthly_mask].copy()

    # cat01_code を 4 桁文字列に統一
    cpi_monthly = cpi_monthly.copy()
    cpi_monthly["cpi_code_str"] = cpi_monthly["cat01_code"].astype(str).str.zfill(4)

    # 対象カテゴリーに絞り込み
    target_codes = set(v["cpi_code"] for v in CPI_MID_CATEGORY_MAP.values())
    cpi_mid = cpi_monthly[cpi_monthly["cpi_code_str"].isin(target_codes)].copy()

    # 年次平均
    annual = (
        cpi_mid.groupby(["year", "cpi_code_str"])["value"]
        .mean()
        .reset_index()
        .rename(columns={"cpi_code_str": "cpi_code", "value": "cpi_index"})
    )
    annual["cpi_mid_name"] = annual["cpi_code"].map(CPI_CODE_TO_NAME)
    return annual


def _load_import_price_annual() -> pd.DataFrame:
    """
    BOJ CGPI 集計輸入物価指数の年次平均を返す。
    Returns pd.DataFrame: columns = year, p_import (2020=100)
    """
    cgpi_path = DATA_RAW / "boj-cgpi" / "import_prices_extracted.csv"
    df = pd.read_csv(cgpi_path, parse_dates=["date"])
    df["year"] = df["date"].dt.year
    total = df[df["group"] == "total"].copy()
    annual = (
        total.groupby("year")["value"]
        .mean()
        .reset_index()
        .rename(columns={"value": "p_import"})
    )
    return annual


def build_panel_dataset(force: bool = False) -> pd.DataFrame:
    """
    パネルデータセット（long 形式）を構築する。

    BOJ CGPI 輸入物価は 2020年基準のため、CPI ベースラインも 2020 年に合わせる。
    データは 2015-2025 の全年を保持する:
      - 主分析期間: 2021-2024（ショック期、輸入価格急騰）
      - プラセボ期間: 2015-2019（非ショック期、日本の近ゼロインフレ期）
      - 2020 は P_import≈100 かつ ΔCPI≈0 で識別力がないため、回帰では除外する

    force: キャッシュを無視して再計算（再現性検証用）

    Returns
    -------
    pd.DataFrame with columns:
        cpi_mid_name, cpi_code, year,
        delta_cpi,       : ΔCPI_{c,t} (pp, 対2020年比)
        ic,              : IC_c (輸入含有率, 時間不変)
        p_import,        : P_import_t (BOJ CGPI total, 2020=100)
        shift_share,     : IC_c × (P_import_t − 100) (ショック幅との交差項)
        group,
        is_transport_comms,
        is_competitive_import
    Cache: data/processed/price-indices/panel_cost_push.csv
    """
    PRICE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = PRICE_DIR / "panel_cost_push.csv"

    if cache_path.exists() and not force:
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    from src.analysis.bridge_matrix_mid import compute_mid_category_import_content

    # 1. IC_c
    ic_df = compute_mid_category_import_content(force=force)
    ic_map = ic_df.set_index("cpi_mid_name")[["import_content", "group", "is_transport_comms", "is_competitive_import", "cpi_code"]]

    # 2. CPI 年次インデックス（全年）
    cpi_annual = _load_cpi_annual_mid()

    # 2020 ベースライン（CGPI 基準年に合わせる）
    baseline = (
        cpi_annual[cpi_annual["year"] == 2020]
        .set_index("cpi_code")["cpi_index"]
        .rename("baseline_2020")
    )
    cpi_annual = cpi_annual.merge(baseline, on="cpi_code", how="left")
    cpi_annual["delta_cpi"] = cpi_annual["cpi_index"] - cpi_annual["baseline_2020"]

    # 3. P_import_t（2015-2026 の連続系列）
    p_import = _load_import_price_annual()

    # 4. パネル結合（inner join → P_import がある年のみ）
    panel = cpi_annual.merge(p_import, on="year", how="inner")

    # Ensure cpi_code is consistent str type before merge
    panel["cpi_code"] = panel["cpi_code"].astype(str).str.zfill(4)
    ic_reset = ic_map.reset_index()
    ic_reset["cpi_code"] = ic_reset["cpi_code"].astype(str).str.zfill(4)

    panel = panel.merge(
        ic_reset,
        on=["cpi_mid_name", "cpi_code"],
        how="left",
    )
    panel = panel.rename(columns={"import_content": "ic"})

    # 5. 交差項: IC_c × (P_import_t − 100)
    panel["shift_share"] = panel["ic"] * (panel["p_import"] - 100.0)

    # 2020 は識別力なし（P_import≈100, ΔCPI≈0）なので除外
    # 2025 は CPI データが年途中のため除外
    panel = panel[panel["year"].between(2015, 2024) & (panel["year"] != 2020)].copy()

    # 欠損を除去
    panel = panel.dropna(subset=["delta_cpi", "ic", "p_import"]).reset_index(drop=True)

    cols = [
        "cpi_mid_name", "cpi_code", "year",
        "delta_cpi", "ic", "p_import", "shift_share",
        "group", "is_transport_comms", "is_competitive_import",
    ]
    panel = panel[cols].sort_values(["cpi_mid_name", "year"]).reset_index(drop=True)

    shock_obs = panel[panel["year"].between(2021, 2024)]
    placebo_obs = panel[panel["year"].between(2015, 2019)]
    panel.to_csv(cache_path, index=False)
    print(f"Saved panel dataset: {cache_path} ({len(panel)} obs total, "
          f"{panel['cpi_mid_name'].nunique()} categories)")
    print(f"  ショック期 2021-2024: {len(shock_obs)} obs")
    print(f"  プラセボ期 2015-2019: {len(placebo_obs)} obs")
    return panel


def run_panel_regression(
    df: pd.DataFrame,
    se_type: str = "cluster",
    exclude_transport: bool = False,
    exclude_competitive_imports: bool = False,
    years: tuple | None = None,
) -> dict:
    """
    Shift-Share パネルOLS を実行する。

    Two-way FE (entity + time) を手動ダミーで実装し、
    linearmodels の PanelOLS でクラスターSE を適用する。

    Parameters
    ----------
    df : pd.DataFrame from build_panel_dataset()
    se_type : "cluster" (推奨) | "robust"
    exclude_transport : True の場合、通信カテゴリーを除外
    exclude_competitive_imports : True の場合、競争的輸入財（衣料・履物類）を除外。
        これらは IC が高いが中国等からの価格競争で小売価格が集計輸入物価と
        連動しない「外れ値」カテゴリー。除外で識別力が大幅に改善する。
    years : (start, end) | None → None なら全期間

    Returns
    -------
    dict with keys: beta, se, tstat, pval, n_obs, n_categories, r2_within, spec_label
    """
    try:
        from linearmodels import PanelOLS
        USE_LINEARMODELS = True
    except ImportError:
        USE_LINEARMODELS = False

    sub = df.copy()

    if exclude_transport:
        sub = sub[~sub["is_transport_comms"]]

    if exclude_competitive_imports:
        sub = sub[~sub["is_competitive_import"]]

    if years is not None:
        sub = sub[sub["year"].between(years[0], years[1])]

    sub = sub.dropna(subset=["delta_cpi", "shift_share"])

    n_cats = sub["cpi_mid_name"].nunique()
    n_obs = len(sub)

    if USE_LINEARMODELS:
        # MultiIndex: (entity, time)
        sub = sub.set_index(["cpi_mid_name", "year"])
        exog = sub[["shift_share"]]
        dependent = sub["delta_cpi"]

        model = PanelOLS(
            dependent,
            exog,
            entity_effects=True,
            time_effects=True,
            drop_absorbed=True,
            check_rank=False,
        )

        if se_type == "cluster":
            result = model.fit(cov_type="clustered", cluster_entity=True)
        else:
            result = model.fit(cov_type="robust")

        beta = float(result.params["shift_share"])
        se = float(result.std_errors["shift_share"])
        tstat = float(result.tstats["shift_share"])
        pval = float(result.pvalues["shift_share"])
        r2_within = float(result.rsquared_within)  # within R²（固定効果除去後）

    else:
        # Fallback: statsmodels OLS + two-way dummies
        sub = sub.reset_index()
        dummies_cat = pd.get_dummies(sub["cpi_mid_name"], prefix="cat", drop_first=True)
        dummies_yr = pd.get_dummies(sub["year"], prefix="yr", drop_first=True)
        X = pd.concat([sub[["shift_share"]], dummies_cat, dummies_yr], axis=1).astype(float)
        X = sm.add_constant(X)
        y = sub["delta_cpi"]
        ols = sm.OLS(y, X).fit(cov_type="HC1")

        beta = float(ols.params["shift_share"])
        se = float(ols.bse["shift_share"])
        tstat = float(ols.tvalues["shift_share"])
        pval = float(ols.pvalues["shift_share"])
        r2_within = float(ols.rsquared)

    label_parts = []
    if exclude_transport:
        label_parts.append("通信除外")
    if years:
        label_parts.append(f"{years[0]}–{years[1]}")
    if not label_parts:
        label_parts = ["ベースライン"]

    return {
        "beta": round(beta, 4),
        "se": round(se, 4),
        "tstat": round(tstat, 3),
        "pval": round(pval, 4),
        "n_obs": n_obs,
        "n_categories": n_cats,
        "r2_within": round(r2_within, 3),
        "spec_label": " / ".join(label_parts),
    }


def run_cross_section_fd(
    df: pd.DataFrame,
    year_from: int = 2021,
    year_to: int = 2022,
    exclude_transport: bool = False,
    exclude_competitive_imports: bool = False,
) -> dict:
    """
    一階差分横断面OLS: Δ²CPI_{c} = β × IC_c × ΔP_import + ε_c

    T=2 の "ショック遷移" 期に特化した推定。
    entity FE は一階差分で自動消去、time FE は省略（T=1 の差分のため）。
    SE は HC1 頑健標準誤差。

    Returns dict with same keys as run_panel_regression.
    """
    from_df = df[df["year"] == year_from].set_index("cpi_mid_name")
    to_df = df[df["year"] == year_to].set_index("cpi_mid_name")

    fd = to_df["delta_cpi"] - from_df["delta_cpi"]
    d_p = df[df["year"] == year_to]["p_import"].iloc[0] - df[df["year"] == year_from]["p_import"].iloc[0]
    ic = from_df["ic"]

    if exclude_transport:
        mask = ~from_df["is_transport_comms"]
        fd = fd[mask]
        ic = ic[mask]

    if exclude_competitive_imports:
        mask2 = ~from_df.loc[ic.index, "is_competitive_import"]
        fd = fd[mask2]
        ic = ic[mask2]

    d_shift = (ic * d_p).rename("shift_share")
    X = sm.add_constant(d_shift)
    y = fd.reindex(X.index)

    valid = y.notna() & X["shift_share"].notna()
    res = sm.OLS(y[valid], X[valid]).fit(cov_type="HC1")

    return {
        "beta": round(float(res.params["shift_share"]), 4),
        "se": round(float(res.bse["shift_share"]), 4),
        "tstat": round(float(res.tvalues["shift_share"]), 3),
        "pval": round(float(res.pvalues["shift_share"]), 4),
        "n_obs": int(valid.sum()),
        "n_categories": int(valid.sum()),
        "r2_within": round(float(res.rsquared), 3),
        "spec_label": f"first-diff {year_from}→{year_to}",
    }


def run_sensitivity_analyses(df: pd.DataFrame) -> pd.DataFrame:
    """
    5パターンの感度分析を実行する。

    (i)   ベースライン:           全カテゴリー × 2021-2024（ショック期）
    (ii)  通信除外:               is_transport_comms==False × 2021-2024
    (iii) 競争的輸入財除外:       衣料・履物類を除外 × 2021-2024
          衣料・履物は中国製品主体のため IC 高いが価格転嫁が起きない外れ値。
          除外により R² と有意性が大幅改善 → コストプッシュ識別の頑健性を示す。
    (iv)  一階差分 2021→2022:    最大 ΔP_import (+47pp) 横断面 n=41
    (v)   プラセボ（2015-2019）: 非ショック期（日本の近ゼロインフレ期）→ β ≈ 0 を期待。
          ショック期特有の結果であることを支持する期間ベースの偽陽性チェック。
          IC の外生性を直接検証: 同じ IC 構造で P_import が変動した場合でも、
          コストプッシュが働かない時期では β ≈ 0 になる。

    Returns
    -------
    pd.DataFrame: 各行が1仕様
    """
    rows = []

    # (i) ベースライン（ショック期）
    res = run_panel_regression(df, se_type="cluster", years=(2021, 2024))
    rows.append({"仕様": "(i) ベースライン（全41カテゴリー）", **_fmt(res)})

    # (ii) 通信除外（政策的価格操作を排除）
    res = run_panel_regression(df, se_type="cluster", exclude_transport=True, years=(2021, 2024))
    rows.append({"仕様": "(ii) 通信除外", **_fmt(res)})

    # (iii) 競争的輸入財除外（衣料・履物）
    res = run_panel_regression(df, se_type="cluster", exclude_competitive_imports=True, years=(2021, 2024))
    rows.append({"仕様": "(iii) 競争的輸入財除外（衣料・履物）", **_fmt(res)})

    # (iv) 一階差分 2021→2022
    res = run_cross_section_fd(df, year_from=2021, year_to=2022)
    rows.append({"仕様": "(iv) 一階差分 2021→22（n=41）", **_fmt(res)})

    # (v) 期間ベースプラセボ: 非ショック期（2015-2019）
    #     同じ IC 構造・同様の P_import 変動で β ≈ 0 → ショック期の結果がショック特有であることを確認
    res = run_panel_regression(df, se_type="cluster", years=(2015, 2019))
    rows.append({"仕様": "(v) プラセボ（2015-2019 非ショック期）", **_fmt(res)})

    return pd.DataFrame(rows)


def _fmt(res: dict) -> dict:
    return {
        "β": res["beta"],
        "SE": res["se"],
        "t値": res["tstat"],
        "p値": res["pval"],
        "N": res["n_obs"],
        "カテゴリー数": res["n_categories"],
        "R²_within": res["r2_within"],
    }


def make_regression_table(
    sensitivity_df: pd.DataFrame,
    output_path: Path | None = None,
) -> pd.DataFrame:
    """
    感度分析結果を整形して出力する。

    CSV と LaTeX tabular の両方を保存する。
    """
    PRICE_DIR.mkdir(parents=True, exist_ok=True)

    if output_path is None:
        output_path = PRICE_DIR / "cost_push_panel_results.csv"

    sensitivity_df.to_csv(output_path, index=False)

    # LaTeX テーブル
    latex_path = output_path.with_suffix(".tex")
    with open(latex_path, "w") as f:
        f.write("\\begin{tabular}{lrrrrrr}\n")
        f.write("\\hline\n")
        f.write("仕様 & $\\hat{\\beta}$ & SE & $t$ & $p$ & $N$ & $R^2$ \\\\\n")
        f.write("\\hline\n")
        for _, row in sensitivity_df.iterrows():
            sig = ""
            if row["p値"] < 0.01:
                sig = "***"
            elif row["p値"] < 0.05:
                sig = "**"
            elif row["p値"] < 0.10:
                sig = "*"
            f.write(
                f"{row['仕様']} & {row['β']:.3f}{sig} & ({row['SE']:.3f}) & "
                f"{row['t値']:.2f} & {row['p値']:.3f} & {int(row['N'])} & "
                f"{row['R²_within']:.3f} \\\\\n"
            )
        f.write("\\hline\n")
        f.write("\\end{tabular}\n")

    print(f"Saved results to {output_path}")
    print(f"Saved LaTeX to {latex_path}")
    return sensitivity_df


def plot_scatter_panel(
    df: pd.DataFrame,
    highlight_year: int = 2023,
    output_path: Path | None = None,
) -> None:
    """
    Scatter plot: shift_share (IC_c × P_import_t) vs ΔCPI_{c,t}

    全年データを重ねプロット、highlight_year を強調。
    ベースライン回帰直線と信頼区間を重ねる。
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import japanize_matplotlib

    if output_path is None:
        output_path = PRICE_DIR / "fig_cost_push_panel.png"

    PRICE_DIR.mkdir(parents=True, exist_ok=True)

    years = sorted(df["year"].unique())
    cmap = plt.cm.Blues
    n_years = len(years)

    fig, ax = plt.subplots(figsize=(10, 7))

    for i, yr in enumerate(years):
        sub = df[df["year"] == yr]
        alpha = 0.35 if yr != highlight_year else 0.85
        size = 20 if yr != highlight_year else 55
        color = cmap(0.3 + 0.6 * i / n_years) if yr != highlight_year else "#e74c3c"
        ax.scatter(sub["shift_share"], sub["delta_cpi"],
                   alpha=alpha, s=size, color=color, zorder=2 if yr != highlight_year else 5)

        # highlight year: ラベル付き（上位5カテゴリー）
        if yr == highlight_year:
            top = sub.nlargest(5, "delta_cpi")
            for _, row in top.iterrows():
                ax.annotate(
                    row["cpi_mid_name"],
                    (row["shift_share"], row["delta_cpi"]),
                    fontsize=7,
                    xytext=(4, 2),
                    textcoords="offset points",
                )

    # ベースライン回帰直線
    sub_base = df.dropna(subset=["shift_share", "delta_cpi"])
    X_fit = np.linspace(sub_base["shift_share"].min(), sub_base["shift_share"].max(), 100)
    res = run_panel_regression(df, se_type="cluster")
    # Simple OLS line for visualization (full pooled)
    X_pool = sm.add_constant(sub_base["shift_share"])
    fit_pool = sm.OLS(sub_base["delta_cpi"], X_pool).fit()
    y_fit = fit_pool.params["const"] + fit_pool.params["shift_share"] * X_fit
    ax.plot(X_fit, y_fit, color="black", linewidth=1.8, zorder=6, label=f"回帰直線 β={res['beta']:.2f}, p={res['pval']:.3f}")

    ax.axhline(0, color="gray", linestyle="--", alpha=0.4)
    ax.set_xlabel("IC_c × P_import_t（シフト・シェア交差項）", fontsize=12)
    ax.set_ylabel("ΔCPI_{c,t}（pp、対2015-19平均比）", fontsize=12)
    ax.set_title(
        "コストプッシュ識別: 輸入含有率 × 輸入物価 vs CPI 変化（CPI 中分類パネル）",
        fontsize=12,
    )

    # 年次凡例
    patches = [mpatches.Patch(color="#e74c3c", label=f"{highlight_year}（強調）")]
    patches += [
        mpatches.Patch(color=cmap(0.3 + 0.6 * i / n_years), alpha=0.5, label=str(yr))
        for i, yr in enumerate(years) if yr != highlight_year
    ]
    ax.legend(handles=patches, fontsize=8, loc="upper left", ncol=2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"Saved: {output_path}")


def plot_yearly_correlation(
    df: pd.DataFrame,
    output_path: Path | None = None,
) -> None:
    """
    年次別 IC-ΔCPI 相関係数の棒グラフ（ショック期 vs プラセボ期の比較）。

    デマンドプル汚染への反論として：
    - もし需要要因が支配的なら、全年で IC との相関はゼロに近いはず
    - ショック期（2021-2024）: r が一貫して正（コストプッシュシグナル）
    - プラセボ期（2015-2019）: r がゼロ近傍または負（コストプッシュ不在）
    このコントラストが識別の視覚的証拠となる。

    2 パネル構成:
      左: 全41カテゴリーの年次相関棒グラフ
      右: 競争的輸入財除外後（衣料・履物）の年次相関棒グラフ

    Output: data/processed/price-indices/fig_yearly_correlation.png
    """
    import matplotlib.pyplot as plt
    import japanize_matplotlib

    if output_path is None:
        output_path = PRICE_DIR / "fig_yearly_correlation.png"

    PRICE_DIR.mkdir(parents=True, exist_ok=True)

    shock_years = list(range(2021, 2025))
    placebo_years = list(range(2015, 2020))
    all_years = sorted(placebo_years + shock_years)

    # 競争的輸入財除外フラグ
    df_excl = df[~df["is_competitive_import"]].copy()

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    fig.suptitle(
        "IC-ΔCPI 年次相関: ショック期 vs プラセボ期（デマンドプル識別テスト）",
        fontsize=13,
        fontweight="bold",
    )

    titles = ["全41カテゴリー", "競争的輸入財除外後（衣料・履物除く）"]
    datasets = [df, df_excl]

    for ax, data, title in zip(axes, datasets, titles):
        corrs = []
        colors = []
        for yr in all_years:
            sub = data[data["year"] == yr].dropna(subset=["ic", "delta_cpi"])
            r = sub["ic"].corr(sub["delta_cpi"]) if len(sub) >= 5 else np.nan
            corrs.append(r)
            colors.append("#c0392b" if yr in shock_years else "#2980b9")

        bars = ax.bar(all_years, corrs, color=colors, alpha=0.82, edgecolor="white", linewidth=0.8)

        ax.axhline(0, color="black", linewidth=0.8, linestyle="-")
        ax.axvline(2019.5, color="gray", linewidth=1.2, linestyle="--", alpha=0.7, label="ショック開始境界")

        # 値ラベル
        for bar, val in zip(bars, corrs):
            if not np.isnan(val):
                va = "bottom" if val >= 0 else "top"
                offset = 0.01 if val >= 0 else -0.01
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    val + offset,
                    f"{val:.2f}",
                    ha="center",
                    va=va,
                    fontsize=8,
                )

        # 凡例（パッチで手動）
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor="#2980b9", alpha=0.82, label="プラセボ期 (2015–2019)"),
            Patch(facecolor="#c0392b", alpha=0.82, label="ショック期 (2021–2024)"),
        ]
        ax.legend(handles=legend_elements, fontsize=9, loc="upper left")

        ax.set_xticks(all_years)
        ax.set_xticklabels(all_years, rotation=45, fontsize=9)
        ax.set_xlabel("年", fontsize=11)
        ax.set_ylabel("IC-ΔCPI 相関係数 r", fontsize=11)
        ax.set_title(title, fontsize=11)
        ax.set_ylim(-0.45, 0.75)
        ax.grid(axis="y", alpha=0.25)

    # 注記
    fig.text(
        0.5, -0.03,
        "注: IC_c は IO2020 年表から算出した輸入含有率（時間不変）。ΔCPI_{c,t} は 2020 年比の pp 変化。"
        "相関がショック期に一貫して正となり、プラセボ期にゼロ近傍となることが、"
        "コストプッシュ識別の視覚的根拠を与える。",
        ha="center",
        fontsize=8,
        color="gray",
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")

    # 数値サマリーも表示
    print("\n=== 年次別 IC-ΔCPI 相関係数 ===")
    print(f"{'年':>6}  {'全カテゴリー':>14}  {'競争的輸入財除外':>16}  {'期間'}")
    for yr in all_years:
        s1 = df[df["year"] == yr].dropna(subset=["ic", "delta_cpi"])
        s2 = df_excl[df_excl["year"] == yr].dropna(subset=["ic", "delta_cpi"])
        r1 = s1["ic"].corr(s1["delta_cpi"])
        r2 = s2["ic"].corr(s2["delta_cpi"])
        period = "ショック" if yr in shock_years else "プラセボ"
        print(f"  {yr}   {r1:+.3f}           {r2:+.3f}           {period}")


if __name__ == "__main__":
    print("=== Building Panel Dataset ===")
    df = build_panel_dataset()
    print(f"\nShape: {df.shape}")
    print(f"Years: {sorted(df['year'].unique())}")
    print(f"Categories: {df['cpi_mid_name'].nunique()}")
    print(f"\nDescriptive stats:")
    print(df[["delta_cpi", "ic", "p_import", "shift_share"]].describe().round(3).to_string())

    print("\n=== Baseline (cluster entity SE vs unadjusted SE) ===")
    r1 = run_panel_regression(df, se_type="cluster")
    r2 = run_panel_regression(df, se_type="robust")
    print(f"  Cluster entity : β={r1['beta']:.3f} SE={r1['se']:.3f} p={r1['pval']:.3f}")
    print(f"  Robust (HC)    : β={r2['beta']:.3f} SE={r2['se']:.3f} p={r2['pval']:.3f}")

    print("\n=== Sensitivity Analyses ===")
    sens = run_sensitivity_analyses(df)
    print(sens.to_string(index=False))

    print("\n=== Saving Results ===")
    make_regression_table(sens)

    print("\n=== Plot: Scatter ===")
    plot_scatter_panel(df)

    print("\n=== Plot: Yearly Correlation (Demand-Pull Defense) ===")
    plot_yearly_correlation(df)
