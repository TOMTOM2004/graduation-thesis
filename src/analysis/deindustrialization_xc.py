"""
探索(クロスカントリー版): 産業空洞化と2022交易損失の関係。

仮説: 製造業が強い国ほど、2022年の輸入価格ショックによる交易損失
      （実質所得の海外流出）が小さい。

DV : 2022 交易損失 income effect (% GDP)
     = -Δln(交易条件) × (貿易/GDP)/2 × 100   ※正=流出(損失)
IV : 製造業付加価値シェア (% GDP, WB NV.IND.MANF.ZS)
control: 燃料輸入シェア(エネルギー依存=2022最大の交絡), 開放度, 1人当GDP

データ: World Bank（data/raw/crosscountry/*.json, curl取得済み）
単一国時系列(share DV)が分母≈0で不成立だったためのフォールバック（DEC-IDEA-01）。
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "crosscountry"
OUT = ROOT / "data" / "processed" / "deindustrialization"
OUT.mkdir(parents=True, exist_ok=True)

KEYS = ["tot", "trade", "mfgva", "fuelimp", "eimp", "gdppc", "cpi"]


def load(key: str) -> pd.DataFrame:
    data = json.loads((RAW / f"{key}.json").read_text(encoding="utf-8-sig"))
    rows = [
        {"iso": d["countryiso3code"], "country": d["country"]["value"],
         "year": int(d["date"]), key: d["value"]}
        for d in data[1] if d["value"] is not None
    ]
    return pd.DataFrame(rows)


def wide(key: str) -> pd.DataFrame:
    df = load(key)
    return df.pivot_table(index="iso", columns="year", values=key)


def latest_le(w: pd.DataFrame, year: int) -> pd.Series:
    """year 以前で最新の非欠損値（遅い変数の補完）。"""
    cols = [c for c in w.columns if c <= year]
    return w[cols].ffill(axis=1)[max(cols)]


def build() -> pd.DataFrame:
    tot = wide("tot")
    trade = wide("trade")
    names = load("tot")[["iso", "country"]].drop_duplicates().set_index("iso")["country"]

    # DV: 2022 交易損失 income effect (% GDP)
    dln_tot = np.log(tot[2022]) - np.log(tot[2021])
    trade_w = trade[2021] / 100.0 / 2.0          # (X+M)/GDP の半分
    tot_loss = -dln_tot * trade_w * 100          # 正=所得流出(損失)

    df = pd.DataFrame({
        "country": names,
        "tot_loss_2022": tot_loss,
        "dln_tot": dln_tot * 100,
        "mfgva": latest_le(wide("mfgva"), 2022),
        "fuelimp": latest_le(wide("fuelimp"), 2022),
        "eimp": latest_le(wide("eimp"), 2022),
        "openness": trade[2021],
        "gdppc": latest_le(wide("gdppc"), 2022),
        "cpi_2022": wide("cpi")[2022],
    })
    df["ln_gdppc"] = np.log(df["gdppc"])
    df.to_csv(OUT / "xc_2022.csv")
    return df


def regress(df, y, xs, label):
    d = df[[y] + xs].dropna()
    X = sm.add_constant(d[xs])
    m = sm.OLS(d[y], X).fit(cov_type="HC1")
    print(f"\n### {label}  (N={int(m.nobs)}, R2={m.rsquared:.3f})")
    for name in m.params.index:
        print(f"  {name:12s} b={m.params[name]:8.4f}  se={m.bse[name]:7.4f}  "
              f"p={m.pvalues[name]:.3f}")
    return m


if __name__ == "__main__":
    df = build()
    pd.set_option("display.width", 160); pd.set_option("display.max_columns", 20)
    print("=== cross-country 2022 dataset ===")
    print(df.sort_values("tot_loss_2022", ascending=False)
            .round(2).to_string())

    print("\n=== 単相関 ===")
    print(df[["tot_loss_2022", "mfgva", "fuelimp", "eimp", "openness",
              "ln_gdppc", "cpi_2022"]].corr()["tot_loss_2022"].round(3).to_string())

    regress(df, "tot_loss_2022", ["mfgva"], "M1: 単回帰 損失~製造業シェア")
    regress(df, "tot_loss_2022", ["mfgva", "fuelimp"],
            "M2: +燃料輸入シェア(エネ依存control)")
    regress(df, "tot_loss_2022", ["mfgva", "fuelimp", "openness", "ln_gdppc"],
            "M3: フルコントロール")
    regress(df, "cpi_2022", ["mfgva", "fuelimp", "ln_gdppc"],
            "M4(参考): 2022CPIインフレ~製造業シェア")
