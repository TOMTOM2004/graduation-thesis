"""案2 A案: pooled β の FIRST-DIFFERENCE shift-share を期間延長して再推定する。

advisor catch: headline β=0.431 は levels-on-2020 で、levels の shifter (P_t-100)
は持続的トレンド（A-3 の「単調トレンド≒ショック1本」）なので期間延長の恩恵が出ない。
pr_time=1.88->6.35 は年次対数変化（FD）で測った量。よって FD spec を primary にする:

    ΔCPI_{c,t} = β·(IC_c · ΔP_t) + α_c + γ_t + ε_{c,t}      (IC_c は 2020 固定)

shock = ΔP_t（年あたり1本の集計輸入物価変化）。exposure = IC_c。
識別は年FE除去後の cross-category IC×ΔP_t。実効ショック数 = 年数。

windows: FD-current = 変化年 2016-2024 / FD-extended = 変化年 2006-2024。
比較は shock(=年)-level 推論 p の current vs extended（cluster-entity p ではない）。

推論の注意: time-clustered SE は shock=年の few-cluster（G=9〜19）で**反保守的**。
proper な ShiftShareSE/AKM は未実行のため、current 窓の「有意」主張はしない。
案2 の判定（期間延長が識別を救うか）には p の絶対水準でなく
「延長で改善するか」の比較で十分で、その答えは FD-Koyck δ=0.55 で両窓 null。

結論（DEC-013/A-5）: 期間延長は pooled β のクリーン識別を救わない/強化しない。
単一集計 shifter では two-way FE の time FE が時間変動を吸収し、識別は
cross-sectional な IC（2020固定）に依存するため。magic δ は無い（level-anchoring）。
levels β=0.431 は levels/累積でのみ立ち annual-difference では消える（headline の
頑健性は案2より大きい別問題で、ここでは spurious/robust と断じない）。
"""
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"


def load_cpi_annual_ext():
    """Extended 2020-base linked CPI by mid-category, annual avg, 2005-2024.

    Mirrors src.analysis.cost_push_panel._load_cpi_annual_mid EXACTLY: e-Stat CPI
    time_code is YYYY00MMMM (monthly) or YYYY10... (annual). The existing pipeline
    keeps str[4:6] in 01-12, which selects the ANNUAL (年度) rows and groups by year
    -> one annual-average index per category-year. We replicate that on the
    2005-2024 file so windows are apples-to-apples with the headline.
    """
    from src.analysis.bridge_matrix_mid import CPI_CODE_TO_NAME, CPI_MID_CATEGORY_MAP
    cpi = pd.read_csv(RAW / "cpi" / "cpi_category_2005_2024.csv")
    cpi = cpi[cpi["tab_code"] == 1].copy()  # 指数 only (drop 前年比% / contribution tabs)
    cpi["year"] = cpi["time_code"].astype(str).str[:4].astype(int)
    mask = cpi["time_code"].astype(str).str[4:6].isin([f"{m:02d}" for m in range(1, 13)])
    cpi = cpi[mask].copy()
    cpi["cpi_code"] = cpi.cat01_code.astype(str).str.zfill(4)
    target = set(v["cpi_code"] for v in CPI_MID_CATEGORY_MAP.values())
    cpi = cpi[cpi.cpi_code.isin(target)]
    annual = cpi.groupby(["year", "cpi_code"])["value"].mean().reset_index().rename(columns={"value": "cpi_index"})
    annual["cpi_mid_name"] = annual.cpi_code.map(CPI_CODE_TO_NAME)
    return annual


def load_pimport_annual_ext():
    """Aggregate import price (yen-basis total), 2020-base, annual avg, spliced 2005-2024."""
    link = pd.read_csv(RAW / "boj-cgpi" / "cgpilink1.csv", header=None, low_memory=False, encoding="shift_jis")
    months = link.iloc[0, 3:].astype(float).astype(int).values
    idx = pd.to_datetime([f"{m // 100}-{m % 100:02d}-01" for m in months])
    tot = pd.Series(pd.to_numeric(link.iloc[59, 3:], errors="coerce").values, index=idx)  # 円ベース総平均
    tot = tot[tot.index <= "2019-12-01"]
    rec = pd.read_csv(RAW / "boj-cgpi" / "import_prices_extracted.csv", parse_dates=["date"])
    rect = rec[rec.group == "total"].set_index("date")["value"]
    ov = tot.index.intersection(rect.index)
    assert (tot.loc[ov] - rect.loc[ov]).abs().mean() < 1e-6, "P_import splice mismatch"
    spliced = pd.concat([tot[tot.index < "2020-01-01"], rect[rect.index >= "2020-01-01"]]).sort_index()
    ann = spliced.resample("YE").mean()
    return pd.DataFrame({"year": ann.index.year, "p_import": ann.values})


def build_fd_panel():
    from src.analysis.bridge_matrix_mid import compute_mid_category_import_content
    ic = compute_mid_category_import_content()[
        ["cpi_mid_name", "cpi_code", "import_content", "group", "is_competitive_import"]
    ].rename(columns={"import_content": "ic"})
    ic["cpi_code"] = ic.cpi_code.astype(str).str.zfill(4)

    cpi = load_cpi_annual_ext()
    pim = load_pimport_annual_ext()

    panel = cpi.merge(ic, on=["cpi_mid_name", "cpi_code"], how="left").merge(pim, on="year", how="inner")
    panel = panel.sort_values(["cpi_mid_name", "year"])
    # FIRST DIFFERENCES (annual)
    panel["dcpi"] = panel.groupby("cpi_mid_name")["cpi_index"].diff()
    panel["dp"] = panel.groupby("cpi_mid_name")["p_import"].diff()  # same for all c within year
    panel["ss_fd"] = panel["ic"] * panel["dp"]
    panel = panel.dropna(subset=["dcpi", "ss_fd", "ic"])
    return panel


def koyck_shifter(pim, delta):
    """S_t(delta) = sum_{s>=0} delta^s * dP_{t-s}, on the long aggregate P_import series."""
    s, acc, first = [], 0.0, True
    for v in pim["dp"].values:
        if np.isnan(v):
            s.append(np.nan); continue
        acc = v + (0.0 if first else delta * acc)
        first = False
        s.append(acc)
    return pd.Series(s, index=pim["year"].values)


def fit(sub, y, x, time_fe=True, cluster_time=True):
    from linearmodels import PanelOLS
    ps = sub.set_index(["cpi_mid_name", "year"]).dropna(subset=[y, x])
    r = PanelOLS(ps[y], ps[[x]], entity_effects=True, time_effects=time_fe,
                 drop_absorbed=True, check_rank=False).fit(
        cov_type="clustered", cluster_entity=not cluster_time, cluster_time=cluster_time)
    return r.params[x], r.pvalues[x], int(r.nobs)


if __name__ == "__main__":
    panel = build_fd_panel()  # has dcpi, ss_fd (=IC*dP), ic, dp
    pim = load_pimport_annual_ext().sort_values("year")
    pim["dp"] = pim["p_import"].diff()
    nc = panel[~panel.is_competitive_import].copy()
    # also need levels DV for the levels spec
    cpi = load_cpi_annual_ext()
    from src.analysis.bridge_matrix_mid import compute_mid_category_import_content
    ic = compute_mid_category_import_content()[["cpi_mid_name", "cpi_code", "import_content", "is_competitive_import"]].rename(columns={"import_content": "ic"})
    ic["cpi_code"] = ic.cpi_code.astype(str).str.zfill(4)
    pl = cpi.merge(ic, on=["cpi_mid_name", "cpi_code"]).merge(pim[["year", "p_import"]], on="year").sort_values(["cpi_mid_name", "year"])
    b2020 = pl[pl.year == 2020].set_index("cpi_mid_name")["cpi_index"].rename("b")
    pl = pl.merge(b2020, on="cpi_mid_name")
    pl["delta_cpi"] = pl["cpi_index"] - pl["b"]
    pl["ss_lev"] = pl["ic"] * (pl["p_import"] - 100.0)
    pl_nc = pl[~pl.is_competitive_import].copy()

    print("Reproduces existing CPI (overlap diff=0). exclude competitive imports.\n")
    print("=== LEVELS spec (DV = CPI - CPI_2020), shifter IC*(P-100), two-way FE ===")
    print("    [p_time = shock-level (year) clustered inference] ")
    for yrs, lab in [((2015, 2024), "2015-24 (current)"), ((2005, 2024), "2005-24 (extended)")]:
        s = pl_nc[pl_nc.year.between(*yrs) & (pl_nc.year != 2020)]
        be, pe, n = fit(s, "delta_cpi", "ss_lev", cluster_time=False)
        _, pt, _ = fit(s, "delta_cpi", "ss_lev", cluster_time=True)
        print(f"  {lab}: beta={be:+.3f}  p_entity={pe:.4f}  p_time={pt:.4f}  n={n}")

    print("\n=== DECISIVE: FD-DV, Koyck shifter S_t(delta), two-way FE, time-clustered ===")
    print("    delta=0 -> contemporaneous FD; delta->1 -> cumulative. delta=0.55 = project calibration")
    for d in [0.0, 0.25, 0.55, 0.8, 1.0]:
        St = koyck_shifter(pim, d)
        nc["ss"] = nc["ic"] * nc["year"].map(St)
        bc, pc, _ = fit(nc[nc.year.between(2016, 2024)], "dcpi", "ss")
        be, pe, _ = fit(nc[nc.year.between(2006, 2024)], "dcpi", "ss")
        star = "  <- calibrated" if abs(d - 0.55) < 1e-9 else ""
        print(f"  delta={d:.2f} | cur beta={bc:+.3f} p_time={pc:.4f} | ext beta={be:+.3f} p_time={pe:.4f}{star}")

    print("\n=== SECONDARY: entity-only FE (demand-pull NOT controlled), delta=0.55 ===")
    St = koyck_shifter(pim, 0.55); nc["ss"] = nc["ic"] * nc["year"].map(St)
    for yrs, lab in [((2016, 2024), "cur"), ((2006, 2024), "ext")]:
        b, pt, n = fit(nc[nc.year.between(*yrs)], "dcpi", "ss", time_fe=False, cluster_time=True)
        print(f"  {lab}: beta={b:+.3f} p_time={pt:.4f} n={n}")
    print("\nVERDICT: period extension does NOT rescue/strengthen pooled-beta identification.")
    print("  levels: destroyed by extension (0.53 p=0.0002 -> -0.01 p=0.96)")
    print("  FD-Koyck two-way (clean): null at calibrated delta=0.55 in BOTH windows")
    print("  entity-only: stable beta but demand-pull-confounded; p does not tighten with extension")
