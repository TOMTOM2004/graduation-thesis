"""
米（コメ）価格高騰の Q1-Q5 実効インフレ格差への寄与控除（Task D）.

背景
----
2024-25 年の米価急騰（令和の米騒動: 2023年不作＋流通問題）は国内要因ショック
であり、輸入とはほぼ無関係（米の自給率 ~100%・輸入は制限的）。本論文の
Q1-Q5 実効インフレ格差（暦年・2019年固定シェア: 2022 +2.01 / 2023 +2.06 /
2024 +2.45 / 2025 +3.36 pp）を「輸入コストプッシュ由来の逆進性」として提示
するため、米の寄与を恒等式会計で定量化し控除する（識別なし・純会計）。

手法（counterfactual 置換法）
----------------------------
確立済み格差の定義（cost_push_id.compute_cpi_changes + quintile_impact、
oil_lp_prep.annual_gap_crosscheck で複製済み）:

    gap_t = Σ_c (s_Q1,c − s_Q5,c) × (I_c,t − mean(I_c, 2015..2019))

  I_c,t = 10大費目 CPI の暦年平均指数（2020=100）、シェアは 2019年家計調査
  （二人以上の世帯、cat02=3）固定・非再正規化。

米はこのうち「食料」費目の内部に CPI ウエイトで入っているため、控除は
食料費目を「食料（米類を除く）」に置換する counterfactual で行う:

  1. CPI_食料除く米,t = (W_食料·CPI_食料,t − W_米類·CPI_米類,t) / (W_食料 − W_米類)
     W は 2020年基準 CPI ウエイト（全国・一万分比）: 食料=2626, 米類=62。
     出所: 総務省統計局「消費者物価指数のしくみと見方 ―2020年基準消費者
     物価指数― 付1 ウエイト一覧（全国）」
     https://www.stat.go.jp/data/cpi/2020/mikata/pdf/fu1.pdf
     （2020年基準ラスパイレスの下では食料指数は下位指数のウエイト加重
     平均に一致するため、この再構成は恒等的に正確）
  2. 五分位シェア: s_q(食料除く米) = s_q(食料) − s_q(米)。
     s_q(米) = 家計調査 品目別支出金額（e-Stat 0003348240、年収五分位・
     二人以上の世帯 cat02=03・2019年・品目分類 010110001「米」）÷ 同表の
     消費支出（001100000）。s_q(食料) は確立済みシェア（10大費目ファイル）
     をそのまま使い、他費目・ベースライン定義も一切変更しない。
  3. 食料除く米系列のベースラインはその系列自身の 2015-19 暦年平均。
  4. 米寄与 = gap_established − gap_net_of_rice（構成上恒等）。
     解析的分解: 寄与 = (s1f−s5f)·(W米/W食)·Δ米_t  [直接項]
                + [(s1r−s5r) − (W米/W食)(s1f−s5f)]·Δ食料除く米_t  [再加重項]

注意（caveat）
--------------
- 米は国産・非輸入財のため、この控除は輸入帰属クレームを「純化」する
  （控除後の格差 = 輸入コストプッシュ帰属の下限側でなく、米という国内
  ショック混入を除いた清浄値）。ミニマムアクセス米等の少量輸入は無視。
- 純会計であり行動反応・代替は考慮しない（確立済み格差と同じ前提）。

Run: uv run python src/analysis/rice_deduction.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = str(Path(__file__).resolve().parents[2])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.analysis.cost_push_id import HH_TO_CPI_CODE
from src.analysis.quintile_impact import load_expenditure_shares

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed" / "rice-deduction"

CPI_CACHE = DATA_RAW / "cpi" / "cpi_category_2015_2025.csv"
HH_ITEM_CACHE = DATA_RAW / "household-survey" / "household_quintile_items_rice_2019.csv"

# e-Stat 家計調査 品目別支出金額（年収五分位・二人以上の世帯・年次）DEC-016
HH_ITEM_TABLE = "0003348240"
# cat01（品目分類 2020年改定）コード
ITEM_CODES = {
    "001100000": "消費支出",
    "010000000": "食料",
    "010100000": "穀類",
    "010110001": "米",
}

# CPI cache cat01_code（2020年基準リンク表・全国・指数）
CPI_CODE_FOOD = 2   # 0002 食料
CPI_CODE_RICE = 4   # 0004 米類（うるち米＋もち米）

# 2020年基準 CPI ウエイト（全国・一万分比）。出所: 総務省統計局
# 「消費者物価指数のしくみと見方（2020年基準）付1 ウエイト一覧（全国）」
# https://www.stat.go.jp/data/cpi/2020/mikata/pdf/fu1.pdf
W_FOOD = 2626.0
W_RICE = 62.0

ESTABLISHED_GAPS = {2022: 2.01, 2023: 2.06, 2024: 2.45, 2025: 3.36}
YEARS = [2022, 2023, 2024, 2025]


# --------------------------------------------------------------------------- #
# CPI: 食料・米類の月次→暦年平均                                              #
# --------------------------------------------------------------------------- #
def load_cpi_monthly(code: int) -> pd.Series:
    """CPI cache から指定 cat01 の暦年月次系列（2020=100）を返す。
    time_code=YYYY00MMMM（[6:8]==[8:10]）のみ＝年計・年度計を除外。"""
    df = pd.read_csv(CPI_CACHE)
    df = df[pd.to_numeric(df["tab_code"], errors="coerce") == 1]
    df = df[pd.to_numeric(df["cat01_code"], errors="coerce") == code]
    tc = df["time_code"].astype(str)
    mm = [f"{i:02d}" for i in range(1, 13)]
    df = df[tc.str[8:10].isin(mm) & (tc.str[6:8] == tc.str[8:10])].copy()
    tc = df["time_code"].astype(str)
    df["date"] = pd.to_datetime(tc.str[:4] + "-" + tc.str[8:10] + "-01")
    s = df.set_index("date")["value"].astype(float).sort_index()
    if s.empty:
        raise RuntimeError(f"CPI cat01={code} not found in {CPI_CACHE}")
    return s


# --------------------------------------------------------------------------- #
# 家計調査 品目別（米）五分位シェア                                           #
# --------------------------------------------------------------------------- #
def fetch_hh_items_2019() -> pd.DataFrame:
    """fetch-if-missing: 0003348240 の 2019年・二人以上の世帯(cat02=03)・
    全国、消費支出/食料/穀類/米 × 五分位（平均含む）。"""
    if HH_ITEM_CACHE.exists():
        return pd.read_csv(HH_ITEM_CACHE, dtype={"cat01_code": str, "cat03_code": str})
    from src.data.estat_api import get_stats_data

    print(f"Fetching {HH_ITEM_TABLE} (品目別×五分位, 2019)...")
    df = get_stats_data(
        HH_ITEM_TABLE,
        cdCat01=",".join(ITEM_CODES.keys()),
        cdCat02="03",  # 二人以上の世帯（2000年～）
        cdArea="00000",
        cdTime="2019000000",
    )
    if df.empty:
        raise RuntimeError("e-Stat returned no data for 0003348240")
    HH_ITEM_CACHE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(HH_ITEM_CACHE, index=False)
    print(f"Saved {HH_ITEM_CACHE} ({len(df)} rows)")
    return df


def rice_shares_2019(lines: list[str]) -> tuple[pd.Series, pd.Series]:
    """五分位別 s_q(米), s_q(食料)（品目分類ベース、消費支出比）を返す。
    index=quintile 1..5（0=平均も保持して返却は 0..5）。"""
    df = fetch_hh_items_2019()
    df["cat01_code"] = df["cat01_code"].astype(str).str.zfill(9)
    df["cat03_code"] = pd.to_numeric(df["cat03_code"], errors="coerce").astype(int)

    def pick(code: str) -> pd.Series:
        s = (
            df[df["cat01_code"] == code]
            .set_index("cat03_code")["value"].astype(float).sort_index()
        )
        if s.empty:
            raise RuntimeError(f"item {code} ({ITEM_CODES[code]}) missing in fetch")
        return s

    total = pick("001100000")
    rice = pick("010110001")
    food = pick("010000000")
    grain = pick("010100000")

    s_rice = rice / total
    s_food_item = food / total
    s_grain = grain / total

    lines.append("\n[米シェア 2019・二人以上の世帯・品目分類 (e-Stat 0003348240・年間支出額)]")
    lines.append(
        f"{'分位':>4} {'消費支出(円/年)':>14} {'米(円/年)':>10} "
        f"{'s(米)%':>8} {'s(穀類)%':>9} {'s(食料)%':>9}"
    )
    for q in sorted(total.index):
        label = "平均" if q == 0 else f"Q{q}"
        lines.append(
            f"{label:>4} {total[q]:>14,.0f} {rice[q]:>10,.0f} "
            f"{s_rice[q]*100:>8.3f} {s_grain[q]*100:>9.3f} {s_food_item[q]*100:>9.3f}"
        )
    lines.append(
        f"[米シェア] Q1−Q5 差: s(米) {100*(s_rice[1]-s_rice[5]):+.3f}pp, "
        f"s(穀類) {100*(s_grain[1]-s_grain[5]):+.3f}pp"
    )
    return s_rice, s_food_item


# --------------------------------------------------------------------------- #
# 確立済み格差の複製 + counterfactual                                          #
# --------------------------------------------------------------------------- #
def annual_avg(s: pd.Series) -> pd.Series:
    return s.groupby(s.index.year).mean()


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("=== 米（コメ）価格高騰の Q1-Q5 格差寄与控除（恒等式会計） ===")

    # --- 1. 米類 CPI の推移 -------------------------------------------------
    cpi_rice_m = load_cpi_monthly(CPI_CODE_RICE)
    cpi_food_m = load_cpi_monthly(CPI_CODE_FOOD)
    rice_ann = annual_avg(cpi_rice_m)
    food_ann = annual_avg(cpi_food_m)

    lines.append("\n[米類 CPI（2020=100・全国・暦年平均）]")
    lines.append(f"{'年':>6} {'指数':>8} {'前年比%':>8} {'対2015-19基準':>12}")
    rice_base = rice_ann.loc[2015:2019].mean()
    rice_yoy = (rice_ann / rice_ann.shift(1) - 1) * 100
    for yr in range(2020, 2026):
        lines.append(
            f"{yr:>6} {rice_ann[yr]:>8.1f} {rice_yoy[yr]:>+8.1f} "
            f"{rice_ann[yr]-rice_base:>+12.1f}"
        )
    peak_m = cpi_rice_m.pct_change(12).idxmax()
    peak_v = cpi_rice_m.pct_change(12).max() * 100
    lines.append(
        f"[米類 CPI] 月次前年同月比ピーク: {peak_m:%Y-%m} {peak_v:+.1f}%"
        f"（令和の米騒動: 2023年不作＋流通要因＝国内ショック）"
    )

    # --- 2. 五分位 米シェア（2019固定） ------------------------------------
    s_rice, s_food_item = rice_shares_2019(lines)

    # 確立済み 10大費目シェア（load_expenditure_shares: 非再正規化・cat02=3）
    shares = load_expenditure_shares(year=2019, household_type=3)
    codes = list(HH_TO_CPI_CODE.keys())
    dshare = shares.loc[1, codes] - shares.loc[5, codes]

    # クロスチェック: 品目分類の食料シェア vs 確立済み（用途分類系）食料シェア
    lines.append("\n[整合性チェック] 食料シェア: 品目分類(0003348240) vs 確立済み10大費目ファイル")
    for q in range(1, 6):
        a, b = s_food_item[q], shares.loc[q, 60]
        lines.append(f"  Q{q}: {a*100:.2f}% vs {b*100:.2f}% (差 {100*(a-b):+.2f}pp)")

    # --- 3. 確立済み格差の複製 ----------------------------------------------
    # 暦年平均 CPI（10大費目、cache から）
    cpi_ann = {}
    name_to_code = {  # cache cat01_code for 10大費目
        "食料": 2, "住居": 45, "光熱・水道": 54, "家具・家事用品": 60,
        "被服及び履物": 82, "保健医療": 107, "交通・通信": 111,
        "教育": 118, "教養娯楽": 122, "諸雑費": 145,
    }
    for hh_code, cpi_name in HH_TO_CPI_CODE.items():
        cpi_ann[hh_code] = annual_avg(load_cpi_monthly(name_to_code[cpi_name]))
    cpi_ann = pd.DataFrame(cpi_ann)
    baseline = cpi_ann.loc[2015:2019].mean()
    gap_est = ((cpi_ann - baseline) * dshare).sum(axis=1)

    lines.append("\n[確立済み格差の複製チェック]")
    max_diff = 0.0
    for yr, want in ESTABLISHED_GAPS.items():
        got = float(gap_est.loc[yr])
        max_diff = max(max_diff, abs(got - want))
        lines.append(f"  {yr}: computed {got:.3f}pp vs established {want:.2f}pp (差 {got-want:+.3f})")
    if max_diff >= 0.1:
        raise RuntimeError(f"確立済み格差の複製失敗 (max diff {max_diff:.3f}pp >= 0.1)")
    lines.append(f"  PASS (max |diff| = {max_diff:.4f}pp < 0.1pp)")

    # --- 4. counterfactual: 食料 → 食料除く米類 -----------------------------
    # ラスパイレス恒等式による正確な再構成（2020年基準ウエイト）
    cpi_fxr_m = (W_FOOD * cpi_food_m - W_RICE * cpi_rice_m) / (W_FOOD - W_RICE)
    fxr_ann = annual_avg(cpi_fxr_m)
    fxr_base = fxr_ann.loc[2015:2019].mean()

    d_s_rice = float(s_rice[1] - s_rice[5])
    d_s_food = float(dshare[60])
    d_s_fxr = d_s_food - d_s_rice

    # 食料以外の費目の寄与（両シナリオ共通）
    other_codes = [c for c in codes if c != 60]
    gap_other = ((cpi_ann[other_codes] - baseline[other_codes]) * dshare[other_codes]).sum(axis=1)

    d_food = cpi_ann[60] - baseline[60]          # Δ食料（対2015-19基準）
    d_fxr = fxr_ann - fxr_base                   # Δ食料除く米類
    d_rice = rice_ann - rice_base                # Δ米類

    gap_net = gap_other + d_s_fxr * d_fxr
    contribution = gap_est - gap_net

    # 解析的分解（検算用）: 直接項 + 再加重項
    wr = W_RICE / W_FOOD
    contrib_direct = d_s_food * wr * d_rice
    contrib_reweight = (d_s_rice - wr * d_s_food) * d_fxr
    # 参考: 素朴近似 (s1r−s5r)×(Δ米 − Δ食料)
    contrib_naive = d_s_rice * (d_rice - d_food)

    lines.append("\n[手法] counterfactual 置換法: 食料費目を「食料除く米類」CPI")
    lines.append(f"  CPI_食料除く米 = ({W_FOOD:.0f}·CPI_食料 − {W_RICE:.0f}·CPI_米類) / {W_FOOD-W_RICE:.0f}")
    lines.append("  （2020年基準ウエイト 食料=2626, 米類=62, 全国・一万分比。総務省統計局")
    lines.append("   「しくみと見方 付1 ウエイト一覧」https://www.stat.go.jp/data/cpi/2020/mikata/pdf/fu1.pdf）")
    lines.append(f"  シェア置換: s_q(食料) − s_q(米)。Q1−Q5 差: 食料 {d_s_food*100:+.3f}pp, "
                 f"米 {d_s_rice*100:+.3f}pp, 食料除く米 {d_s_fxr*100:+.3f}pp")
    lines.append("  米寄与 = gap_established − gap_net（恒等）。米価が 2015-19 基準に")
    lines.append("  固定された counterfactual と同値（Δ米=0 なら寄与 0）。")

    lines.append("\n[結果] Q1-Q5 実効インフレ格差の米寄与分解（pp・対2015-19基準・暦年）")
    lines.append(
        f"{'年':>6} {'確立済み格差':>12} {'米寄与':>8} {'控除後格差':>10} "
        f"{'(直接項':>9} {'再加重項':>9} {'素朴近似)':>10}"
    )
    rows = []
    for yr in YEARS:
        lines.append(
            f"{yr:>6} {gap_est[yr]:>12.3f} {contribution[yr]:>8.3f} {gap_net[yr]:>10.3f} "
            f"{contrib_direct[yr]:>9.3f} {contrib_reweight[yr]:>9.3f} {contrib_naive[yr]:>10.3f}"
        )
        rows.append({
            "year": yr,
            "gap_established": round(float(gap_est[yr]), 4),
            "rice_contribution_pp": round(float(contribution[yr]), 4),
            "gap_net_of_rice": round(float(gap_net[yr]), 4),
            "contrib_direct_pp": round(float(contrib_direct[yr]), 4),
            "contrib_reweight_pp": round(float(contrib_reweight[yr]), 4),
            "rice_cpi_yoy_pct": round(float(rice_yoy[yr]), 2),
            "rice_cpi_vs_baseline": round(float(d_rice[yr]), 2),
        })

    # --- 5. sanity checks ----------------------------------------------------
    lines.append("\n[sanity]")
    # (i) 恒等性: net = est − contribution（構成上自明だが分解の実装検算）
    recon = contrib_direct + contrib_reweight
    max_dec = float((contribution - recon).loc[YEARS].abs().max())
    lines.append(f"  分解恒等性 |寄与 − (直接+再加重)| max = {max_dec:.2e} "
                 f"({'PASS' if max_dec < 1e-9 else 'FAIL'})")
    if max_dec >= 1e-9:
        raise RuntimeError("解析的分解が counterfactual 差分と一致しない")
    # (ii) 2022/2023: 米価は横ばい〜下落 → 米価格の直接効果（直接項）はほぼゼロのはず。
    #      総寄与には再加重項（家計の米シェア(Q1−Q5差0.52pp) > CPIウエイト比按分
    #      wr·食料シェア差(0.20pp) という構造効果 × 食料全般インフレ）が乗るため、
    #      食料インフレが大きい2023年は総寄与が +0.06pp 程度出るが、これは米価
    #      ショックではなくシェア構造の会計効果（調査済み・想定内）。
    for yr in (2022, 2023):
        cd = float(contrib_direct[yr])
        ct = float(contribution[yr])
        ok = abs(cd) < 0.05
        lines.append(
            f"  {yr} 米価直接項 = {cd:+.4f}pp "
            f"({'PASS: ほぼゼロ（米価横ばい/下落期）' if ok else 'FAIL: 要調査'})"
            f" ／ 総寄与 {ct:+.4f}pp（差は再加重項＝シェア構造効果）"
        )
        if not ok:
            raise RuntimeError(f"{yr} の米価直接項が想定外に大きい: {cd:+.4f}pp")

    # --- 6. outputs ----------------------------------------------------------
    out_csv = OUT_DIR / "rice_gap_contribution.csv"
    pd.DataFrame(rows).to_csv(out_csv, index=False)
    lines.append(f"\n[saved] {out_csv}")

    lines.append(
        "\n[caveats]\n"
        "  - 米は国産・輸入制限下でほぼ100%自給＝2024-25年の米価急騰は国内ショック。\n"
        "    本控除は「輸入コストプッシュ由来の逆進性」クレームを純化する（控除後も\n"
        "    格差は正で拡大傾向＝輸入帰属の主張は米を除いても成立するかを直接確認）。\n"
        "  - ミニマムアクセス米等の少量輸入は無視（米類 CPI 全体を国内ショック扱い）。\n"
        "  - 純会計（恒等式）・識別なし・行動反応なし。確立済み格差と同一の前提\n"
        "    （2019年固定シェア・非再正規化・対2015-19暦年基準・二人以上の世帯）。\n"
        "  - CPI ウエイトは 2020年基準の公表値（食料2626・米類62）を使用。リンク係数\n"
        "    処理済み接続指数に厳密恒等でない可能性は残るが、米類ウエイトが小さく\n"
        "    (2.4% of 食料) 誤差は二次的。"
    )

    report = "\n".join(lines)
    print(report)
    (OUT_DIR / "rice_deduction_summary.txt").write_text(report + "\n", encoding="utf-8")

    # --- 7. figure -----------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import japanize_matplotlib  # noqa: F401

    fig, ax = plt.subplots(figsize=(8, 5))
    xs = np.arange(len(YEARS))
    net_vals = [float(gap_net[y]) for y in YEARS]
    rice_vals = [float(contribution[y]) for y in YEARS]
    ax.bar(xs, net_vals, width=0.55, color="#2980b9", label="米類を除く格差（輸入コストプッシュ側）")
    ax.bar(xs, rice_vals, width=0.55, bottom=net_vals, color="#e67e22",
           label="米類の寄与（国内ショック）")
    for i, y in enumerate(YEARS):
        tot = net_vals[i] + rice_vals[i]
        ax.annotate(f"{tot:.2f}", (i, tot), xytext=(0, 4),
                    textcoords="offset points", ha="center", fontsize=9)
        if abs(rice_vals[i]) > 0.03:
            ax.annotate(f"米 {rice_vals[i]:+.2f}", (i, net_vals[i] + rice_vals[i] / 2),
                        ha="center", va="center", fontsize=8, color="white")
    ax.set_xticks(xs)
    ax.set_xticklabels([str(y) for y in YEARS])
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set_ylabel("Q1−Q5 実効インフレ格差（pp・対2015-19基準）")
    ax.set_title("Q1-Q5 格差に占める米（国内ショック）の寄与\n（暦年・2019年固定シェア・恒等式会計）")
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.25)
    fig.text(0.5, -0.02,
             "注: 米類CPI（2020年基準ウエイト62/食料2626）を食料費目から控除した counterfactual。"
             "米は国産（自給率~100%）のため控除後が輸入帰属クレームの清浄値。",
             ha="center", fontsize=7.5, color="gray")
    plt.tight_layout()
    fig.savefig(OUT_DIR / "fig_rice_deduction.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nSaved figure: {OUT_DIR / 'fig_rice_deduction.png'}")


if __name__ == "__main__":
    main()
