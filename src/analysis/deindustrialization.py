"""
探索: 産業空洞化とインフレの質（コストプッシュ比率）の時系列分析。

仮説: 第二次産業（製造業）の弱体化＝空洞化が進むほど、インフレに占める
      コストプッシュ（供給主導）比率が上昇する。

被説明変数(DV): Shapiro(2022)型 供給主導シェア（data/processed/shapiro/）を年次化。
説明変数(IV): 製造業付加価値シェア(World Bank NV.IND.MANF.ZS)、
             産業就業シェア(WB SL.IND.EMPL.ZS) ほか（海外生産比率は別途付加）。

注: これは探索フェーズの first-pass。識別の主リスク=共通トレンドによる
    spurious 相関。階差・トレンド除去・コントロールで頑健性を確認する。
"""

from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SHAPIRO = ROOT / "data" / "processed" / "shapiro"
WB_RAW = ROOT / "data" / "raw" / "industry-structure"
OUT = ROOT / "data" / "processed" / "deindustrialization"
OUT.mkdir(parents=True, exist_ok=True)

SPECS = ["VAR_lag12", "VAR_lag3", "AR_lag12", "AR_lag3", "primary"]


def annual_supply_share(spec: str) -> pd.DataFrame:
    """月次 supply_infl/total_infl を年次集約。

    年次シェア = Σ supply_infl / Σ total_infl（年内累積寄与の比）。
    月次 supply_share の単純平均は total_infl≈0 の月で発散するため使わない。
    """
    df = pd.read_csv(SHAPIRO / f"supply_share_{spec}.csv", parse_dates=["date"])
    df["year"] = df["date"].dt.year
    g = df.groupby("year").agg(
        supply_infl=("supply_infl", "sum"),
        total_infl=("total_infl", "sum"),
        n_months=("date", "count"),
    )
    g = g[g["n_months"] == 12]  # 完全な年のみ
    g[f"css_{spec}"] = g["supply_infl"] / g["total_infl"] * 100  # cost-push share %
    return g[[f"css_{spec}"]]


def fetch_worldbank(indicator: str, col: str) -> pd.DataFrame:
    """World Bank 指標をローカル JSON（curl 取得済み）から読む。"""
    data = json.loads((WB_RAW / f"wb_{indicator}.json").read_text())
    rows = [
        {"year": int(d["date"]), col: d["value"]}
        for d in data[1]
        if d["value"] is not None
    ]
    return pd.DataFrame(rows).set_index("year").sort_index()


def build() -> pd.DataFrame:
    dv = pd.concat([annual_supply_share(s) for s in SPECS], axis=1)

    wb = pd.concat(
        [
            fetch_worldbank("NV.IND.MANF.ZS", "mfg_va_share"),    # 製造業付加価値%GDP
            fetch_worldbank("SL.IND.EMPL.ZS", "ind_empl_share"),  # 産業就業%
            fetch_worldbank("NE.IMP.GNFS.ZS", "imports_gdp"),     # 輸入%GDP(開放度control)
        ],
        axis=1,
    )

    df = dv.join(wb, how="left")
    df.to_csv(OUT / "annual_panel.csv")
    return df


if __name__ == "__main__":
    df = build()
    pd.set_option("display.width", 140)
    pd.set_option("display.max_columns", 20)
    print("=== annual panel (DV=cost-push share %, IV=WB) ===")
    print(df.round(2).to_string())
    print("\n=== 変動量チェック (窓内 min-max) ===")
    win = df.loc[2001:2024]
    for c in ["css_VAR_lag12", "mfg_va_share", "ind_empl_share", "imports_gdp"]:
        if c in win:
            s = win[c].dropna()
            print(f"{c:18s}: min={s.min():.2f} max={s.max():.2f} 幅={s.max()-s.min():.2f}")
