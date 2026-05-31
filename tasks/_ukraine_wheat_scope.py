"""ウクライナ自然実験（小麦コストプッシュ）の feasibility scoping。

問い: 2022/2 のウクライナ侵攻を鋭い外生的供給ショックとして、小麦集約的な食料品目
（食パン・うどん・スパゲッティ・小麦粉）を treatment、米（うるち米）を control とする
DiD/event-study で cost-push 転嫁の clean な LATE が取れるか。
make-or-break = advisor 指摘の「energy 交絡」（小麦品目が同時にエネルギー集約的だと
侵攻後の上昇を小麦に帰属できない）。

手順:
1. mid-cat IC（mid_category_ic_by_group.csv）の ic_energy は食料内でほぼフラット
   (0.0022-0.0033) ＝ mid-cat 粒度では小麦/エネルギーの差を識別不能 → 品目レベル必須。
2. 品目別CPI（e-Stat 0003427113・tab=1・月次）で小麦品目 vs 米 vs エネルギーの
   2022/2前後の path を比較。2022-01=100 で正規化。

scoping verdict (2026-05-31):
- 小麦品目は侵攻後に一斉に +10〜22%・持続。米はほぼフラット(クリーン control)。
- エネルギーは別軌道（電気代は2023に補助で急落・ガソリンは補助で横ばい）＝
  小麦の上昇はエネルギーと連動しない → **energy 交絡は管理可能**（make-or-break クリア）。
- → 自然実験は集計 shift-share より clean で feasible。残課題は (a) 米 control の
  妥当性（米は独自の需給・政策・2024令和の米騒動）、(b) 円安も小麦を押上げ（ただし
  これは import cost-push そのもので識別対象として可）、(c) treated 品目数が少ない。
- 推奨: 品目別の輸入小麦集約度を連続 treatment 化＋複数 control＋energy 集約度を統制。
"""
import pandas as pd
from src.data.estat_api import get_stats_data

CPI_TABLE = "0003427113"
ITEMS = {
    "1021": "食パン", "1031": "ゆでうどん", "1042": "スパゲッティ", "1071": "小麦粉",
    "1001": "うるち米A", "3701": "灯油", "7301": "ガソリン", "3500": "電気代",
}
WHEAT = ["食パン", "ゆでうどん", "スパゲッティ", "小麦粉"]
CONTROL = ["うるち米A"]
ENERGY = ["灯油", "ガソリン", "電気代"]


def fetch_item_cpi(t_from="202101", t_to="202312"):
    # NB: this table's range query is sensitive to the start; 202101 returns 2022-01 onward reliably.
    df = get_stats_data(CPI_TABLE, cdArea="00000", cdCat01=",".join(ITEMS), cdTimeFrom=t_from, cdTimeTo=t_to)
    df["tab"] = df.tab_code.astype(str)
    df["s"] = df.time_code.astype(str)
    # monthly rows: YYYY00MMMM (s[4:6]=='00', month duplicated in s[6:10]); exclude annual (s[6:]=='0000')
    mon = df[(df.tab == "1") & (df.s.str.len() == 10) & (df.s.str[4:6] == "00") & (df.s.str[6:] != "0000")].copy()
    mon["ym"] = mon.s.str[:4] + "-" + mon.s.str[6:8]
    mon["code"] = mon.cat01_code.astype(str).str.zfill(4)
    # guard against 速報/確報 duplicates: average within (ym,code)
    piv = mon.pivot_table(index="ym", columns="code", values="value", aggfunc="mean").sort_index()
    piv.columns = [ITEMS.get(c, c) for c in piv.columns]
    return piv


def main():
    ic = pd.read_csv("data/processed/import-content/mid_category_ic_by_group.csv")
    food = ic[ic.group == "food"]
    print("1. mid-cat ic_energy(食料内)範囲: %.4f〜%.4f ＝ ほぼフラット → mid-cat 粒度では識別不能、品目レベル必須"
          % (food.ic_energy.min(), food.ic_energy.max()))

    piv = fetch_item_cpi()
    base = "2022-01" if "2022-01" in piv.index else piv.index[0]
    idx = piv / piv.loc[base] * 100  # ウクライナ(2022/2)直前を100
    order = [c for c in WHEAT + CONTROL + ENERGY if c in idx.columns]
    rows = [r for r in ["2022-01", "2022-03", "2022-06", "2022-12", "2023-06", "2023-12"] if r in idx.index]
    print(f"\n2. 品目別CPI（{base}=100、ウクライナ=2022/2）:")
    print(idx.loc[rows, order].round(1).to_string())

    w = idx[WHEAT].mean(axis=1)
    c = idx[CONTROL].mean(axis=1)
    for mth in ["2022-12", "2023-12"]:
        if mth in idx.index:
            print(f"\n3. 小麦平均 vs 米（DiD の素・{mth}）: 小麦={w.loc[mth]:.1f} / 米={c.loc[mth]:.1f} "
                  f"→ 差={w.loc[mth]-c.loc[mth]:.1f}pp")
    print("   エネルギーは別軌道（電気代2023急落=補助）→ energy 交絡は管理可能＝自然実験 feasible。")


if __name__ == "__main__":
    main()
