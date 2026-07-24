"""
勤労者世帯の五分位別・実質実収入チェック（ユーザー指摘 2026-07-24: 名目/実質の確認）。

背景:
  quintile_impact.compute_quintile_real_income_change は名前に反して名目所得を
  使っておらず（実効インフレ gap の pivot のみ）、実質所得の五分位比較は未計算だった。
  本スクリプトが初めて名目実収入を突き合わせる。

設計:
  - 母集団: 勤労者世帯 (cat02=4)。家計調査の実収入(cat01=19)は二人以上世帯全体
    (cat02=3) には収録されないため。負担系列(柱③・cat02=3)とは母集団・分位の
    ランキングが異なる点に注意（無職・年金世帯を含まない）。
  - 名目: 実収入の 2015-19 平均比 %（暦年）
  - 実効インフレ: cat02=4 の 2019年固定シェア × cpi_change_vs_baseline（柱③と同式）
  - 実質 = 名目% − 実効インフレpt

出力: data/processed/did/real_income_worker.csv
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed" / "did"

MAJOR_CODES = [60, 102, 107, 112, 122, 140, 145, 152, 156, 165]
TOTAL_CONS_CODE = 59
INCOME_CODE = 19  # 実収入
WORKER = 4        # 勤労者世帯


def main() -> pd.DataFrame:
    hh = pd.read_csv(DATA_RAW / "household-survey" / "household_quintile_2015_2025.csv")
    hh["year"] = hh["time_code"].astype(str).str[:4].astype(int)
    w = hh[hh["cat02_code"] == WORKER]

    # 名目実収入: 2015-19 平均比 %
    inc = w[(w["cat01_code"] == INCOME_CODE) & (w["cat03_code"].between(1, 5))].pivot_table(
        index="year", columns="cat03_code", values="value"
    )
    nom = (inc / inc.loc[2015:2019].mean() - 1) * 100

    # 実効インフレ: 勤労者世帯 2019 年固定シェア（柱③と同じ恒等式・母集団のみ違う）
    y19 = w[w["year"] == 2019]
    tot = y19[y19["cat01_code"] == TOTAL_CONS_CODE].set_index("cat03_code")["value"]
    shares = {
        q: {
            c: float(
                y19[(y19["cat01_code"] == c) & (y19["cat03_code"] == q)]["value"].iloc[0]
            )
            / float(tot[q])
            for c in MAJOR_CODES
        }
        for q in range(1, 6)
    }
    cpi = pd.read_csv(ROOT / "data" / "processed" / "price-indices" / "cpi_changes.csv")

    rows = []
    for year in sorted(set(cpi["year"]) & set(nom.index)):
        yc = cpi[cpi["year"] == year].set_index("hh_cat_code")["cpi_change_vs_baseline"]
        for q in range(1, 6):
            eff = sum(shares[q][c] * yc.get(c, float("nan")) for c in MAJOR_CODES)
            rows.append(
                {
                    "year": year,
                    "quintile": q,
                    "nominal_income_pct": round(nom.loc[year, q], 2),
                    "effective_inflation_pp": round(eff, 2),
                    "real_income_pct": round(nom.loc[year, q] - eff, 2),
                }
            )
    out = pd.DataFrame(rows)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT_DIR / "real_income_worker.csv", index=False)

    piv = out.pivot(index="year", columns="quintile", values="real_income_pct")
    piv["real_gap_q1_q5"] = piv[1] - piv[5]
    print(piv.round(2).to_string())
    return out


if __name__ == "__main__":
    main()
