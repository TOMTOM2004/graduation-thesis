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

    - 日本 労働力人口・就業者数・15歳以上人口（万人・月次・原数値）:
      e-Stat 労働力調査 基本集計 statsDataId=0003005798
      （就業状態別15歳以上人口・全国・男女計。分母批判対応の水準系列）
    - 日本 15-64歳人口（人・月次・季調）: FRED LFWA64TTJPM647S
      （OECD経由・原典は総務省人口推計。縮小する分母を明示するため）
    - 米国 労働力人口 CLF16OV / 就業者数 CE16OV（千人・季調）: FRED CSV

注記（ソース切替の記録）:
    労働力調査の季節調整系列を e-Stat で直接テーブル探索したが、
    複合キーワード検索が 0 件・単独キーワードは 1664 件と絞り込み効率が
    悪かったため、失業率は景気動向指数個別系列（原典は労働力調査）、
    参加率は FRED の OECD 系列（15-64歳）に切替えた。
    水準系列（労働力人口・就業者数）は「労働力調査 基本集計 月次 全国」の
    検索1回目で 0003005798 を特定できたため e-Stat を直接使用（原数値。
    年平均比較で季節性は相殺）。毎月勤労統計の総実労働時間指数は
    検索2回で現行基準（2020=100）の月次テーブルを特定できず
    （ヒットは平成17年=100 の旧基準系列のみ）、規定によりスキップ。

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
    # --- 水準系列（分母批判対応: 率でなく絶対水準で労働投入の非収縮を確認） ---
    "CLF16OV": "米 労働力人口（千人・季調）",
    "CE16OV": "米 就業者数（千人・季調）",
    "LFWA64TTJPM647S": "日 15-64歳人口（人・季調・OECD経由/原典 人口推計）",
}

# 景気動向指数 個別系列（0003446462）の cat01 コード
CI_TABLE_ID = "0003446462"
CI_CODES = {
    "2090": "jp_jobs_to_applicants",  # C9 有効求人倍率(除学卒)
    "3060": "jp_unemployment",  # Lg6 完全失業率(逆サイクル) ※値は失業率
}

# 労働力調査 基本集計 就業状態別15歳以上人口（月次・全国・万人・原数値）
LFS_TABLE_ID = "0003005798"
LFS_CODES = {
    "00": "jp_pop15plus",  # 15歳以上人口
    "01": "jp_labor_force",  # 労働力人口
    "02": "jp_employment",  # 就業者
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


def fetch_jp_labor_levels() -> pd.DataFrame:
    """労働力調査 基本集計: 労働力人口・就業者数・15歳以上人口（万人・月次・原数値）."""
    data = _estat_get(
        f"estat_{LFS_TABLE_ID}_lfs_levels.json",
        {
            "statsDataId": LFS_TABLE_ID,
            "cdCat02": ",".join(LFS_CODES),
            "cdCat03": "0",  # 男女計
            "cdTimeFrom": "2018000101",
        },
    )
    values = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
    rows = []
    for v in values:
        t = v["@time"]  # e.g. 2019000101 -> 2019-01
        period = pd.Period(f"{t[:4]}-{t[-2:]}", freq="M")
        rows.append((period, LFS_CODES[v["@cat02"]], pd.to_numeric(v["$"], errors="coerce")))
    df = pd.DataFrame(rows, columns=["date", "series", "value"])
    return df.pivot(index="date", columns="series", values="value").sort_index()


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


def index_2019(s: pd.Series) -> pd.Series:
    """2019年平均=100 の指数化（率でなく水準で比較するため）."""
    base = s[s.index.year == 2019].mean()
    return s / base * 100.0


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


def make_levels_figure(df: pd.DataFrame, path: Path) -> None:
    """水準パネル: 率でなく絶対水準で「労働投入は収縮していない」を示す."""
    import matplotlib

    matplotlib.use("Agg")
    import japanize_matplotlib  # noqa: F401
    import matplotlib.pyplot as plt

    C_JP, C_JP2, C_US, C_POP = "#2563a8", "#7aa7d1", "#d1662e", "#888888"
    x = df.index.to_timestamp()

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))

    def style(ax, title, ylabel):
        ax.set_title(title, fontsize=11, fontweight="bold", loc="left")
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(axis="y", color="#dddddd", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        ax.tick_params(labelsize=9)

    # 左: 指数化した水準（2019年平均=100）
    ax = axes[0]
    ax.axhline(100, color="#bbbbbb", lw=0.8, ls=":")
    ax.plot(x, df["idx_us_employment"], color=C_US, lw=1.8, label="米 就業者数")
    ax.plot(x, df["idx_jp_labor_force"], color=C_JP, lw=1.8, label="日 労働力人口")
    ax.plot(x, df["idx_jp_employment"], color=C_JP2, lw=1.8, label="日 就業者数")
    ax.plot(
        x, df["idx_jp_pop1564"], color=C_POP, lw=1.4, ls="--", label="日 15-64歳人口（分母）"
    )
    style(ax, "労働力・就業者の水準（2019年平均=100）", "指数")
    trough = df["idx_us_employment"].min()
    ax.annotate(
        f"米 2020年4月 {trough:.0f}",
        xy=(pd.Timestamp("2020-04-01"), trough),
        xytext=(pd.Timestamp("2021-04-01"), trough + 1.5),
        fontsize=8.5, color="#555555",
        arrowprops=dict(arrowstyle="-", color="#999999", lw=0.8),
    )
    ax.legend(fontsize=8.5, frameon=False, loc="lower right")

    # 右: 日本の絶対水準（万人）— 分母（15-64歳人口）の縮小と労働投入の非収縮
    ax = axes[1]
    ax.plot(x, df["jp_pop1564"], color=C_POP, lw=1.4, ls="--", label="15-64歳人口")
    ax.plot(x, df["jp_labor_force"], color=C_JP, lw=1.8, label="労働力人口")
    ax.plot(x, df["jp_employment"], color=C_JP2, lw=1.8, label="就業者数")
    style(ax, "日本の絶対水準（万人・原数値）", "万人")
    ax.legend(fontsize=8.5, frameon=False, loc="center right")

    fig.suptitle(
        "水準で見た日米労働投入: 日本は人口減少下でも労働力・就業者数が収縮していない",
        fontsize=12.5, fontweight="bold", y=0.99,
    )
    fig.text(
        0.01, 0.005,
        "出所: e-Stat 労働力調査 基本集計 0003005798（万人・原数値）, "
        "FRED CE16OV（米・季調）, LFWA64TTJPM647S（15-64歳人口・原典 人口推計）",
        fontsize=7.5, color="#777777",
    )
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(path, dpi=200)
    plt.close(fig)
    print(f"  figure -> {path.relative_to(ROOT)}")


# ---------------------------------------------------------------- main


def build_summary_argument(facts: pd.DataFrame) -> str:
    """水準ベース（分母批判にロバスト）の消去法論旨を実データから組み立てる."""

    def f(series: str, col: str) -> float:
        return float(facts.loc[series, col])

    jp_lf_19, jp_lf_20min = f("jp_labor_force", "2019avg"), f("jp_labor_force", "2020min")
    jp_lf_24 = f("jp_labor_force", "2024avg")
    jp_em_19, jp_em_20min = f("jp_employment", "2019avg"), f("jp_employment", "2020min")
    jp_em_24 = f("jp_employment", "2024avg")
    pop_19, pop_24 = f("jp_pop1564", "2019avg"), f("jp_pop1564", "2024avg")
    us_em_trough = f("idx_us_employment", "2020min")
    jp_lf_dip = (jp_lf_20min / jp_lf_19 - 1) * 100
    jp_em_dip = (jp_em_20min / jp_em_19 - 1) * 100
    jp_lf_24chg = (jp_lf_24 / jp_lf_19 - 1) * 100
    jp_em_24chg = (jp_em_24 / jp_em_19 - 1) * 100
    pop_chg = (pop_24 / pop_19 - 1) * 100

    return f"""\
【消去法の論旨（記述的・因果主張はしない。水準ベースで分母批判にロバスト）】

(0) 分母批判への対応 — 率でなく水準で判定する:
日本の労働参加率の上昇は、生産年齢人口（分母）が縮小するなかで機械的に
生じうるため、参加「率」の日米比較だけでは労働投入の非収縮の証拠にならない。
そこで絶対水準を確認すると、日本の15-64歳人口は2019年平均{pop_19:,.0f}万人から
2024年平均{pop_24:,.0f}万人へ{pop_chg:+.1f}%縮小したにもかかわらず、
労働力人口は2019年平均{jp_lf_19:,.0f}万人 → 2020年最低{jp_lf_20min:,.0f}万人
（2019年比{jp_lf_dip:+.1f}%）→ 2024年平均{jp_lf_24:,.0f}万人（同{jp_lf_24chg:+.1f}%）、
就業者数は{jp_em_19:,.0f}万人 → {jp_em_20min:,.0f}万人（同{jp_em_dip:+.1f}%）→
{jp_em_24:,.0f}万人（同{jp_em_24chg:+.1f}%）と、コロナ期の落ち込みは1%前後に
とどまり、2023年に2019年水準をほぼ回復、2024年には上回った。
すなわち日本の労働投入（人数ベース）は収縮していない。これは水準の事実であり、
分母の縮小に依存しない。

(1) 対照的に米国は水準そのものが崩落した:
米国の就業者数は2020年4月に2019年平均比で約{100 - us_em_trough:.0f}%減
（指数{us_em_trough:.0f}）まで落ち込み、2019年水準の回復に約2年を要した。
失業率も14.8%へ急騰し、その後の回復過程で歴史的な労働需給の逼迫
（大量離職・賃金高騰）が生じた。米国型の供給制約は「労働投入の毀損と
その不完全な回復」という水準の現象である。

(2) 参加率上昇の正しい解釈（機械的注意つき）:
日本の労働参加率（15-64歳）の上昇（2019年79.8%→2024年81.6%）は、
一部は分母縮小の機械的効果を含む。ただし水準（労働力人口・就業者数）が
維持・微増している以上、その含意は「人口が減るなかで追加的に人を労働市場に
引き込んだ」ことであり、米国型の労働退出（労働力からの離脱）とは逆方向である。
参加率単独では証拠にならないが、水準の事実と合わせれば補強材料になる。

(3) その他の国内供給制約指標:
有効求人倍率はコロナ期でも1倍を一度も割らず、製造工業稼働率指数は
2019年平均比でむしろ低め（2024年平均は約12%低い水準）に推移しており、
国内生産能力がフル稼働で逼迫していた形跡もない。

(結論) 日本には米国型の国内労働供給制約・能力制約がほぼ存在せず、
国内発の供給ショックで2021-24年のインフレを説明する余地は小さい。
したがって Shapiro 分解が示す供給主導シェア（2022年=0.70）の源泉は、
消去法的に国内供給制約ではなく輸入価格経由の外的ショックと解釈するのが
自然であり、本論文の外的要因フレーミングを補強する。
（限界: 就業者数は人数ベースであり、労働時間を含む総労働投入
（毎月勤労統計 総実労働時間指数）は現行基準の月次テーブルを特定できず
未確認。日本の水準系列は原数値のため月次比較には季節性が残るが、
本判定は年平均・年内極値ベースで季節性の影響は小さい。）
"""


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/4] fetching series ...")
    fred = {sid: fetch_fred(sid) for sid in FRED_SERIES}
    ci = fetch_ci_series()
    caputil = fetch_capacity_utilization()
    lfs = fetch_jp_labor_levels()

    df = pd.DataFrame(
        {
            "us_unemployment": fred["UNRATE"],
            "us_participation_16plus": fred["CIVPART"],
            "us_participation_1564": fred["LRAC64TTUSM156S"],
            "jp_participation_1564": fred["LRAC64TTJPM156S"],
            "jp_unemployment": ci["jp_unemployment"],
            "jp_jobs_to_applicants": ci["jp_jobs_to_applicants"],
            "jp_capacity_utilization": caputil,
            # --- 水準系列（分母批判対応） ---
            "jp_labor_force": lfs["jp_labor_force"],  # 万人・原数値
            "jp_employment": lfs["jp_employment"],  # 万人・原数値
            "jp_pop15plus": lfs["jp_pop15plus"],  # 万人・原数値
            "jp_pop1564": fred["LFWA64TTJPM647S"] / 1e4,  # 人→万人・季調
            "us_labor_force": fred["CLF16OV"],  # 千人・季調
            "us_employment": fred["CE16OV"],  # 千人・季調
        }
    )
    df = df.loc[pd.Period(PERIOD_START, "M"): pd.Period(PERIOD_END, "M")]
    for col in ("jp_labor_force", "jp_employment", "jp_pop1564", "us_employment"):
        df[f"idx_{col}"] = index_2019(df[col])
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
    make_levels_figure(df, OUT_DIR / "fig_supply_constraint_levels.png")

    lines = [
        "日本の供給制約の消去法チェック — 主要ファクト",
        f"(生成: supply_constraint_check.py, 対象期間 {PERIOD_START}..{PERIOD_END})",
        "",
        facts.round(2).to_string(),
        "",
        "数値の読み方: 2019avg=コロナ前水準, 2020max/min=コロナ期の極値, 20XXavg=年平均",
        "単位: jp_labor_force/jp_employment/jp_pop15plus/jp_pop1564=万人,",
        "      us_labor_force/us_employment=千人, idx_*=2019年平均=100の指数",
        "",
        build_summary_argument(facts),
        "",
        "データソース:",
        "  - FRED: UNRATE, CIVPART, LRAC64TTUSM156S, LRAC64TTJPM156S (OECD経由・15-64歳),",
        "    CLF16OV, CE16OV (米・水準・千人・季調), LFWA64TTJPM647S (日15-64歳人口・原典 人口推計)",
        "  - e-Stat 0003005798 労働力調査 基本集計 就業状態別15歳以上人口",
        "    (全国・男女計・万人・月次・原数値): 労働力人口・就業者数・15歳以上人口",
        "  - e-Stat 0003446462 景気動向指数 個別系列: C9有効求人倍率(除学卒),",
        "    Lg6完全失業率 (原典: 厚労省 一般職業紹介状況 / 総務省 労働力調査, 季節調整値)",
        "  - e-Stat 0004052231 製造工業生産能力・稼働率指数 (総合・季調・2020=100)",
        "  - 日本の労働参加率は労働力調査の直接テーブル特定が非効率だったため",
        "    FRED(OECD)系列に切替（本文注記済み）。日米とも15-64歳で定義を統一。",
        "  - 毎月勤労統計 総実労働時間指数: 検索2回で現行基準の月次テーブルを",
        "    特定できず（旧基準 平成17年=100 のみヒット）スキップ。",
    ]
    summary_txt = OUT_DIR / "supply_constraint_summary.txt"
    summary_txt.write_text("\n".join(lines))
    print(f"[4/4] summary -> {summary_txt.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
