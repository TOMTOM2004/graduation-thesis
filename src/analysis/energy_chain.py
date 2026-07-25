"""
Task B: エネルギー起点の連鎖会計（accounting decomposition, NOT causal identification）.

仮説「コストプッシュの大元はエネルギー輸入」を会計的に定量化する。
各 CPI カテゴリの輸入コスト曝露（import content, 直接+間接 Leontief 伝播・
競争輸入型・B-4是正済）のうち、エネルギー投入（石油・石炭・天然ガス、
IO 061/211/212/461/462）経由の比率を計算する。

入力（既存成果物・一切変更しない）:
  - data/processed/import-content/mid_category_ic_by_group.csv
      IC_{c,g} = Σ_i B(c,i)·(μ_g^T L^d)_i  （tasks/_a4_groupspec.py 生成・B-4是正済）
  - data/processed/bridge-matrix/mid_category_import_content.csv
      pc_value_bn_jpy（IO 民間消費列の中分類別消費額 = 集計ウェイト）
  - src/analysis/trade_loss.compute_annual_price_index()
      BOJ CGPI 輸入物価・5グループ年平均（2020=100）
  - src/analysis/quintile_impact.load_expenditure_shares(2019)
      家計調査 2019年 五分位別 10大費目支出シェア

出力: data/processed/energy-chain/
  - energy_origin_shares.csv   カテゴリ別（中分類41 + 10大費目集計）
  - energy_chain_summary.txt   集計値・五分位・トップ10
  - fig_energy_origin.png      10大費目別エネルギー起因比率（横棒）
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from src.utils.io_utils import load_io_table, compute_input_coefficients
from src.analysis.import_content import GROUPS, GROUP_JA, SECTOR_GROUP_MAP
from src.analysis.bridge_matrix_mid import build_bridge_matrix_mid, CPI_MID_CATEGORY_MAP
from src.analysis.trade_loss import compute_annual_price_index
from src.analysis.quintile_impact import load_expenditure_shares, QUINTILE_LABELS

plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Maru Gothic Pro"]

DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
OUT_DIR = DATA_PROCESSED / "energy-chain"

IC_BY_GROUP_PATH = DATA_PROCESSED / "import-content" / "mid_category_ic_by_group.csv"
MID_IC_PATH = DATA_PROCESSED / "bridge-matrix" / "mid_category_import_content.csv"

# 中分類の hh_group → 家計調査 10大費目（cat01_code, 名称）
# transport と comms は家計調査では「交通・通信」に統合されている
HH_GROUP_TO_MAJOR: dict[str, tuple[int, str]] = {
    "food": (60, "食料"),
    "housing": (102, "住居"),
    "energy": (107, "光熱・水道"),
    "furniture": (112, "家具・家事用品"),
    "clothing": (122, "被服及び履物"),
    "health": (140, "保健医療"),
    "transport": (145, "交通・通信"),
    "comms": (145, "交通・通信"),
    "education": (152, "教育"),
    "recreation": (156, "教養娯楽"),
    "other": (165, "その他の消費支出"),
}

SHOCK_FROM, SHOCK_TO = 2020, 2022


def load_mid_ic_by_group() -> pd.DataFrame:
    """中分類×5商品グループ IC に消費ウェイトと10大費目を付与して返す。"""
    icg = pd.read_csv(IC_BY_GROUP_PATH)
    # 列名の "group" は家計側の大費目グループ（商品グループと紛らわしいため改名）
    icg = icg.rename(columns={"group": "hh_group"})

    mid_ic = pd.read_csv(MID_IC_PATH)[["cpi_mid_name", "pc_value_bn_jpy"]]
    df = icg.merge(mid_ic, on="cpi_mid_name", how="left", validate="1:1")
    if df["pc_value_bn_jpy"].isna().any():
        missing = df[df["pc_value_bn_jpy"].isna()]["cpi_mid_name"].tolist()
        raise ValueError(f"消費ウェイト欠損: {missing}")

    df["major_code"] = df["hh_group"].map(lambda g: HH_GROUP_TO_MAJOR[g][0])
    df["major_name"] = df["hh_group"].map(lambda g: HH_GROUP_TO_MAJOR[g][1])
    return df


def build_variant_ic_by_group() -> pd.DataFrame:
    """
    感度分析: 誘発輸入ベースの IC_{c,g}（標準的な競争輸入型の誘発輸入公式）。

    リポジトリ既定の IC = μ_g^T L^d は、輸入浸透率 μ_i が 1 に近い投入財
    （原油・天然ガス μ≈0.99）の連鎖を μ_i·(1−μ_i)·A の重みで数えるため、
    「電気の輸入燃料コスト」等を大幅に過小計上する（例: 061→461 リンクで約1/80）。
    標準的な誘発輸入は M = μ̂(Ax+f), x = L^d(I−μ̂)f から:

        ic_j^g = μ_j·1{j∈g} + (1−μ_j)·(μ_g^T A L^d)_j

    本関数はこの定義で中分類別 IC_{c,g} を再計算する（既存ファイルは変更しない）。
    """
    io = load_io_table()
    A = compute_input_coefficients(io)
    x = io["output"]
    imp = io["imports"].abs()
    mu = (imp / (x + imp).replace(0, np.inf)).fillna(0.0)
    n = A.shape[0]
    L_d = np.linalg.inv(np.eye(n) - (np.eye(n) - np.diag(mu.values)) @ A.values)
    codes = io["sector_codes"]

    sector_ic_g = {}
    for g in GROUPS:
        mu_g = np.array([mu[c] if SECTOR_GROUP_MAP.get(c) == g else 0.0 for c in codes])
        chain = mu_g @ A.values @ L_d  # (μ_g^T A L^d)_j
        direct = np.array([mu[c] if SECTOR_GROUP_MAP.get(c) == g else 0.0 for c in codes])
        ic_g = direct + (1.0 - mu.values) * chain
        sector_ic_g[g] = pd.Series(np.clip(ic_g, 0, 1), index=codes)

    bridge = build_bridge_matrix_mid()
    rows = []
    for cat_name in CPI_MID_CATEGORY_MAP:
        w = bridge.loc[cat_name]
        rec = {"cpi_mid_name": cat_name}
        for g in GROUPS:
            rec[f"ic_{g}"] = float((w * sector_ic_g[g]).sum())
        rec["ic_total"] = sum(rec[f"ic_{g}"] for g in GROUPS)
        rows.append(rec)
    return pd.DataFrame(rows)


def compute_group_shocks() -> dict[str, float]:
    """5グループの 2020→2022 輸入物価上昇率（fraction）。BOJ CGPI 年平均から計算。"""
    annual = compute_annual_price_index()
    pv = annual.pivot(index="year", columns="group", values="price_index")
    shocks = {}
    for g in GROUPS:
        p0 = pv.loc[SHOCK_FROM, g]
        p1 = pv.loc[SHOCK_TO, g]
        shocks[g] = p1 / p0 - 1.0
    return shocks


def decompose(df: pd.DataFrame, shocks: dict[str, float]) -> pd.DataFrame:
    """カテゴリごとに IC 分解・エネルギー比率・ショック加重版を計算。"""
    out = df.copy()
    # (1) 静的な IC 構成: エネルギー経由の IC 比率
    out["energy_share_of_ic"] = out["ic_energy"] / out["ic_total"]

    # (2) ショック加重: 予測輸入コストプッシュ（2020→2022, pp of category price）
    for g in GROUPS:
        out[f"push_{g}_pp"] = out[f"ic_{g}"] * shocks[g] * 100.0
    push_cols = [f"push_{g}_pp" for g in GROUPS]
    out["push_total_pp"] = out[push_cols].sum(axis=1)
    out["energy_share_of_push"] = out["push_energy_pp"] / out["push_total_pp"]
    return out


def aggregate_major(mid: pd.DataFrame) -> pd.DataFrame:
    """中分類 → 10大費目へ消費額（IO民間消費列）加重で集計。"""
    def agg(sub: pd.DataFrame) -> pd.Series:
        w = sub["pc_value_bn_jpy"]
        wsum = w.sum()
        rec = {"pc_value_bn_jpy": wsum, "n_mid": len(sub)}
        for c in (
            [f"ic_{g}" for g in GROUPS]
            + ["ic_total"]
            + [f"push_{g}_pp" for g in GROUPS]
            + ["push_total_pp"]
        ):
            rec[c] = (sub[c] * w).sum() / wsum
        return pd.Series(rec)

    major = (
        mid.groupby(["major_code", "major_name"])
        .apply(agg, include_groups=False)
        .reset_index()
    )
    major["energy_share_of_ic"] = major["ic_energy"] / major["ic_total"]
    major["energy_share_of_push"] = major["push_energy_pp"] / major["push_total_pp"]
    return major.sort_values("major_code").reset_index(drop=True)


def quintile_energy_origin(major: pd.DataFrame) -> pd.DataFrame:
    """五分位別: 輸入コスト曝露合計に占めるエネルギー起因比率（2019支出シェア加重）。"""
    shares = load_expenditure_shares(year=2019)  # index=quintile, cols=hh_cat_code
    m = major.set_index("major_code")
    rows = []
    for q in shares.index:
        s = shares.loc[q]
        # 静的IC加重
        ic_total = sum(s.get(c, 0.0) * m.loc[c, "ic_total"] for c in m.index)
        ic_energy = sum(s.get(c, 0.0) * m.loc[c, "ic_energy"] for c in m.index)
        # ショック加重（2020→2022 push）
        push_total = sum(s.get(c, 0.0) * m.loc[c, "push_total_pp"] for c in m.index)
        push_energy = sum(s.get(c, 0.0) * m.loc[c, "push_energy_pp"] for c in m.index)
        rows.append({
            "quintile": q,
            "quintile_label": QUINTILE_LABELS.get(q, str(q)),
            "weighted_ic_total": ic_total,
            "weighted_ic_energy": ic_energy,
            "energy_share_of_ic": ic_energy / ic_total,
            "weighted_push_total_pp": push_total,
            "weighted_push_energy_pp": push_energy,
            "energy_share_of_push": push_energy / push_total,
        })
    return pd.DataFrame(rows)


def make_figure(major_canon: pd.DataFrame, major_var: pd.DataFrame, path: Path) -> None:
    """10大費目別エネルギー起因比率（ショック加重・2定義併記）。"""
    mv = major_var.set_index("major_code")
    d = major_canon.copy()
    d["var_share"] = d["major_code"].map(mv["energy_share_of_push"])
    d = d.sort_values("var_share")
    y = np.arange(len(d))
    fig, ax = plt.subplots(figsize=(9, 5.8))
    ax.barh(y + 0.2, d["var_share"] * 100, height=0.38, color="#d95f02", alpha=0.9,
            label="誘発輸入定義（感度・μ̂(Ax+f) ベース）")
    ax.barh(y - 0.2, d["energy_share_of_push"] * 100, height=0.38, color="#1b4965",
            label="本文既定 IC 定義（B-4是正済）")
    ax.set_yticks(y)
    ax.set_yticklabels(d["major_name"], fontsize=10)
    ax.set_xlabel("輸入コスト曝露（2020→2022 ショック加重）に占めるエネルギー起因比率（%）",
                  fontsize=10)
    ax.set_title("10大費目別・輸入コスト曝露のエネルギー起因比率\n"
                 "（産業連関表 Leontief 伝播による会計分解・直接+間接・因果識別ではない）",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9, loc="lower right")
    ax.set_xlim(0, 100)
    ax.grid(axis="x", alpha=0.3)
    for yi, (sv, sc) in zip(y, zip(d["var_share"], d["energy_share_of_push"])):
        ax.annotate(f"{sv*100:.0f}%", (sv * 100, yi + 0.2), xytext=(4, -3),
                    textcoords="offset points", fontsize=8.5, color="#d95f02",
                    fontweight="bold")
        ax.annotate(f"{sc*100:.0f}%", (sc * 100, yi - 0.2), xytext=(4, -3),
                    textcoords="offset points", fontsize=8, color="#1b4965")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    shocks = compute_group_shocks()

    # --- 定義1: リポジトリ既定 IC = μ_g^T L^d（B-4是正済・既存CSV再利用）---
    mid = decompose(load_mid_ic_by_group(), shocks)
    major = aggregate_major(mid)
    quint = quintile_energy_origin(major)

    # --- 定義2（感度）: 誘発輸入ベース ---
    base_meta = load_mid_ic_by_group()[
        ["cpi_mid_name", "hh_group", "major_code", "major_name",
         "is_competitive_import", "pc_value_bn_jpy"]
    ]
    mid_v = base_meta.merge(build_variant_ic_by_group(), on="cpi_mid_name",
                            how="left", validate="1:1")
    mid_v = decompose(mid_v, shocks)
    major_v = aggregate_major(mid_v)
    quint_v = quintile_energy_origin(major_v)

    # --- 集計（全消費・IO民間消費額加重）---
    def agg_stats(df: pd.DataFrame) -> dict:
        w = df["pc_value_bn_jpy"]
        return {
            "ic_total": (df["ic_total"] * w).sum() / w.sum(),
            "ic_energy": (df["ic_energy"] * w).sum() / w.sum(),
            "push_total": (df["push_total_pp"] * w).sum() / w.sum(),
            "push_energy": (df["push_energy_pp"] * w).sum() / w.sum(),
        }

    agg = agg_stats(mid)
    agg_v = agg_stats(mid_v)

    # --- CSV: 中分類 + 10大費目 × 2定義 ---
    out_cols = (
        ["cpi_mid_name", "hh_group", "major_code", "major_name",
         "is_competitive_import", "pc_value_bn_jpy"]
        + [f"ic_{g}" for g in GROUPS] + ["ic_total", "energy_share_of_ic"]
        + [f"push_{g}_pp" for g in GROUPS] + ["push_total_pp", "energy_share_of_push"]
    )
    parts = []
    for df, level, defn in [
        (mid, "mid", "canonical_muT_Ld"),
        (mid_v, "mid", "induced_import"),
    ]:
        p = df[out_cols].copy()
        p["level"] = level
        p["definition"] = defn
        parts.append(p)
    for df, defn in [(major, "canonical_muT_Ld"), (major_v, "induced_import")]:
        p = df.copy()
        p["cpi_mid_name"] = p["major_name"]
        p["level"] = "major"
        p["definition"] = defn
        parts.append(p)
    combined = pd.concat(parts, ignore_index=True)
    combined.to_csv(OUT_DIR / "energy_origin_shares.csv", index=False)

    quint["definition"] = "canonical_muT_Ld"
    quint_v["definition"] = "induced_import"
    pd.concat([quint, quint_v], ignore_index=True).to_csv(
        OUT_DIR / "quintile_energy_origin.csv", index=False)

    make_figure(major, major_v, OUT_DIR / "fig_energy_origin.png")

    # --- summary ---
    top10 = mid.sort_values("energy_share_of_push", ascending=False).head(10)
    top10_v = mid_v.sort_values("energy_share_of_push", ascending=False).head(10)
    lines = []
    lines.append("=" * 72)
    lines.append("エネルギー起点の連鎖会計（Task B）— 輸入コスト曝露のエネルギー起因比率")
    lines.append("=" * 72)
    lines.append("")
    lines.append("【定義】会計分解（因果識別ではない）。IC_{c,g} = Σ_i B(c,i)·(μ_g^T L^d)_i")
    lines.append("  （2020年IO表・競争輸入型・直接+間接 Leontief 伝播・B-4是正済）")
    lines.append("  エネルギー = 石油・石炭・天然ガス由来（IO 061/211/212/461/462、原油単独ではない）")
    lines.append("")
    lines.append(f"【輸入物価ショック {SHOCK_FROM}→{SHOCK_TO}（BOJ CGPI 年平均）】")
    for g in GROUPS:
        lines.append(f"  {GROUP_JA[g]:<16s}: {shocks[g]*+100:+7.1f}%")
    lines.append("")
    for label, a, mj, qt, tp in [
        ("定義1: 本文既定 IC = μᵀLᵈ（B-4是正済・論文の他数値と整合）",
         agg, major, quint, top10),
        ("定義2（感度）: 誘発輸入ベース ic_j = μ_j + (1−μ_j)(μ_gᵀA Lᵈ)_j",
         agg_v, major_v, quint_v, top10_v),
    ]:
        lines.append("─" * 72)
        lines.append(f"◆ {label}")
        lines.append("─" * 72)
        lines.append("【集計（IO民間消費額加重・中分類41カテゴリ）】")
        lines.append(f"  総輸入含有率 IC          : {a['ic_total']:.4f}")
        lines.append(f"  うちエネルギー経由        : {a['ic_energy']:.4f}"
                     f"（構成比 {a['ic_energy']/a['ic_total']*100:.1f}%）")
        lines.append(f"  予測輸入コストプッシュ計   : {a['push_total']:.2f}pp（2020→2022）")
        lines.append(f"  うちエネルギー起因        : {a['push_energy']:.2f}pp"
                     f"（構成比 {a['push_energy']/a['push_total']*100:.1f}%）")
        lines.append("")
        lines.append("【10大費目別】IC_c／エネルギー構成比（静的）／エネルギー起因比率（ショック加重）")
        for _, r in mj.iterrows():
            lines.append(
                f"  {r['major_name']:<10s}: IC={r['ic_total']:.3f}  "
                f"静的エネ比={r['energy_share_of_ic']*100:5.1f}%  "
                f"push={r['push_total_pp']:5.2f}pp  "
                f"エネ起因比={r['energy_share_of_push']*100:5.1f}%"
            )
        lines.append("")
        lines.append("【五分位別（2019年支出シェア加重・二人以上の世帯）】")
        for _, r in qt.iterrows():
            lines.append(
                f"  {r['quintile_label']:<8s}: 加重push={r['weighted_push_total_pp']:5.2f}pp  "
                f"エネ起因比={r['energy_share_of_push']*100:5.1f}%  "
                f"（静的IC加重エネ比={r['energy_share_of_ic']*100:5.1f}%）"
            )
        lines.append("")
        lines.append("【エネルギー起因比率トップ10（中分類・ショック加重）】")
        for _, r in tp.iterrows():
            lines.append(
                f"  {r['cpi_mid_name']:<14s}: エネ起因比={r['energy_share_of_push']*100:5.1f}%  "
                f"push={r['push_total_pp']:5.2f}pp  IC={r['ic_total']:.3f}"
            )
        lines.append("")
    lines.append("【2定義の乖離について】")
    lines.append("  既定 IC = μᵀLᵈ は μ_i≈1 の投入財（原油・天然ガス μ≈0.99）の連鎖を")
    lines.append("  μ_i·(1−μ_i)·A の重みで数えるため、電気・ガス代の輸入燃料コスト経由の")
    lines.append("  曝露を大幅に過小計上する（061→461 リンクで約1/80）。誘発輸入定義は")
    lines.append("  M=μ̂(Ax+f) から導出した標準形。エネルギー起因比率は定義2の方が高く、")
    lines.append("  「大元はエネルギー」仮説の評価には定義2が経済的に適切と考えられるが、")
    lines.append("  論文の既存数値（IC・shift-share 等）は定義1で計算されている点に留意。")
    lines.append("")
    lines.append("【留意事項（正直な限界）】")
    lines.append("  1. これはコスト曝露の会計分解（Leontief・行動反応なし・価格設定行動なし）。")
    lines.append("     因果識別ではない。")
    lines.append("  2. 「エネルギー」= 石油・石炭・天然ガス輸入（+電力・ガス供給の輸入分）。")
    lines.append("     原油単独ではない。")
    lines.append("  3. 食料の非エネルギー輸入チャネル（穀物等）は food グループとして別掲・")
    lines.append("     本分解では energy に含めない。")
    lines.append("  4. C-4 overshoot の注意は CPI 水準予測（push_total_pp の絶対値）に適用される。")
    lines.append("     構成比（energy_share_*）は共通の Leontief オブジェクトの比であるため")
    lines.append("     相対的に頑健だが、IC/Leontief の構築（セクター→グループのマッピング、")
    lines.append("     ブリッジ行列、競争輸入型仮定）には依存する（DEC-014: β-invariant≠robust）。")
    lines.append("  5. 5グループ外の輸入（電子部品・輸送機械等）は本分解の分母に含まれない。")
    lines.append("     「輸入コスト曝露」は5グループ（エネ・金属・化学・食料・木材）起因分の合計。")

    summary = "\n".join(lines)
    (OUT_DIR / "energy_chain_summary.txt").write_text(summary, encoding="utf-8")
    print(summary)
    print(f"\nSaved: {OUT_DIR}")


if __name__ == "__main__":
    main()
