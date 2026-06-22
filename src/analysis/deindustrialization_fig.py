"""
本論補強用の図表生成: 2022年輸入価格ショックによる交易損失の国際比較。

探索仮説（製造業→耐性）は反証されたが（DEC-IDEA-02）、その過程で得た
クロスカントリー・データは本論の主機構「輸入/エネルギー依存→所得流出」を
日本の国際的位置づけとして補強する。本論の考察・国際比較節で使用する。

出力:
  data/processed/deindustrialization/fig_tot_loss_ranking.png
  data/processed/deindustrialization/fig_energy_tot_loss.png
  data/processed/deindustrialization/japan_intl_comparison.md
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import statsmodels.api as sm

plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Maru Gothic Pro"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed" / "deindustrialization"

C_LOSS = "#c0392b"     # 損失(流出)
C_GAIN = "#27ae60"     # 利得
C_JP = "#1f4e79"       # 日本ハイライト
C_FIT = "#b03050"      # 回帰線(emphasis)

JP_NAME = {
    "USA": "米国", "CAN": "カナダ", "MEX": "メキシコ", "GBR": "英国",
    "DEU": "ドイツ", "FRA": "フランス", "ITA": "イタリア", "ESP": "スペイン",
    "NLD": "オランダ", "BEL": "ベルギー", "AUT": "オーストリア", "CHE": "スイス",
    "SWE": "スウェーデン", "NOR": "ノルウェー", "DNK": "デンマーク",
    "FIN": "フィンランド", "PRT": "ポルトガル", "IRL": "アイルランド",
    "GRC": "ギリシャ", "POL": "ポーランド", "CZE": "チェコ", "HUN": "ハンガリー",
    "SVK": "スロバキア", "SVN": "スロベニア", "EST": "エストニア",
    "LVA": "ラトビア", "LTU": "リトアニア", "LUX": "ルクセンブルク",
    "ISL": "アイスランド", "JPN": "日本", "KOR": "韓国", "AUS": "オーストラリア",
    "NZL": "ニュージーランド", "TUR": "トルコ", "ISR": "イスラエル",
    "CHL": "チリ", "COL": "コロンビア", "CRI": "コスタリカ", "CHN": "中国",
    "IND": "インド", "BRA": "ブラジル", "IDN": "インドネシア",
    "ZAF": "南アフリカ", "SAU": "サウジアラビア", "THA": "タイ", "MYS": "マレーシア",
}


def jname(iso, fallback=""):
    return JP_NAME.get(iso, fallback)


def load() -> pd.DataFrame:
    df = pd.read_csv(OUT / "xc_2022.csv", index_col=0)
    return df


def fig_ranking(df: pd.DataFrame):
    d = df.dropna(subset=["tot_loss_2022"]).sort_values("tot_loss_2022")
    colors = [C_JP if i == "JPN" else (C_LOSS if v > 0 else C_GAIN)
              for i, v in zip(d.index, d["tot_loss_2022"])]
    fig, ax = plt.subplots(figsize=(8.2, 11))
    y = np.arange(len(d))
    ax.barh(y, d["tot_loss_2022"], color=colors, alpha=0.85)
    ax.set_yticks(y)
    labels = [jname(i, c) + ("  ◀" if i == "JPN" else "")
              for i, c in zip(d.index, d["country"])]
    ax.set_yticklabels(labels, fontsize=8)
    for t, i in zip(ax.get_yticklabels(), d.index):
        if i == "JPN":
            t.set_color(C_JP); t.set_fontweight("bold")
    ax.axvline(0, color="#333", lw=0.8)
    ax.set_xlabel("2022年 交易損失 income effect（％GDP、正＝所得の海外流出）", fontsize=10)
    ax.set_title("輸入価格ショックによる実質所得流出の国際比較（2022年・46ヶ国）\n"
                 "赤＝流出 / 緑＝利得（エネルギー輸出国）", fontsize=11, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    jp = d.loc["JPN", "tot_loss_2022"]
    ax.annotate(f"日本 {jp:.2f}％GDP", xy=(jp, list(d.index).index("JPN")),
                xytext=(jp + 2.5, list(d.index).index("JPN")),
                fontsize=9, color=C_JP, fontweight="bold",
                va="center", arrowprops=dict(arrowstyle="->", color=C_JP))
    plt.tight_layout()
    p = OUT / "fig_tot_loss_ranking.png"
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    return p


def fig_scatter(df: pd.DataFrame):
    d = df.dropna(subset=["tot_loss_2022", "eimp"]).copy()
    fig, ax = plt.subplots(figsize=(9, 6.2))
    is_jp = d.index == "JPN"
    ax.scatter(d.loc[~is_jp, "eimp"], d.loc[~is_jp, "tot_loss_2022"],
               s=42, color="#7f8c8d", alpha=0.7, edgecolor="white", linewidth=0.5)
    ax.scatter(d.loc[is_jp, "eimp"], d.loc[is_jp, "tot_loss_2022"],
               s=130, color=C_JP, edgecolor="white", linewidth=1.2, zorder=5)

    # OLS fit
    X = sm.add_constant(d["eimp"])
    m = sm.OLS(d["tot_loss_2022"], X).fit()
    xs = np.linspace(d["eimp"].min(), d["eimp"].max(), 100)
    ax.plot(xs, m.params["const"] + m.params["eimp"] * xs,
            color=C_FIT, lw=2, label=f"回帰直線（R²={m.rsquared:.2f}）")

    # 混雑する右上クラスタ(KOR/ITA)はラベル省略。代表国＋外れ値のみ注記
    for iso in ["DEU", "USA", "NOR", "SAU", "AUS"]:
        if iso in d.index:
            r = d.loc[iso]
            ax.annotate(jname(iso, r["country"]), (r["eimp"], r["tot_loss_2022"]),
                        fontsize=8.5, xytext=(4, -10), textcoords="offset points",
                        color="#444")
    # 日本は矢印付きで空きスペースへ
    jp = d.loc["JPN"]
    ax.annotate("日本", (jp["eimp"], jp["tot_loss_2022"]),
                xytext=(jp["eimp"] - 230, jp["tot_loss_2022"] + 3.2),
                fontsize=12, color=C_JP, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=C_JP, lw=1.3))
    ax.axhline(0, color="#333", lw=0.7, ls=":")
    ax.set_xlabel("純エネルギー輸入（％エネルギー使用、正＝輸入依存・負＝輸出国）", fontsize=10)
    ax.set_ylabel("2022年 交易損失（％GDP、正＝所得流出）", fontsize=10)
    ax.set_title("エネルギー輸入依存が2022年の実質所得流出を規定する\n"
                 "日本は輸入依存・所得流出ともに高位", fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    p = OUT / "fig_energy_tot_loss.png"
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    return p, m


def table_md(df: pd.DataFrame, m):
    d = df.dropna(subset=["tot_loss_2022"]).sort_values("tot_loss_2022", ascending=False)
    rank = {iso: i + 1 for i, iso in enumerate(d.index)}
    n = len(d)
    pick = ["IRL", "TUR", "THA", "ITA", "JPN", "KOR", "DEU", "FRA", "USA",
            "CAN", "AUS", "SAU", "NOR"]
    lines = [
        "# 日本の交易損失 国際比較（2022年・46ヶ国）",
        "",
        "_本論の考察・国際比較節用。探索: `deindustrialization-inflation.md` DEC-IDEA-02 由来。_",
        "",
        f"- **日本の順位: {rank['JPN']}位 / {n}ヶ国**（交易損失 {d.loc['JPN','tot_loss_2022']:.2f}％GDP）",
        f"- 日本の交易条件変化 2021→2022: **{d.loc['JPN','dln_tot']:.1f}％**（標本中の悪化幅最大級）",
        f"- 純エネルギー輸入依存(eimp)が交易損失を強く規定: 単回帰 R²={m.rsquared:.2f}",
        "",
        "| 国 | 交易損失%GDP | 交易条件Δ% | 製造業%GDP | 純エネ輸入 |",
        "|---|---:|---:|---:|---:|",
    ]
    for iso in pick:
        if iso in d.index:
            r = d.loc[iso]
            mark = " **(日本)**" if iso == "JPN" else ""
            lines.append(f"| {jname(iso, r['country'])}{mark} | {r['tot_loss_2022']:.2f} | "
                         f"{r['dln_tot']:.1f} | {r['mfgva']:.1f} | {r['eimp']:.0f} |")
    p = OUT / "japan_intl_comparison.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


if __name__ == "__main__":
    df = load()
    p1 = fig_ranking(df)
    p2, m = fig_scatter(df)
    p3 = table_md(df, m)
    print("saved:")
    for p in (p1, p2, p3):
        print(" ", p.relative_to(ROOT))
