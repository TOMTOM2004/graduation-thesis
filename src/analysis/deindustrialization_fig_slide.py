"""
スライド専用の交易損失ランキング図（2カラム・横長・大きめフォント）。

本論用の縦長46行図（deindustrialization_fig.py の fig_tot_loss_ranking）は
スライド尺だと国名ラベルが微小化して読めない。スライドでは46ヶ国を
左右2パネルに分割し、横長アスペクトで国名を可読サイズにする。

出力: slides/assets/s2b-tot-loss-ranking.png （本論用 png は変更しない）
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = ["Hiragino Sans", "Hiragino Maru Gothic Pro"]
plt.rcParams["axes.unicode_minus"] = False

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "processed" / "deindustrialization"
ASSETS = ROOT / "slides" / "assets"

C_LOSS = "#c0392b"
C_GAIN = "#27ae60"
C_JP = "#1f4e79"

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


def main():
    df = pd.read_csv(OUT / "xc_2022.csv", index_col=0)
    d = df.dropna(subset=["tot_loss_2022"]).sort_values("tot_loss_2022", ascending=False)
    n = len(d)
    rank = {iso: i + 1 for i, iso in enumerate(d.index)}
    half = (n + 1) // 2
    segs = [d.iloc[:half], d.iloc[half:]]

    xmin = d["tot_loss_2022"].min()
    xmax = d["tot_loss_2022"].max()
    pad = (xmax - xmin) * 0.16

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.4))
    for ax, seg in zip(axes, segs):
        seg = seg.iloc[::-1]  # 上位を上に表示
        y = np.arange(len(seg))
        colors = [C_JP if i == "JPN" else (C_LOSS if v > 0 else C_GAIN)
                  for i, v in zip(seg.index, seg["tot_loss_2022"])]
        ax.barh(y, seg["tot_loss_2022"], color=colors, alpha=0.88)
        ax.set_yticks(y)
        labels = [f"{rank[i]}. {jname(i, c)}"
                  for i, c in zip(seg.index, seg["country"])]
        ax.set_yticklabels(labels, fontsize=12)
        for t, i in zip(ax.get_yticklabels(), seg.index):
            if i == "JPN":
                t.set_color(C_JP); t.set_fontweight("bold")
        ax.axvline(0, color="#333", lw=0.9)
        ax.set_xlim(xmin - pad, xmax + pad)
        # 日本は棒の位置に矢印付きで注記
        if "JPN" in seg.index:
            jy = list(seg.index).index("JPN")
            jv = seg.loc["JPN", "tot_loss_2022"]
            ax.annotate(f"◀ 日本 {jv:.2f}%GDP", xy=(jv, jy),
                        xytext=(jv + 3.6, jy),
                        fontsize=11.5, color=C_JP, fontweight="bold", va="center",
                        arrowprops=dict(arrowstyle="->", color=C_JP, lw=1.4))
        ax.set_xlabel("交易損失（％GDP、正＝海外流出）", fontsize=11)
        ax.grid(axis="x", alpha=0.3)
        ax.tick_params(axis="x", labelsize=10)

    fig.suptitle("輸入価格ショックによる実質所得流出の国際比較（2022年・46ヶ国）　"
                 "赤＝流出／緑＝利得（エネルギー輸出国）",
                 fontsize=13, fontweight="bold", y=0.99)
    plt.tight_layout(rect=(0, 0, 1, 0.96))
    ASSETS.mkdir(parents=True, exist_ok=True)
    p = ASSETS / "s2b-tot-loss-ranking.png"
    plt.savefig(p, dpi=150, bbox_inches="tight"); plt.close()
    print("saved:", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
