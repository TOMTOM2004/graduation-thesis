"""
円安の会計分解（FX decomposition of import price inflation）.

BOJ 輸入物価指数の 円ベース（PRCG20_26xx）と 契約通貨ベース（PRCG20_25xx）の
対数差分の差を「為替要因」とする恒等式ベースの会計分解。識別仮定なし。

    Δlog P_yen − Δlog P_contract = 為替要因（機械的寄与）
    Δlog P_contract               = 海外価格要因（契約通貨建て価格の変化）

対象系列: 総平均 / 石油・石炭・天然ガス（energy） / 飲食料品・食料用農水産物（food）
期間: 2015-01 〜 最新（cgpilink1.csv + cgpi_m_jp.zip、2020=100）

出力:
- data/raw/boj-cgpi/import_prices_both_bases.csv   （生抽出、既存ファイルは不変更）
- data/processed/fx-decomp/fx_decomp_monthly.csv    （月次 YoY 分解）
- data/processed/fx-decomp/fx_decomp_calendar_year.csv（暦年分解表 2021-2025）
- data/processed/fx-decomp/fx_decomp_cumulative.csv （2020-12 起点の累積分解）
- data/processed/fx-decomp/fig_fx_decomp.png        （2パネル図）
- data/processed/fx-decomp/fx_decomp_summary.txt    （サマリー）
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from data.fetch_import_prices import (  # noqa: E402
    RAW_DIR,
    load_cgpi_link_raw,
    load_cgpi_raw,
)

OUT_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "fx-decomp"

# 分析ウィンドウの終端（生抽出はフル期間を保持、分析はここで切る）
ANALYSIS_END = pd.Timestamp("2025-12-01")

# 円ベース（yen）と契約通貨ベース（contract）の並行系列コード
# 円ベース: PRCG20_26xxxxxxxx / 契約通貨ベース: PRCG20_25xxxxxxxx
SERIES = {
    "total": {
        "name": "総平均",
        "yen": "PRCG20_2600000000",
        "contract": "PRCG20_2500000000",
    },
    "energy": {
        "name": "石油・石炭・天然ガス",
        "yen": "PRCG20_2600520001",
        "contract": "PRCG20_2500520001",
    },
    "food": {
        "name": "飲食料品・食料用農水産物",
        "yen": "PRCG20_2600120001",
        "contract": "PRCG20_2500120001",
    },
}


def _extract(df: pd.DataFrame, codes: dict[str, tuple[str, str]],
             filter_years=None) -> pd.DataFrame:
    """Extract multiple series codes from a wide CGPI dataframe → long format."""
    code_col = df.columns[0]
    date_cols = [c for c in df.columns[3:] if str(c).isdigit() and len(str(c)) == 6]
    rows = []
    for code, (group, basis) in codes.items():
        sub = df.loc[df[code_col] == code]
        if sub.empty:
            continue
        row = sub.iloc[0]
        for date_str in date_cols:
            val = row.get(date_str)
            if pd.notna(val):
                year = int(str(date_str)[:4])
                if filter_years and year not in filter_years:
                    continue
                month = int(str(date_str)[4:6])
                rows.append({
                    "date": pd.Timestamp(year, month, 1),
                    "group": group,
                    "basis": basis,
                    "value": float(val),
                })
    return pd.DataFrame(rows)


def extract_both_bases() -> pd.DataFrame:
    """円ベース＋契約通貨ベースの輸入物価指数を 2015-01〜最新まで抽出."""
    cache_path = RAW_DIR / "import_prices_both_bases.csv"
    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path, parse_dates=["date"])

    codes = {}
    for group, spec in SERIES.items():
        codes[spec["yen"]] = (group, "yen")
        codes[spec["contract"]] = (group, "contract")

    df_link = _extract(load_cgpi_link_raw(), codes, filter_years=range(2015, 2020))
    df_zip = _extract(load_cgpi_raw(), codes)

    result = (
        pd.concat([df_link, df_zip], ignore_index=True)
        .sort_values(["group", "basis", "date"])
        .drop_duplicates(subset=["group", "basis", "date"])
        .reset_index(drop=True)
    )
    result.to_csv(cache_path, index=False)
    print(f"Saved {cache_path} ({len(result)} rows, "
          f"{result['date'].min().date()} – {result['date'].max().date()})")
    return result


def build_panel(df: pd.DataFrame) -> pd.DataFrame:
    """Wide panel: index (date) × columns (group, basis) → log levels."""
    wide = df.pivot_table(index="date", columns=["group", "basis"], values="value")
    return wide.sort_index()


def sanity_check_yen_basis(df: pd.DataFrame) -> str:
    """円ベース系列が既存キャッシュ import_prices_extracted.csv と一致するか確認."""
    lines = ["== Sanity check 1: 円ベース vs 既存 import_prices_extracted.csv =="]
    existing = pd.read_csv(RAW_DIR / "import_prices_extracted.csv", parse_dates=["date"])
    for group in SERIES:
        old = existing[existing["group"] == group].set_index("date")["value"]
        new = (df[(df["group"] == group) & (df["basis"] == "yen")]
               .set_index("date")["value"])
        common = old.index.intersection(new.index)
        diff = (old.loc[common] - new.loc[common]).abs()
        in_win = diff[diff.index <= ANALYSIS_END]
        out_win = diff[diff.index > ANALYSIS_END]
        lines.append(
            f"  {group}: overlap {len(common)} months, "
            f"max |diff| (≤2025-12, 分析窓) = {in_win.max():.6g}, "
            f"max |diff| (2026-, 速報改定) = "
            f"{out_win.max():.6g}" if len(out_win) else
            f"  {group}: overlap {len(common)} months, max |diff| = {diff.max():.6g}"
        )
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df = extract_both_bases()
    panel = build_panel(df)
    panel = panel.loc[panel.index <= ANALYSIS_END]
    logp = np.log(panel)

    # ---------- (i) 月次 YoY Δlog 分解 ----------
    yoy = (logp - logp.shift(12)) * 100  # log-pt (%)
    monthly = []
    for group in SERIES:
        m = pd.DataFrame({
            "date": yoy.index,
            "group": group,
            "yoy_yen_logpct": yoy[(group, "yen")].values,
            "yoy_contract_logpct": yoy[(group, "contract")].values,
        })
        m["yoy_fx_logpct"] = m["yoy_yen_logpct"] - m["yoy_contract_logpct"]
        monthly.append(m)
    monthly = pd.concat(monthly, ignore_index=True).dropna(subset=["yoy_yen_logpct"])
    monthly.to_csv(OUT_DIR / "fx_decomp_monthly.csv", index=False)

    # ---------- (ii) 暦年分解表 2021-2025 ----------
    # 暦年平均指数の対数変化率で分解（恒等式が厳密に保存される）
    ann = panel.groupby(panel.index.year).mean()
    log_ann = np.log(ann)
    dlog_ann = (log_ann - log_ann.shift(1)) * 100

    cy_rows = []
    for year in range(2021, 2026):
        for group in SERIES:
            total = dlog_ann.loc[year, (group, "yen")]
            contract = dlog_ann.loc[year, (group, "contract")]
            fx = total - contract
            cy_rows.append({
                "year": year,
                "group": group,
                "group_ja": SERIES[group]["name"],
                "total_yen_logpct": round(total, 2),
                "foreign_price_logpct": round(contract, 2),
                "fx_logpct": round(fx, 2),
                "foreign_price_share_pct": round(100 * contract / total, 1)
                if abs(total) > 1e-9 else np.nan,
                "fx_share_pct": round(100 * fx / total, 1)
                if abs(total) > 1e-9 else np.nan,
            })
    cy = pd.DataFrame(cy_rows)
    cy.to_csv(OUT_DIR / "fx_decomp_calendar_year.csv", index=False)

    # ---------- (iii) 累積分解（2020-12 起点） ----------
    base = pd.Timestamp("2020-12-01")
    cum = (logp - logp.loc[base]) * 100
    cum = cum.loc[cum.index >= base]

    cum_rows = []
    for group in SERIES:
        cy_yen = cum[(group, "yen")]
        peak_date = cy_yen.idxmax()
        for label, dt in [("peak", peak_date),
                          ("2025-12", pd.Timestamp("2025-12-01"))]:
            if dt not in cum.index:
                dt = cum.index.max()
                label = f"latest({dt.date()})"
            total = cum.loc[dt, (group, "yen")]
            contract = cum.loc[dt, (group, "contract")]
            fx = total - contract
            cum_rows.append({
                "group": group,
                "point": label,
                "date": dt.date(),
                "cum_total_yen_logpct": round(total, 2),
                "cum_foreign_price_logpct": round(contract, 2),
                "cum_fx_logpct": round(fx, 2),
                "foreign_price_share_pct": round(100 * contract / total, 1),
                "fx_share_pct": round(100 * fx / total, 1),
                "index_yen": round(panel.loc[dt, (group, "yen")], 1),
                "index_contract": round(panel.loc[dt, (group, "contract")], 1),
            })
    cum_df = pd.DataFrame(cum_rows)
    cum_df.to_csv(OUT_DIR / "fx_decomp_cumulative.csv", index=False)

    # ---------- 図 ----------
    import matplotlib
    matplotlib.use("Agg")
    import japanize_matplotlib  # noqa: F401
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharex=True)
    panel_specs = [("total", "総平均"), ("energy", "石油・石炭・天然ガス")]
    for ax, (group, title) in zip(axes, panel_specs):
        x = cum.index
        contract_c = cum[(group, "contract")]
        fx_c = cum[(group, "yen")] - cum[(group, "contract")]
        ax.stackplot(
            x, contract_c, fx_c,
            labels=["海外価格要因（契約通貨ベース）", "為替要因（円安）"],
            colors=["#4878A8", "#D1495B"], alpha=0.85,
        )
        ax.plot(x, cum[(group, "yen")], color="#222222", lw=1.6,
                label="輸入物価（円ベース）累積変化")
        ax.axhline(0, color="gray", lw=0.6)
        ax.set_title(title, fontsize=13)
        ax.set_ylabel("2020年12月比 累積対数変化率（%）")
        ax.legend(fontsize=9, loc="upper left", frameon=False)
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("輸入物価上昇の会計分解：海外価格要因 vs 為替要因（恒等式・識別仮定なし）",
                 fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(OUT_DIR / "fig_fx_decomp.png", dpi=200)
    plt.close(fig)

    # ---------- サマリー ----------
    sanity1 = sanity_check_yen_basis(df)

    # 定性チェック: 円ベース 2022 年ピーク水準と契約通貨ベースの乖離
    yen_total = panel[("total", "yen")]
    con_total = panel[("total", "contract")]
    peak22 = yen_total.loc["2022"].idxmax()
    sanity2 = (
        "== Sanity check 2: 定性チェック（講義ノートの様式化事実） ==\n"
        f"  円ベース総平均 2022年ピーク: {yen_total.loc['2022'].max():.1f} "
        f"({peak22.strftime('%Y-%m')}, 2020=100)\n"
        f"  同月の契約通貨ベース: {con_total.loc[peak22]:.1f}\n"
        f"  乖離（円/契約, log%）: "
        f"{100 * (np.log(yen_total.loc[peak22]) - np.log(con_total.loc[peak22])):.1f}\n"
        f"  乖離の推移（12月時点, log%）: "
        + ", ".join(
            f"{y}={100 * (np.log(yen_total.loc[f'{y}-12-01']) - np.log(con_total.loc[f'{y}-12-01'])):.1f}"
            for y in range(2021, 2026)
            if pd.Timestamp(f"{y}-12-01") in yen_total.index
        )
    )

    with open(OUT_DIR / "fx_decomp_summary.txt", "w") as f:
        f.write("円安の会計分解（輸入物価指数 円ベース vs 契約通貨ベース）\n")
        f.write("恒等式: Δlog P_yen − Δlog P_contract = 為替要因（識別仮定なし）\n")
        f.write(f"データ: BOJ CGPI 2020年基準（cgpilink1 + cgpi_m_jp.zip）, "
                f"{df['date'].min().date()} – {df['date'].max().date()}\n")
        f.write("系列コード:\n")
        for g, s in SERIES.items():
            f.write(f"  {s['name']}: 円ベース={s['yen']} / 契約通貨ベース={s['contract']}\n")
        f.write("\n== 暦年分解（年平均指数の対数変化率, log-pt%） ==\n")
        f.write(cy.to_string(index=False))
        f.write("\n\n== 累積分解（2020-12 起点, log-pt%） ==\n")
        f.write(cum_df.to_string(index=False))
        f.write("\n\n" + sanity1 + "\n\n" + sanity2 + "\n")

    print(sanity1)
    print(sanity2)
    print("\n暦年分解:")
    print(cy.to_string(index=False))
    print("\n累積分解:")
    print(cum_df.to_string(index=False))
    print(f"\nOutputs → {OUT_DIR}")


if __name__ == "__main__":
    main()
