"""日本の供給制約の消去法チェック（日米労働市場・稼働率の記述的比較）.

目的:
    米国型の国内供給制約（大量解雇 → 労働力不足 → 国内供給能力の毀損）が
    日本では起きていないことを公的データで確認し、2021-24年の供給主導
    インフレ（Shapiro分解）が国内要因ではなく輸入経由であることを
    消去法的に補強する（動機部の記述的証拠。因果主張はしない）。

データソース（すべて認証不要の公開ソース）:
    - 米国 失業率 UNRATE / 労働参加率 CIVPART（16歳以上）: FRED CSV
    - 日米 15-64歳 労働参加率(activity rate) LRAC64TTJPM156S /
      LRAC64TTUSM156S（OECD経由・年齢定義を揃えた比較用）: FRED CSV
    - 日本 完全失業率（季節調整値・逆サイクル系列だが値は失業率そのもの）
      および 有効求人倍率（除学卒・季節調整値）:
      e-Stat 景気動向指数 個別系列 statsDataId=0003446462
      （内閣府景気動向指数の採用系列 C9=有効求人倍率, Lg6=完全失業率。
       原典は総務省労働力調査・厚労省一般職業紹介状況）
    - 日本 製造工業稼働率指数（季節調整済・2020=100）:
      e-Stat 製造工業生産能力・稼働率指数 statsDataId=0004052231

注記（ソース切替の記録）:
    労働力調査の季節調整系列を e-Stat で直接テーブル探索したが、
    複合キーワード検索が 0 件・単独キーワードは 1664 件と絞り込み効率が
    悪かったため、失業率は景気動向指数個別系列（原典は労働力調査）、
    参加率は FRED の OECD 系列（15-64歳）に切替えた。

実行: uv run python src/analysis/supply_constraint_check.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.data.estat_api import get_api_key  # noqa: E402

RAW_DIR = ROOT / "data" / "raw" / "labor"
OUT_DIR = ROOT / "data" / "processed" / "supply-constraint"

FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}"
ESTAT_DATA = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

FRED_SERIES = {
    "UNRATE": "米 失業率（16歳以上・季調）",
    "CIVPART": "米 労働参加率（16歳以上・季調）",
    "LRAC64TTJPM156S": "日 労働参加率（15-64歳・OECD・季調）",
    "LRAC64TTUSM156S": "米 労働参加率（15-64歳・OECD・季調）",
}

# 景気動向指数 個別系列（0003446462）の cat01 コード
CI_TABLE_ID = "0003446462"
CI_CODES = {
    "2090": "jp_jobs_to_applicants",  # C9 有効求人倍率(除学卒)
    "3060": "jp_unemployment",  # Lg6 完全失業率(逆サイクル) ※値は失業率
}

# 製造工業稼働率指数 総合季節調整済【月次】2020=100
CAPUTIL_TABLE_ID = "0004052231"
CAPUTIL_MFG_CODE = "1100000000"  # 製造工業

PERIOD_START, PERIOD_END = "2018-01", "2025-12"


# ---------------------------------------------------------------- fetch


def fetch_fred(sid: str) -> pd.Series:
    """FRED CSV を取得（キャッシュあり）し月次 Series を返す。"""
    cache = RAW_DIR / f"fred_{sid}.csv"
    if not cache.exists():
        resp = httpx.get(FRED_CSV.format(sid=sid), timeout=60, follow_redirects=True)
        resp.raise_for_status()
        cache.write_text(resp.text)
        print(f"  downloaded FRED {sid} -> {cache.relative_to(ROOT)}")
    df = pd.read_csv(cache)
    df.columns = ["date", sid]
    df["date"] = pd.PeriodIndex(pd.to_datetime(df["date"]), freq="M")
    s = df.set_index("date")[sid]
    return pd.to_numeric(s, errors="coerce")


def _estat_get(cache_name: str, params: dict) -> dict:
    cache = RAW_DIR / cache_name
    if cache.exists():
        return json.loads(cache.read_text())
    params = {"appId": get_api_key(), **params}
    resp = httpx.get(ESTAT_DATA, params=params, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    status = data["GET_STATS_DATA"]["RESULT"]["STATUS"]
    if status != 0:
        raise RuntimeError(f"e-Stat error status={status}: {data['GET_STATS_DATA']['RESULT']}")
    cache.write_text(json.dumps(data, ensure_ascii=False))
    print(f"  downloaded e-Stat -> {cache.relative_to(ROOT)}")
    return data


def fetch_ci_series() -> pd.DataFrame:
    """景気動向指数 個別系列から 有効求人倍率・完全失業率（月次・季調）."""
    data = _estat_get(
        f"estat_{CI_TABLE_ID}_ci_labor.json",
        {
            "statsDataId": CI_TABLE_ID,
            "cdCat01": ",".join(CI_CODES),
            "cdTimeFrom": "2018000101",
        },
    )
    values = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
    rows = []
    for v in values:
        t = v["@time"]  # e.g. 2019000101 -> 2019-01
        period = pd.Period(f"{t[:4]}-{t[-2:]}", freq="M")
        rows.append((period, CI_CODES[v["@cat01"]], pd.to_numeric(v["$"], errors="coerce")))
    df = pd.DataFrame(rows, columns=["date", "series", "value"])
    return df.pivot(index="date", columns="series", values="value")


def fetch_capacity_utilization() -> pd.Series:
    """製造工業稼働率指数（総合・季調・2020=100・月次）."""
    data = _estat_get(
        f"estat_{CAPUTIL_TABLE_ID}_caputil.json",
        {"statsDataId": CAPUTIL_TABLE_ID, "cdCat02": CAPUTIL_MFG_CODE},
    )
    sd = data["GET_STATS_DATA"]["STATISTICAL_DATA"]
    # time クラスの名称が "201801" 形式（先頭行はウエイト行）
    time_map = {}
    for obj in sd["CLASS_INF"]["CLASS_OBJ"]:
        if obj["@id"] == "time":
            for c in obj["CLASS"]:
                name = c["@name"]
                if name.isdigit() and len(name) == 6:
                    time_map[c["@code"]] = pd.Period(f"{name[:4]}-{name[4:]}", freq="M")
    rows = [
        (time_map[v["@time"]], pd.to_numeric(v["$"], errors="coerce"))
        for v in sd["DATA_INF"]["VALUE"]
        if v["@time"] in time_map
    ]
    s = pd.DataFrame(rows, columns=["date", "jp_capacity_utilization"]).set_index("date")
    return s["jp_capacity_utilization"].sort_index()


# ---------------------------------------------------------------- facts


def yearly_stats(s: pd.Series) -> dict:
    """2019平均 / 2020の極値 / 2022-2025平均."""
    out = {"2019avg": s[s.index.year == 2019].mean()}
    s20 = s[s.index.year == 2020].dropna()
    if len(s20):
        out["2020max"] = s20.max()
        out["2020min"] = s20.min()
    for y in (2022, 2023, 2024, 2025):
        sy = s[s.index.year == y].dropna()
        out[f"{y}avg"] = sy.mean() if len(sy) else float("nan")
    return out


# ---------------------------------------------------------------- figure


def make_figure(df: pd.DataFrame, path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import japanize_matplotlib  # noqa: F401
    import matplotlib.pyplot as plt

    # dataviz skill: 少系列・固定色（JP=青系, US=橙系）、細線、控えめグリッド
    C_JP, C_US = "#2563a8", "#d1662e"
    x = df.index.to_timestamp()

    fig, axes = plt.subplots(2, 2, figsize=(11, 7.5), sharex=True)

    def style(ax, title, ylabel):
        ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(axis="y", color="#dddddd", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=9)

    ax = axes[0, 0]
    ax.plot(x, df["us_unemployment"], color=C_US, lw=1.8, label="米国")
    ax.plot(x, df["jp_unemployment"], color=C_JP, lw=1.8, label="日本")
    style(ax, "失業率（季節調整値）", "%")
    ax.annotate(
        f"米 2020年ピーク {df['us_unemployment'].max():.1f}%",
        xy=(pd.Timestamp("2020-04-01"), df["us_unemployment"].max()),
        xytext=(pd.Timestamp("2021-06-01"), df["us_unemployment"].max() - 1.5),
        fontsize=8.5, color="#555555",
        arrowprops=dict(arrowstyle="-", color="#999999", lw=0.8),
    )
    ax.annotate(
        f"日 ピーク {df['jp_unemployment'].max():.1f}%",
        xy=(pd.Timestamp("2020-10-01"), df["jp_unemployment"].max()),
        xytext=(pd.Timestamp("2021-10-01"), 5.5),
        fontsize=8.5, color="#555555",
        arrowprops=dict(arrowstyle="-", color="#999999", lw=0.8),
    )
    ax.legend(fontsize=9, frameon=False)

    ax = axes[0, 1]
    ax.plot(x, df["us_participation_1564"], color=C_US, lw=1.8, label="米国")
    ax.plot(x, df["jp_participation_1564"], color=C_JP, lw=1.8, label="日本")
    style(ax, "労働参加率（15-64歳・OECD定義・季節調整値）", "%")
    ax.legend(fontsize=9, frameon=False, loc="center right")

    ax = axes[1, 0]
    ax.plot(x, df["jp_jobs_to_applicants"], color=C_JP, lw=1.8)
    ax.axhline(1.0, color="#999999", lw=0.8, ls="--")
    style(ax, "日本 有効求人倍率（除学卒・季節調整値）", "倍")
    ax.text(
        x[-1], 1.02, "1倍", fontsize=8.5, color="#777777", ha="right", va="bottom"
    )

    ax = axes[1, 1]
    ax.plot(x, df["jp_capacity_utilization"], color=C_JP, lw=1.8)
    style(ax, "日本 製造工業稼働率指数（季節調整済・2020=100）", "指数")

    for ax in axes[1]:
        ax.tick_params(axis="x", rotation=0)

    fig.suptitle(
        "日米労働市場と日本の稼働率: 米国型の国内供給制約は日本に見られない",
        fontsize=13, fontweight="bold", y=0.99,
    )
    fig.text(
        0.01, 0.005,
        "出所: FRED (UNRATE, LRAC64TTJPM156S, LRAC64TTUSM156S), "
        "e-Stat 景気動向指数個別系列（原典: 労働力調査・一般職業紹介状況）, "
        "製造工業生産能力・稼働率指数",
        fontsize=7.5, color="#777777",
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.97))
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"  figure -> {path.relative_to(ROOT)}")


# ---------------------------------------------------------------- main


SUMMARY_ARGUMENT = """\
【消去法の論旨（記述的・因果主張はしない）】
米国では2020年に失業率が14.8%へ急騰し労働参加率も約3pp低下、その後の回復過程で
歴史的な労働需給の逼迫（大量離職・賃金高騰）が生じ、国内労働供給の毀損そのものが
供給制約の一因となった。対照的に日本は、失業率のピークが3.1%にとどまり、
労働参加率（15-64歳）はコロナ期の小幅な落ち込みの後も上昇基調を維持
（2019年79.8%→2024年81.6%）、有効求人倍率はコロナ期でも1倍を一度も割らず、
製造工業稼働率指数は2019年平均比でむしろ低め（2024年平均は約12%低い水準）に
推移しており、国内生産能力がフル稼働で逼迫していた形跡もない。すなわち日本には
米国型の国内労働供給制約・能力制約がほぼ存在せず、国内発の供給ショックで
2021-24年のインフレを説明する余地は小さい。したがって Shapiro 分解が示す供給主導シェア（2022年=0.70）の源泉は、
消去法的に国内供給制約ではなく輸入価格経由の外的ショックと解釈するのが自然であり、
本論文の外的要因フレーミングを補強する。
"""


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/4] fetching series ...")
    fred = {sid: fetch_fred(sid) for sid in FRED_SERIES}
    ci = fetch_ci_series()
    caputil = fetch_capacity_utilization()

    df = pd.DataFrame(
        {
            "us_unemployment": fred["UNRATE"],
            "us_participation_16plus": fred["CIVPART"],
            "us_participation_1564": fred["LRAC64TTUSM156S"],
            "jp_participation_1564": fred["LRAC64TTJPM156S"],
            "jp_unemployment": ci["jp_unemployment"],
            "jp_jobs_to_applicants": ci["jp_jobs_to_applicants"],
            "jp_capacity_utilization": caputil,
        }
    )
    df = df.loc[pd.Period(PERIOD_START, "M"): pd.Period(PERIOD_END, "M")]
    df.index.name = "date"
    series_csv = OUT_DIR / "supply_constraint_series.csv"
    df.to_csv(series_csv)
    print(f"[2/4] series -> {series_csv.relative_to(ROOT)}  shape={df.shape}")

    dfy = df.copy()
    dfy.index = dfy.index.to_timestamp()
    facts = pd.DataFrame({col: yearly_stats(dfy[col]) for col in df.columns}).T
    facts.index.name = "series"
    facts_csv = OUT_DIR / "supply_constraint_facts.csv"
    facts.round(2).to_csv(facts_csv)
    print(f"[3/4] facts -> {facts_csv.relative_to(ROOT)}")
    print(facts.round(2).to_string())

    make_figure(df, OUT_DIR / "fig_supply_constraint.png")

    lines = [
        "日本の供給制約の消去法チェック — 主要ファクト",
        f"(生成: supply_constraint_check.py, 対象期間 {PERIOD_START}..{PERIOD_END})",
        "",
        facts.round(2).to_string(),
        "",
        "数値の読み方: 2019avg=コロナ前水準, 2020max/min=コロナ期の極値, 20XXavg=年平均",
        "",
        SUMMARY_ARGUMENT,
        "",
        "データソース:",
        "  - FRED: UNRATE, CIVPART, LRAC64TTUSM156S, LRAC64TTJPM156S (OECD経由・15-64歳)",
        "  - e-Stat 0003446462 景気動向指数 個別系列: C9有効求人倍率(除学卒),",
        "    Lg6完全失業率 (原典: 厚労省 一般職業紹介状況 / 総務省 労働力調査, 季節調整値)",
        "  - e-Stat 0004052231 製造工業生産能力・稼働率指数 (総合・季調・2020=100)",
        "  - 日本の労働参加率は労働力調査の直接テーブル特定が非効率だったため",
        "    FRED(OECD)系列に切替（本文注記済み）。日米とも15-64歳で定義を統一。",
    ]
    summary_txt = OUT_DIR / "supply_constraint_summary.txt"
    summary_txt.write_text("\n".join(lines))
    print(f"[4/4] summary -> {summary_txt.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
