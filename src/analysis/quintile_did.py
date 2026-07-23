"""
ITEM-021: 五分位 × 費目曝露 DiD の実現可能性調査（ゼミ指摘の検証）。

設計（exposure event-study / DiD）:
  クロスセクション = CPI中分類レベルの費目 c（輸入含有率 IC_c で連続曝露を測る）
  時間 = 暦年 t（2015-2024, DEC-023）
  群 = 所得五分位 q（Q1 vs Q5）

  (A) 価格伝播 event-study（識別改善テスト・DEC-013/015 との比較対象）:
        Δlog CPI_{c,t} = α_t + β_t · IC_c + ε_{c,t}   （年ごとのクロスセクション回帰）
      プレ期(2016-2020)の β_t ≈ 0 かつショック期(2022-)の β_t > 0 なら、
      時系列β(0.373)と独立の設計でコストプッシュ伝播を支持する証拠。
      推論は cluster(category) と IC ラベルの permutation（N が小さいため）。

  (B) 支出シェア triple-diff（行動込み帰着・恒等式との差分）:
        s_{q,c,t} = γ_{c,q} + λ_{q,t} + Σ_t δ_t·(IC_c×D_t) + Σ_t θ_t·(IC_c×D_t×Q1_q) + ε
      θ_t: 高曝露費目のシェアが Q1 で Q5 より大きく動いたか（event-study, base 2021）。
      恒等式（柱③）はシェア固定の機械的帰着、こちらは行動反応込みの実現値。

注意（DEC-013/015 整合）:
  独立マクロショックは実質1つ。β_t の解釈は「輸入曝露と価格上昇の
  クロスセクション相関」であり、"因果的に識別" とは書かない。
"""

from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
BRIDGE_DIR = ROOT / "data" / "processed" / "bridge-matrix"
OUT_DIR = ROOT / "data" / "processed" / "did"

BASE_YEAR = 2021  # event-study 基準年（ショック直前）
POST_YEARS = [2022, 2023, 2024]
PRE_TEST_YEARS = [2016, 2017, 2018, 2019, 2020]  # プレトレンド検定対象

# 家計調査（用途分類・年間収入五分位）cat01_code → CPI中分類名の対応。
# 同名一致を基本とし、複合のみ合算（衣料・医薬品系）。近似一致は flag。
HH_TO_CPI_MID: dict[str, dict] = {
    "穀類": {"hh": [61]}, "魚介類": {"hh": [66]}, "肉類": {"hh": [71]},
    "乳卵類": {"hh": [74]}, "野菜・海藻": {"hh": [78]}, "果物": {"hh": [83]},
    "油脂・調味料": {"hh": [86]}, "菓子類": {"hh": [89]}, "調理食品": {"hh": [90]},
    "飲料": {"hh": [93]}, "酒類": {"hh": [97]}, "外食": {"hh": [98]},
    "家賃": {"hh": [103], "approx": "HH=家賃地代（地代含む）"},
    "設備修繕・維持": {"hh": [104]},
    "電気代": {"hh": [108]}, "ガス代": {"hh": [109]}, "他の光熱": {"hh": [110]},
    "上下水道料": {"hh": [111]},
    "家庭用耐久財": {"hh": [113]},
    "室内装備品": {"hh": [117], "approx": "HH=室内装備・装飾品"},
    "家事用消耗品": {"hh": [120]}, "家事サービス": {"hh": [121]},
    "衣料": {"hh": [123, 124, 128, 132, 136, 137], "approx": "和服+洋服+シャツ類+下着類+生地+他の被服の合算"},
    "履物類": {"hh": [138]}, "被服関連サービス": {"hh": [139]},
    "医薬品・健康保持用摂取品": {"hh": [141, 142], "approx": "医薬品+健康保持用摂取品の合算"},
    "保健医療用品・器具": {"hh": [143]}, "保健医療サービス": {"hh": [144]},
    "交通": {"hh": [146]}, "自動車等関係費": {"hh": [147]}, "通信": {"hh": [151]},
    "授業料等": {"hh": [153]}, "教科書・学習参考教材": {"hh": [154]}, "補習教育": {"hh": [155]},
    "教養娯楽用耐久財": {"hh": [157]}, "教養娯楽用品": {"hh": [158]},
    "書籍・他の印刷物": {"hh": [159]}, "教養娯楽サービス": {"hh": [160]},
    "パック旅行費": {"hh": [162]}, "理美容サービス": {"hh": [167]},
    # 放送受信料: 家計調査側に単独項目がなく対応不能のため除外
}

TOTAL_CONS_CODE = 59  # 消費支出
HOUSEHOLD_TYPE = 3    # 二人以上の世帯（DEC-011: universe 固定）


def load_cpi_mid_annual() -> pd.DataFrame:
    """CPI中分類の暦年平均指数（DEC-023: 月次のみ選択して暦年平均）。"""
    cpi = pd.read_csv(DATA_RAW / "cpi" / "cpi_category_2015_2025.csv")
    tc = cpi["time_code"].astype(str)
    mm = [f"{i:02d}" for i in range(1, 13)]
    monthly = cpi[tc.str[8:10].isin(mm) & tc.str[6:8].isin(mm)].copy()
    monthly["year"] = monthly["time_code"].astype(str).str[:4].astype(int)
    monthly["name_clean"] = (
        monthly["cat01_name"].astype(str).str.replace(r"^\d+\s*", "", regex=True)
    )
    target = set(HH_TO_CPI_MID.keys())
    sel = monthly[monthly["name_clean"].isin(target)].copy()
    # 同名複数コード（例: 電気代=中分類56と品目3500）は IC 側の cpi_code（中分類）で解決
    ic_codes = (
        pd.read_csv(BRIDGE_DIR / "mid_category_import_content.csv")
        .set_index("cpi_mid_name")["cpi_code"]
        .astype(int)
        .to_dict()
    )
    dup_names = sel.groupby("name_clean")["cat01_code"].nunique()
    for name in dup_names[dup_names > 1].index:
        keep = ic_codes.get(name)
        if keep is None:
            raise ValueError(f"CPI名の曖昧一致を解決できない: {name}")
        sel = sel[(sel["name_clean"] != name) | (sel["cat01_code"].astype(int) == keep)]
    dup = sel.groupby("name_clean")["cat01_code"].nunique()
    if (dup > 1).any():
        raise ValueError(f"CPI名の曖昧一致: {dup[dup > 1].index.tolist()}")
    annual = (
        sel.groupby(["name_clean", "year"])["value"].mean().rename("cpi_index").reset_index()
    )
    return annual


def load_quintile_shares_mid() -> pd.DataFrame:
    """五分位 × CPI中分類対応費目 × 年の支出シェア（対消費支出）。"""
    hh = pd.read_csv(DATA_RAW / "household-survey" / "household_quintile_2015_2024.csv")
    hh = hh[hh["cat02_code"] == HOUSEHOLD_TYPE].copy()
    hh["year"] = hh["time_code"].astype(str).str[:4].astype(int)

    total = (
        hh[hh["cat01_code"] == TOTAL_CONS_CODE]
        .set_index(["year", "cat03_code"])["value"]
        .rename("total_cons")
    )

    rows = []
    for cpi_name, spec in HH_TO_CPI_MID.items():
        sub = hh[hh["cat01_code"].isin(spec["hh"])]
        agg = sub.groupby(["year", "cat03_code"])["value"].sum().rename("spend")
        df = pd.concat([agg, total], axis=1, join="inner").reset_index()
        df["category"] = cpi_name
        df["share"] = df["spend"] / df["total_cons"]
        rows.append(df)
    out = pd.concat(rows, ignore_index=True)
    out = out.rename(columns={"cat03_code": "quintile"})
    return out[out["quintile"].between(1, 5)]


def build_panel() -> pd.DataFrame:
    """(category, quintile, year) パネル: share, Δlog CPI, IC。"""
    ic = pd.read_csv(BRIDGE_DIR / "mid_category_import_content.csv")
    ic = ic[ic["cpi_mid_name"].isin(HH_TO_CPI_MID.keys())][
        ["cpi_mid_name", "group", "import_content"]
    ].rename(columns={"cpi_mid_name": "category"})

    cpi = load_cpi_mid_annual().rename(columns={"name_clean": "category"})
    cpi = cpi.sort_values(["category", "year"])
    cpi["dlog_cpi"] = cpi.groupby("category")["cpi_index"].transform(
        lambda s: np.log(s) - np.log(s.shift(1))
    )

    shares = load_quintile_shares_mid()
    panel = shares.merge(cpi, on=["category", "year"], how="inner").merge(
        ic, on="category", how="inner"
    )
    missing = set(HH_TO_CPI_MID) - set(panel["category"].unique())
    if missing:
        print(f"Warning: パネルから欠落した費目: {missing}")
    return panel


# ---------------------------------------------------------------- (A) 価格伝播


def price_event_study(panel: pd.DataFrame, n_perm: int = 5000, seed: int = 21) -> pd.DataFrame:
    """
    年ごとのクロスセクション回帰 Δlog CPI_{c,t} = α_t + β_t·IC_c。
    permutation p は IC ラベルを費目間でシャッフルした帰無分布に対する両側 p 値。
    """
    cats = panel[["category", "import_content", "dlog_cpi", "year"]].drop_duplicates(
        ["category", "year"]
    )
    rng = np.random.default_rng(seed)
    rows = []
    for year in sorted(cats["year"].unique()):
        yr = cats[(cats["year"] == year)].dropna(subset=["dlog_cpi"])
        if len(yr) < 10:
            continue
        x = yr["import_content"].to_numpy()
        y = yr["dlog_cpi"].to_numpy() * 100  # pp
        beta = np.polyfit(x, y, 1)[0]
        # OLS (HC1)
        res = smf.ols("y ~ x", data=pd.DataFrame({"x": x, "y": y})).fit(cov_type="HC1")
        # permutation
        null = np.empty(n_perm)
        for i in range(n_perm):
            null[i] = np.polyfit(rng.permutation(x), y, 1)[0]
        p_perm = float((np.abs(null) >= abs(beta)).mean())
        rows.append(
            {
                "year": year,
                "n_categories": len(yr),
                "beta_pp_per_IC": round(beta, 3),
                "se_hc1": round(res.bse["x"], 3),
                "p_hc1": round(res.pvalues["x"], 4),
                "p_perm": round(p_perm, 4),
            }
        )
    return pd.DataFrame(rows)


# ------------------------------------------------------- (B) シェア triple-diff


def share_event_study(panel: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    s_{q,c,t}（Q1・Q5のみ）の event-study:
      share ~ C(category)*C(quintile) + C(year)*C(quintile)
              + IC×D_t + IC×D_t×Q1   （base year = 2021）
    戻り値: (係数表, プレトレンド joint F 検定結果)
    """
    df = panel[panel["quintile"].isin([1, 5])].copy()
    df["share_pp"] = df["share"] * 100
    df["q1"] = (df["quintile"] == 1).astype(int)
    df["ic"] = df["import_content"]
    df["yr"] = df["year"].astype(int)

    # 基準年を除く年ごとに ic×year, ic×year×q1 の明示的ダミー列を構成
    # （patsy の full-rank coding 回避のため formula 内 C() 交互作用は使わない）
    years = [y for y in sorted(df["yr"].unique()) if y != BASE_YEAR]
    d_cols, t_cols = [], []
    for y in years:
        d, t = f"ic_x_{y}", f"ic_x_{y}_q1"
        df[d] = df["ic"] * (df["yr"] == y)
        df[t] = df[d] * df["q1"]
        d_cols.append(d)
        t_cols.append(t)

    formula = "share_pp ~ C(category)*C(q1) + C(yr)*C(q1) + " + " + ".join(
        d_cols + t_cols
    )
    res = smf.ols(formula, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df["category"]}
    )

    rows = []
    for y in years:
        rows.append(
            {
                "year": y,
                "delta_ic_x_year_pp": round(res.params[f"ic_x_{y}"], 3),
                "delta_p": round(res.pvalues[f"ic_x_{y}"], 4),
                "theta_ic_x_year_x_q1_pp": round(res.params[f"ic_x_{y}_q1"], 3),
                "theta_p": round(res.pvalues[f"ic_x_{y}_q1"], 4),
            }
        )
    coefs = pd.DataFrame(rows)

    # プレトレンド joint 検定（θ_t, t<BASE_YEAR = 0）
    names = list(res.params.index)
    pre_terms = [f"ic_x_{y}_q1" for y in years if y < BASE_YEAR]
    R = np.zeros((len(pre_terms), len(names)))
    for i, term in enumerate(pre_terms):
        R[i, names.index(term)] = 1.0
    wtest = res.wald_test(R, use_f=True, scalar=True)
    pre = {"F": float(wtest.fvalue), "p": float(wtest.pvalue), "terms": len(pre_terms)}
    return coefs, pre


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = build_panel()
    print(
        f"パネル: {panel['category'].nunique()} 費目 × 5 分位 × "
        f"{panel['year'].nunique()} 年 = {len(panel)} 行"
    )
    panel.to_csv(OUT_DIR / "did_panel.csv", index=False)

    print("\n(A) 価格伝播 event-study（Δlog CPI on IC, 年別クロスセクション）")
    price = price_event_study(panel)
    print(price.to_string(index=False))
    price.to_csv(OUT_DIR / "price_event_study.csv", index=False)

    print("\n(B) 支出シェア triple-diff event-study（Q1 vs Q5, base 2021）")
    coefs, pre = share_event_study(panel)
    print(coefs.to_string(index=False))
    print(f"プレトレンド joint F({pre['terms']}): F={pre['F']:.2f}, p={pre['p']:.4f}")
    coefs.to_csv(OUT_DIR / "share_triple_diff.csv", index=False)
    pd.DataFrame([pre]).to_csv(OUT_DIR / "share_pretrend_test.csv", index=False)


if __name__ == "__main__":
    main()
