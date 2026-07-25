"""
ITEM-021 追検証: 五分位 DiD 価格 event-study の曝露測度を 定義2（誘発輸入 IC）に
差し替えて「壁③」（既定 IC=μᵀLᵈ がエネルギー小売の輸入燃料チャネルを構造的に
過小計上する問題）の是正が 2022 年クロスセクション識別を復活させるか検証する。

定義2（energy_chain.build_variant_ic_by_group と同型・ただし全グループ合算＝全セクター μ）:
    ic_j = μ_j + (1−μ_j)·(μᵀ A Lᵈ)_j        （μ = 全セクターの輸入浸透率）
中分類への写像は既定 IC と同一のブリッジ B_mid(c,i)（IO 民間消費列由来）を使う:
    IC_c^{def2} = Σ_i B_mid(c,i)·ic_i^{def2}

事前登録した評価基準（post-hoc 合理化禁止）:
  [i]   β_2022 > 0 かつ p_perm < 0.10（元設計の失敗点）
  [ii]  プレ期 2016–2020 の β_t が 2022–2023 と同規模・同有意水準でない
        （def1: β_2016=+4.41 p_perm=0.272, β_2020=+4.31 p_perm=0.126 より悪化しないか）
  [iii] エネルギー4費目（電気代・ガス代・他の光熱・上下水道料）除外で β_2022 が生き残るか
        （def1 では +4.6 p_perm=0.14）
  [iv]  累積 Δlog CPI 2021→2024 on IC: 符号・有意性（def1 は +4.8, p_perm=0.55）

元スクリプト src/analysis/quintile_did.py は変更しない（同一関数を import して再利用、
IC 列のみ差し替え）。乱数は同一 seed=21・n_perm=5000。
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from src.utils.io_utils import load_io_table, compute_input_coefficients
from src.analysis.bridge_matrix_mid import build_bridge_matrix_mid, CPI_MID_CATEGORY_MAP
from src.analysis.quintile_did import (
    HH_TO_CPI_MID,
    build_panel,
    price_event_study,
    share_event_study,
)

plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Maru Gothic Pro"]

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "processed" / "did-def2"

N_PERM = 5000
SEED = 21
ENERGY_ITEMS = ["電気代", "ガス代", "他の光熱", "上下水道料"]  # group=energy の4費目
KEY_ITEMS = ["電気代", "ガス代", "他の光熱", "自動車等関係費"]  # ガソリンは中分類非独立


def compute_def2_sector_ic() -> tuple[pd.Series, pd.Series]:
    """全セクター μ による誘発輸入 IC: ic_j = μ_j + (1−μ_j)(μᵀ A Lᵈ)_j。"""
    io = load_io_table()
    A = compute_input_coefficients(io)
    x = io["output"]
    imp = io["imports"].abs()
    mu = (imp / (x + imp).replace(0, np.inf)).fillna(0.0)
    n = A.shape[0]
    L_d = np.linalg.inv(np.eye(n) - (np.eye(n) - np.diag(mu.values)) @ A.values)
    chain = mu.values @ A.values @ L_d  # (μᵀ A Lᵈ)_j — μ は全セクター
    ic = mu.values + (1.0 - mu.values) * chain
    return pd.Series(np.clip(ic, 0, 1), index=io["sector_codes"]), mu


def compute_def2_mid_ic() -> pd.DataFrame:
    """中分類 IC^{def2}: 既定 IC と同一ブリッジで写像。"""
    sector_ic, _ = compute_def2_sector_ic()
    bridge = build_bridge_matrix_mid()
    rows = []
    for cat_name in CPI_MID_CATEGORY_MAP:
        w = bridge.loc[cat_name]
        rows.append(
            {"category": cat_name, "ic_def2": float((w * sector_ic).sum())}
        )
    return pd.DataFrame(rows)


def perm_beta(x: np.ndarray, y: np.ndarray, n_perm: int, rng) -> tuple:
    """単回帰 slope + HC1 p + permutation p と null 分布を返す。"""
    beta = np.polyfit(x, y, 1)[0]
    res = smf.ols("y ~ x", data=pd.DataFrame({"x": x, "y": y})).fit(cov_type="HC1")
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = np.polyfit(rng.permutation(x), y, 1)[0]
    p_perm = float((np.abs(null) >= abs(beta)).mean())
    return beta, float(res.pvalues["x"]), p_perm, null


def cumulative_regression(panel: pd.DataFrame, ic_col: str) -> dict:
    """累積 Δlog CPI 2021→2024 on IC（[iv]）。"""
    cats = panel[["category", ic_col, "year", "cpi_index"]].drop_duplicates(
        ["category", "year"]
    )
    piv = cats.pivot(index="category", columns="year", values="cpi_index")
    ic = cats.drop_duplicates("category").set_index("category")[ic_col]
    cum = (np.log(piv[2024]) - np.log(piv[2021])) * 100
    df = pd.concat([ic.rename("ic"), cum.rename("cum")], axis=1).dropna()
    rng = np.random.default_rng(SEED)
    beta, p_hc1, p_perm, _ = perm_beta(
        df["ic"].to_numpy(), df["cum"].to_numpy(), N_PERM, rng
    )
    return {"beta": beta, "p_hc1": p_hc1, "p_perm": p_perm, "n": len(df)}


def event_study_with_null(panel: pd.DataFrame, ic_col: str) -> tuple[pd.DataFrame, dict]:
    """price_event_study と同一手順（同 seed）だが null 分布も保持（図のCI用）。"""
    cats = panel[["category", ic_col, "dlog_cpi", "year"]].drop_duplicates(
        ["category", "year"]
    )
    rng = np.random.default_rng(SEED)
    rows, nulls = [], {}
    for year in sorted(cats["year"].unique()):
        yr = cats[cats["year"] == year].dropna(subset=["dlog_cpi"])
        if len(yr) < 10:
            continue
        x = yr[ic_col].to_numpy()
        y = yr["dlog_cpi"].to_numpy() * 100
        beta, p_hc1, p_perm, null = perm_beta(x, y, N_PERM, rng)
        nulls[year] = null
        rows.append(
            {
                "year": year,
                "n_categories": len(yr),
                "beta_pp_per_IC": round(beta, 3),
                "p_hc1": round(p_hc1, 4),
                "p_perm": round(p_perm, 4),
            }
        )
    return pd.DataFrame(rows), nulls


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------- パネル（元スクリプトと同一）+ 定義2 IC の付与
    panel = build_panel()
    ic2 = compute_def2_mid_ic()
    ic2 = ic2[ic2["category"].isin(HH_TO_CPI_MID.keys())]
    panel = panel.merge(ic2, on="category", how="inner")
    panel = panel.rename(columns={"import_content": "ic_def1"})

    ic_tbl = panel[["category", "group", "ic_def1", "ic_def2"]].drop_duplicates(
        "category"
    ).sort_values("ic_def2", ascending=False)
    corr_p = ic_tbl["ic_def1"].corr(ic_tbl["ic_def2"])
    corr_s = ic_tbl["ic_def1"].corr(ic_tbl["ic_def2"], method="spearman")

    # ---------------- (A) event-study: def1 再現（元関数そのまま）と def2
    panel_def1 = panel.rename(columns={"ic_def1": "import_content"})
    es_def1_orig = price_event_study(panel_def1, n_perm=N_PERM, seed=SEED)
    es_def1, nulls1 = event_study_with_null(panel, "ic_def1")
    es_def2, nulls2 = event_study_with_null(panel, "ic_def2")

    # def1 再現の deviation チェック（元関数出力 vs 本スクリプト実装）
    dev = (
        es_def1_orig.set_index("year")[["beta_pp_per_IC", "p_perm"]]
        - es_def1.set_index("year")[["beta_pp_per_IC", "p_perm"]]
    ).abs().max().max()

    merged = es_def1.merge(es_def2, on="year", suffixes=("_def1", "_def2"))
    out = merged.rename(
        columns={
            "beta_pp_per_IC_def1": "beta_def1",
            "p_hc1_def1": "p_hc1_def1",
            "p_perm_def1": "p_perm_def1",
            "beta_pp_per_IC_def2": "beta_def2",
            "p_hc1_def2": "p_hc1_def2",
            "p_perm_def2": "p_perm_def2",
        }
    )[
        ["year", "beta_def1", "p_hc1_def1", "p_perm_def1",
         "beta_def2", "p_hc1_def2", "p_perm_def2"]
    ]
    out.to_csv(OUT_DIR / "event_study_def2.csv", index=False)

    # ---------------- [iii] エネルギー4費目除外
    panel_noe = panel[~panel["category"].isin(ENERGY_ITEMS)]
    es_noe1, _ = event_study_with_null(panel_noe, "ic_def1")
    es_noe2, _ = event_study_with_null(panel_noe, "ic_def2")

    # ---------------- [iv] 累積 2021→2024
    cum1 = cumulative_regression(panel, "ic_def1")
    cum2 = cumulative_regression(panel, "ic_def2")

    # ---------------- (B) triple-diff（def2 IC）
    panel_td2 = panel.drop(columns=["import_content"], errors="ignore").rename(
        columns={"ic_def2": "import_content"}
    )
    coefs2, pre2 = share_event_study(panel_td2)
    coefs2.to_csv(OUT_DIR / "share_triple_diff_def2.csv", index=False)

    # ---------------- 図
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    for es, nulls, color, dx, label in [
        (es_def1, nulls1, "#888888", -0.13, "定義1（既定 IC = $\\mu^T L^d$）"),
        (es_def2, nulls2, "#1b4965", +0.13,
         "定義2（誘発輸入 IC = $\\mu+(1-\\mu)\\,\\mu^T A L^d$）"),
    ]:
        yrs = es["year"].to_numpy()
        lo = np.array([np.percentile(nulls[y], 2.5) for y in yrs])
        hi = np.array([np.percentile(nulls[y], 97.5) for y in yrs])
        ax.errorbar(
            yrs + dx, es["beta_pp_per_IC"], fmt="o", color=color, markersize=6,
            label=label,
        )
        ax.vlines(yrs + dx, lo, hi, color=color, alpha=0.35, linewidth=5)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(2021.5, color="#c0392b", linestyle="--", linewidth=1)
    ax.annotate("ショック期→", (2021.55, ax.get_ylim()[1] * 0.9), fontsize=9,
                color="#c0392b")
    ax.set_xlabel("年")
    ax.set_ylabel("β_t（pp / IC 単位）")
    ax.set_title(
        "価格 event-study: Δlog CPI_{c,t} = α_t + β_t·IC_c（40費目・年別クロスセクション）\n"
        "帯 = IC ラベル permutation 帰無分布の 95% 区間（n=5000）",
        fontsize=11,
    )
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig_event_study_def2.png", dpi=150)
    plt.close(fig)

    # ---------------- 事前登録基準の判定
    b22 = out[out["year"] == 2022].iloc[0]
    crit_i = (b22["beta_def2"] > 0) and (b22["p_perm_def2"] < 0.10)

    pre_years = [2016, 2017, 2018, 2019, 2020]
    pre2_rows = es_def2[es_def2["year"].isin(pre_years)]
    post2_rows = es_def2[es_def2["year"].isin([2022, 2023])]
    max_pre_beta = pre2_rows["beta_pp_per_IC"].abs().max()
    min_pre_pperm = pre2_rows["p_perm"].min()

    noe22_1 = es_noe1[es_noe1["year"] == 2022].iloc[0]
    noe22_2 = es_noe2[es_noe2["year"] == 2022].iloc[0]

    # ---------------- summary
    lines = []
    lines.append("=" * 76)
    lines.append("五分位 DiD 価格 event-study — 定義2（誘発輸入 IC）による壁③是正テスト")
    lines.append("=" * 76)
    lines.append("")
    lines.append(f"def1 再現 deviation（元関数 price_event_study との最大乖離）: {dev:.6g}")
    lines.append("")
    lines.append("【IC の変化（主要費目）】 def1 = μᵀLᵈ ／ def2 = μ+(1−μ)(μᵀALᵈ)")
    for c in KEY_ITEMS:
        r = ic_tbl[ic_tbl["category"] == c]
        if len(r):
            r = r.iloc[0]
            lines.append(
                f"  {c:<10s}: def1={r['ic_def1']:.4f} → def2={r['ic_def2']:.4f} "
                f"（×{r['ic_def2'] / max(r['ic_def1'], 1e-9):.1f}）"
            )
    lines.append("  （ガソリンは40費目に独立項目なし。自動車等関係費に内包）")
    lines.append("")
    lines.append(f"相関 corr(IC_def1, IC_def2) 40費目: Pearson={corr_p:.3f}, "
                 f"Spearman={corr_s:.3f}")
    d = ic_tbl
    lines.append(f"分布: def1 mean={d['ic_def1'].mean():.3f} sd={d['ic_def1'].std():.3f} "
                 f"range=[{d['ic_def1'].min():.3f},{d['ic_def1'].max():.3f}] / "
                 f"def2 mean={d['ic_def2'].mean():.3f} sd={d['ic_def2'].std():.3f} "
                 f"range=[{d['ic_def2'].min():.3f},{d['ic_def2'].max():.3f}]")
    lines.append("")
    lines.append("【(A) event-study 年別 β_t（pp/IC）】")
    lines.append(out.to_string(index=False))
    lines.append("")
    lines.append("【[iii] エネルギー4費目除外（電気代・ガス代・他の光熱・上下水道料）】")
    lines.append("  def1:")
    lines.append(es_noe1.to_string(index=False))
    lines.append("  def2:")
    lines.append(es_noe2.to_string(index=False))
    lines.append("")
    lines.append("【[iv] 累積 Δlog CPI 2021→2024 on IC】")
    lines.append(f"  def1: β={cum1['beta']:+.2f} p_hc1={cum1['p_hc1']:.3f} "
                 f"p_perm={cum1['p_perm']:.3f} (n={cum1['n']})")
    lines.append(f"  def2: β={cum2['beta']:+.2f} p_hc1={cum2['p_hc1']:.3f} "
                 f"p_perm={cum2['p_perm']:.3f} (n={cum2['n']})")
    lines.append("")
    lines.append("【(B) triple-diff θ_t（IC_def2）】")
    lines.append(coefs2.to_string(index=False))
    lines.append(f"  プレトレンド joint F({pre2['terms']}): F={pre2['F']:.2f}, "
                 f"p={pre2['p']:.4f}")
    lines.append("")
    lines.append("【事前登録基準の判定】")
    lines.append(f"  [i]  β_2022(def2)={b22['beta_def2']:+.2f}, "
                 f"p_perm={b22['p_perm_def2']:.3f} → "
                 f"{'PASS' if crit_i else 'FAIL'}（要: >0 かつ p_perm<0.10）")
    lines.append(f"  [ii] プレ期 def2: max|β|={max_pre_beta:.2f}, "
                 f"min p_perm={min_pre_pperm:.3f} vs post 2022/23 "
                 f"β={post2_rows['beta_pp_per_IC'].tolist()}, "
                 f"p_perm={post2_rows['p_perm'].tolist()}")
    lines.append(f"  [iii] エネ除外 β_2022: def1={noe22_1['beta_pp_per_IC']:+.2f} "
                 f"(p_perm={noe22_1['p_perm']:.3f}) / "
                 f"def2={noe22_2['beta_pp_per_IC']:+.2f} "
                 f"(p_perm={noe22_2['p_perm']:.3f})")
    lines.append(f"  [iv] 累積 def2: β={cum2['beta']:+.2f} (p_perm={cum2['p_perm']:.3f})")

    summary = "\n".join(lines)
    (OUT_DIR / "did_def2_summary.txt").write_text(summary, encoding="utf-8")
    print(summary)
    ic_tbl.to_csv(OUT_DIR / "ic_def1_def2_by_category.csv", index=False)
    print(f"\nSaved: {OUT_DIR}")


if __name__ == "__main__":
    main()
