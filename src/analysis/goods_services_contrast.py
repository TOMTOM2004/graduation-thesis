"""
財/サービス分解による識別限界の実証（goods-services contrast）。

設計書: docs/design/2026-07-06-goods-services-contrast.md

年次相関コントラスト（全体では全ショック期年が正・全プラセボ期年が負）が
goods-vs-services 構成差でどこまで説明されるかを、財/サービスバケット別の
年次相関・pooled 回帰 β で定量化する（DEC-022）。
識別の救済（β の有意性回復）は目的ではない。
"""

import matplotlib
matplotlib.use("Agg")   # 必須: pyplot import より前。plt.show() は呼ばない（savefig + close のみ）

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
PRICE_DIR = DATA_PROCESSED / "price-indices"

# §3 の分類テーブル41件（キー=cpi_mid_name、値="goods"|"services"|"energy_util"|"mixed"）
# 主基準: 当該中分類の支出の過半を占める構成が財かサービスか（研究上の事前定義・DEC-010 と同格）
GOODS_SERVICES_MAP: dict[str, str] = {
    "穀類": "goods",                # 食料品（財）
    "魚介類": "goods",               # 同上
    "肉類": "goods",                 # 同上
    "乳卵類": "goods",               # 同上
    "野菜・海藻": "goods",           # 同上
    "果物": "goods",                 # 同上
    "油脂・調味料": "goods",         # 同上
    "菓子類": "goods",               # 同上
    "調理食品": "goods",             # 中食（財として販売）
    "飲料": "goods",                 # 財
    "酒類": "goods",                 # 財
    "外食": "services",              # 飲食サービス
    "家賃": "services",              # 住居サービス（帰属家賃は分析対象外・実支出家賃）
    "設備修繕・維持": "mixed",       # 工事サービス＋資材の混在
    "電気代": "energy_util",         # 財（公共料金）・2023-24 激変緩和補助対象
    "ガス代": "energy_util",         # 同上
    "他の光熱": "energy_util",       # 灯油等（財・補助対象外）
    "上下水道料": "services",        # 公共サービス料金（輸入含有低・価格は行政決定）
    "家庭用耐久財": "goods",         # 財
    "室内装備品": "goods",           # 財
    "家事用消耗品": "goods",         # 財
    "家事サービス": "services",      # サービス
    "衣料": "goods",                 # 財（※回帰では競争的輸入財として除外済・本分析にも入らない）
    "履物類": "goods",               # 同上
    "被服関連サービス": "services",  # クリーニング等
    "保健医療用品・器具": "goods",   # 財
    "医薬品・健康保持用摂取品": "goods",  # 財
    "保健医療サービス": "services",  # 診療等（公定価格）
    "交通": "services",              # 運賃（サービス）
    "自動車等関係費": "mixed",       # ガソリン（財・高IC）＋整備/保険（サービス）の混在
    "通信": "services",              # 通信サービス（政策的価格操作あり・既存 (ii) 仕様で除外対象だが本分析では services に残す）
    "授業料等": "services",          # 教育サービス
    "教科書・学習参考教材": "goods",  # 財
    "補習教育": "services",          # 教育サービス
    "教養娯楽用耐久財": "goods",     # 財
    "教養娯楽用品": "goods",         # 財
    "書籍・他の印刷物": "goods",     # 財
    "教養娯楽サービス": "services",  # パック旅行を除くサービス
    "パック旅行費": "services",      # 旅行サービス
    "理美容サービス": "services",    # サービス
    "放送受信料": "services",        # 公共サービス料金
}

SHOCK_YEARS = (2021, 2024)      # run_panel_regression の years 引数形式（両端含むタプル）
PLACEBO_YEARS = (2015, 2019)
MIN_N_CORR = 8

# §0.1 の golden（year: 期待相関）。検証専用・分析には使わない
GOLDEN_S0_CORR = {
    2015: -0.167, 2016: -0.102, 2017: -0.174, 2018: -0.253, 2019: -0.232,
    2021: 0.064, 2022: 0.136, 2023: 0.389, 2024: 0.255,
}


def load_panel() -> pd.DataFrame:
    """panel_cost_push.csv を読み、bucket 列を付与して返す。

    - 存在しなければ RuntimeError（先に python -m src.analysis.cost_push_panel を実行するよう案内）
    - 衣料・履物（is_competitive_import==True）を除外
    - 双方向の分類検証・バケットサイズ検証を assert（不成立なら fail、silent drop 禁止）
    """
    cache_path = PRICE_DIR / "panel_cost_push.csv"
    if not cache_path.exists():
        raise RuntimeError(
            f"{cache_path} が存在しません。先に `python -m src.analysis.cost_push_panel` を実行してください。"
        )

    df = pd.read_csv(cache_path)

    panel_names_all = set(df["cpi_mid_name"].unique())
    map_names = set(GOODS_SERVICES_MAP.keys())

    missing_in_map = panel_names_all - map_names
    assert not missing_in_map, f"GOODS_SERVICES_MAP に無い cpi_mid_name: {missing_in_map}"
    missing_in_panel = map_names - panel_names_all
    assert not missing_in_panel, f"panel に存在しない GOODS_SERVICES_MAP のキー: {missing_in_panel}"

    df = df[~df["is_competitive_import"]].copy()
    df["bucket"] = df["cpi_mid_name"].map(GOODS_SERVICES_MAP)

    bucket_counts = df.groupby("bucket")["cpi_mid_name"].nunique().to_dict()
    expected = {"goods": 20, "services": 14, "energy_util": 3, "mixed": 2}
    assert bucket_counts == expected, f"バケットサイズ不一致: {bucket_counts} != {expected}"

    return df


def yearly_corr(df: pd.DataFrame) -> dict[int, tuple[float, int]]:
    """§0.1 の4ステップ（年 subset → dropna(subset=["ic","delta_cpi"]) → Series.corr）。

    戻り値 {year: (corr or NaN, n)}。n < MIN_N_CORR は corr=NaN。
    """
    result = {}
    for year in sorted(df["year"].unique()):
        sub = df[df["year"] == year].dropna(subset=["ic", "delta_cpi"])
        n = len(sub)
        if n < MIN_N_CORR:
            result[year] = (float("nan"), n)
        else:
            result[year] = (float(sub["ic"].corr(sub["delta_cpi"])), n)
    return result


def run_bucket_regression(df: pd.DataFrame, years: tuple) -> dict:
    """バケット部分集合 df に既存 run_panel_regression を import 一択で適用する。"""
    from src.analysis.cost_push_panel import run_panel_regression

    res = run_panel_regression(df, se_type="cluster", years=years)
    return {
        "beta": res["beta"],
        "pval": res["pval"],
        "n_categories": res["n_categories"],
    }


def _bucket_frames(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """§1.3 の4仕様それぞれのバケット部分集合を返す。"""
    goods = df[df["bucket"] == "goods"]
    services = df[df["bucket"] == "services"]
    energy_util = df[df["bucket"] == "energy_util"]
    s2_goods = pd.concat([goods, energy_util])

    subsidy_mask = s2_goods["cpi_mid_name"].isin(["電気代", "ガス代"]) & s2_goods["year"].isin([2023, 2024])
    s3_goods = s2_goods[~subsidy_mask]

    return {
        "S0": {"all39": df},
        "S1": {"goods": goods, "services": services},
        "S2": {"goods": s2_goods, "services": services},
        "S3": {"goods": s3_goods, "services": services},
    }


def compute_contrast(force: bool = False) -> pd.DataFrame:
    """§1.3 の4仕様×指標を計算し goods_services_contrast.csv にキャッシュする。"""
    cache_path = PRICE_DIR / "goods_services_contrast.csv"
    if cache_path.exists() and not force:
        cached = pd.read_csv(cache_path, dtype={"year_or_window": str})
        cached["note"] = cached["note"].fillna("")
        return cached

    df = load_panel()
    specs = _bucket_frames(df)

    rows = []
    for spec, buckets in specs.items():
        for bucket, bdf in buckets.items():
            # 年次相関
            corrs = yearly_corr(bdf)
            for year, (corr, n) in corrs.items():
                rows.append({
                    "spec": spec,
                    "bucket": bucket,
                    "metric": "corr",
                    "year_or_window": str(year),
                    "value": corr,
                    "n": n,
                    "note": "",
                })

            # pooled 回帰 β（ショック窓・プラセボ窓）
            for window_name, years in (("shock", SHOCK_YEARS), ("placebo", PLACEBO_YEARS)):
                reg = run_bucket_regression(bdf, years)
                note = (
                    f"p は entity-cluster（クラスタ数={reg['n_categories']}）・"
                    "exposure-robust でない参考値"
                )
                rows.append({
                    "spec": spec,
                    "bucket": bucket,
                    "metric": "beta",
                    "year_or_window": window_name,
                    "value": reg["beta"],
                    "n": reg["n_categories"],
                    "note": note,
                })
                rows.append({
                    "spec": spec,
                    "bucket": bucket,
                    "metric": "beta_p",
                    "year_or_window": window_name,
                    "value": reg["pval"],
                    "n": reg["n_categories"],
                    "note": note,
                })

    out = pd.DataFrame(rows)
    PRICE_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(cache_path, index=False)
    return out


def check_golden(df: pd.DataFrame) -> None:
    """S0 の corr を GOLDEN_S0_CORR と突合（§6-1）。"""
    sub = df[(df.spec == "S0") & (df.metric == "corr")]
    for year, expected in GOLDEN_S0_CORR.items():
        actual = float(sub[sub.year_or_window == str(year)]["value"].iloc[0])
        assert abs(actual - expected) <= 0.005, f"golden mismatch {year}: {actual} vs {expected}"
    print("golden OK")


def print_summary(df: pd.DataFrame) -> None:
    """結果数値は全て df から f-string で出す（直書き禁止）。"""
    print("\n=== goods-services contrast: 年次相関（spec別・bucket別） ===")
    for spec in ["S0", "S1", "S2", "S3"]:
        sub = df[(df.spec == spec) & (df.metric == "corr")]
        for bucket in sorted(sub["bucket"].unique()):
            bsub = sub[sub.bucket == bucket].sort_values("year_or_window")
            vals = ", ".join(
                f"{row.year_or_window}:{row.value:+.2f}(n={int(row.n)})" if pd.notna(row.value)
                else f"{row.year_or_window}:NaN(n={int(row.n)})"
                for row in bsub.itertuples()
            )
            print(f"  [{spec}] {bucket}: {vals}")

    print("\n=== pooled 回帰 β（ショック窓 vs プラセボ窓） ===")
    for spec in ["S0", "S1", "S2", "S3"]:
        sub = df[(df.spec == spec) & (df.metric == "beta")]
        for bucket in sorted(sub["bucket"].unique()):
            bsub = sub[sub.bucket == bucket]
            shock = bsub[bsub.year_or_window == "shock"]
            placebo = bsub[bsub.year_or_window == "placebo"]
            shock_p = df[
                (df.spec == spec) & (df.bucket == bucket)
                & (df.metric == "beta_p") & (df.year_or_window == "shock")
            ]["value"].iloc[0]
            print(
                f"  [{spec}] {bucket}: shock β={shock['value'].iloc[0]:+.4f} (p={shock_p:.4f}), "
                f"placebo β={placebo['value'].iloc[0]:+.4f}  [{shock['note'].iloc[0]}]"
            )


def plot_contrast(df: pd.DataFrame, output_path: Path | None = None) -> None:
    """左: S0 の年次相関棒（既存 fig_yearly_correlation と同スタイル）
    右: S1 の goods vs services 年次相関を並置。"""
    import japanize_matplotlib  # noqa: F401

    if output_path is None:
        output_path = PRICE_DIR / "fig_goods_services_contrast.png"

    shock_years = list(range(2021, 2025))
    placebo_years = list(range(2015, 2020))
    all_years = sorted(placebo_years + shock_years)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    fig.suptitle(
        "goods-services contrast: 財/サービス分解による年次相関コントラストの分解（DEC-022）",
        fontsize=13, fontweight="bold",
    )

    # 左: S0
    ax = axes[0]
    s0 = df[(df.spec == "S0") & (df.metric == "corr")]
    corrs = [s0[s0.year_or_window == str(yr)]["value"].iloc[0] for yr in all_years]
    colors = ["#c0392b" if yr in shock_years else "#2980b9" for yr in all_years]
    ax.bar(all_years, corrs, color=colors, alpha=0.82, edgecolor="white", linewidth=0.8)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(2019.5, color="gray", linewidth=1.2, linestyle="--", alpha=0.7)
    ax.set_xticks(all_years)
    ax.set_xticklabels(all_years, rotation=45, fontsize=9)
    ax.set_xlabel("年")
    ax.set_ylabel("IC-ΔCPI 相関係数 r")
    ax.set_title("S0: 全39カテゴリー")

    # 右: S1 goods vs services
    ax = axes[1]
    s1 = df[(df.spec == "S1") & (df.metric == "corr")]
    width = 0.35
    x = range(len(all_years))
    for i, bucket in enumerate(["goods", "services"]):
        bsub = s1[s1.bucket == bucket]
        vals = [bsub[bsub.year_or_window == str(yr)]["value"].iloc[0] for yr in all_years]
        offset = (i - 0.5) * width
        ax.bar([xi + offset for xi in x], vals, width=width, label=bucket, alpha=0.82)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(3.5, color="gray", linewidth=1.2, linestyle="--", alpha=0.7)
    ax.set_xticks(list(x))
    ax.set_xticklabels(all_years, rotation=45, fontsize=9)
    ax.set_xlabel("年")
    ax.set_title("S1: goods vs services")
    ax.legend(fontsize=9, loc="upper left")

    plt.tight_layout()
    PRICE_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    df = compute_contrast()
    check_golden(df)
    print_summary(df)
    plot_contrast(df)
