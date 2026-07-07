"""
Shapiro supply/demand decomposition -- LAYER 2 (income-quintile, group-specific).

NOVEL contribution (DEC-016 層2): the same NATIONAL CPI price shock crossed with
each income quintile's OWN quantity response. Because the price P_i is national,
the price residual nu_p is COMMON to every quintile -- the only thing that varies
the supply/demand label across groups is the sign of the group's quantity
residual nu_q_g. So this measures DIFFERENTIAL CONSUMPTION RESPONSE, not
differential cost-push exposure:

  ✅  "Q1's response to common national price shocks is more contractionary /
       involuntary (supply-like); Q5 can maintain or expand (demand-like)."
  ❌  "Q1 faces more supply-driven / cost-push inflation."  (FALSE -- P is common.)

Position as the MECHANISM behind the Phase 2b backbone (Q1 faces a higher
effective-inflation gap, +2.01pp in 2022; calendar-year DEC-023): Q1 absorbs it by involuntarily cutting
quantity. Triangulation, not free-standing novelty.

EXPLORATORY by construction (DEC-016 pre-registration): annual data (2000-2024 =
25 points -> 24 YoY), quintile sub-samples are noisy. ONE spec only (demean-YoY
residualization; VAR cross-lags do NOT transfer to 24 obs). Headline statistic is
the supply share POOLED over shock years 2021-2024, per group (per-year quintile
labels are too noisy). Pre-registered hypothesis: Q1 supply-share > Q5. Quintiles
split the sample into fifths -> comparable noise across groups -> a Q1>Q5 gap is
not a sample-size artifact.
"""

import numpy as np
import pandas as pd

from src.data.estat_api import get_stats_data
from src.analysis.shapiro_decomp import (
    OUT_DIR, build_crosswalk, fetch_cpi_items,
)

QTY_TABLE = "0003348236"  # 五分位 数量（年次・2000-2024・二人以上）
EXP_TABLE = "0003348240"  # 五分位 金額（年次）= weights
QUINTILES = {"01": "Q1", "02": "Q2", "03": "Q3", "04": "Q4", "05": "Q5"}
SHOCK_YEARS = (2021, 2022, 2023, 2024)


def _annual_year(time_code) -> float:
    """Annual e-Stat time_code YYYY000000 -> year (NaN otherwise)."""
    s = str(time_code)
    if len(s) == 10 and s.endswith("000000"):
        return int(s[:4])
    return np.nan


def _fetch_quintile(table: str, codes: list[str], cache_name: str) -> pd.DataFrame:
    """Fetch annual quintile data (cat02=03, all quintiles) for matched items."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = OUT_DIR / cache_name
    if cache.exists():
        return pd.read_csv(cache, dtype={"cat01_code": str, "cat03_code": str})
    print(f"Fetching {table} for {len(codes)} items (all quintiles)...")
    parts = []
    for i in range(0, len(codes), 90):
        parts.append(get_stats_data(
            table, cdCat02="03", cdArea="00000",
            cdCat01=",".join(codes[i:i + 90]),
        ))
    df = pd.concat(parts, ignore_index=True)
    df.to_csv(cache, index=False)
    print(f"Saved {cache} ({len(df)} rows)")
    return df


def _national_cpi_annual(cpi_codes: list[str]) -> pd.DataFrame:
    """National CPI annual-average index per item -> [year, cpi_code, P]."""
    cpi = fetch_cpi_items(cpi_codes)
    cpi = cpi.rename(columns={"cat01_code": "cpi_code", "value": "P"})
    # monthly time_code YYYY00MMDD -> year; annual average
    cpi["year"] = cpi["time_code"].astype(str).str.slice(0, 4).astype(int)
    cpi = cpi[cpi["time_code"].astype(str).str.match(r"^\d{4}00\d{4}$")]  # monthly only
    return cpi.groupby(["year", "cpi_code"])["P"].mean().reset_index()


def build_quintile_panel() -> pd.DataFrame:
    """Annual panel [year, quintile, hh_code, cpi_code, P (national), Q_g]."""
    xwalk = build_crosswalk(save=False)
    matched = xwalk[xwalk["matched"]].copy()

    qty = _fetch_quintile(QTY_TABLE, matched["hh_code"].tolist(), "quintile_quantity.csv")
    qty = qty.rename(columns={"cat01_code": "hh_code", "value": "Q"})
    qty["year"] = qty["time_code"].map(_annual_year)
    qty = qty[qty["cat03_code"].isin(QUINTILES)].dropna(subset=["year"])
    qty["quintile"] = qty["cat03_code"].map(QUINTILES)
    qty = qty[["year", "quintile", "hh_code", "Q"]]

    cpi = _national_cpi_annual(matched["cpi_code"].tolist())

    panel = (
        matched[["hh_code", "hh_name", "cpi_code"]]
        .merge(qty, on="hh_code")
        .merge(cpi, on=["year", "cpi_code"])
        .sort_values(["quintile", "hh_code", "year"])
        .reset_index(drop=True)
    )
    return panel


def _demean_yoy(s: pd.Series) -> pd.Series:
    """YoY Δlog minus its own mean = minimal residualization (removes secular
    trend that would otherwise manufacture supply labels). Only spec at 24 obs."""
    d = np.log(s.where(s > 0)).diff()
    return d - d.mean()


def classify_quintile(panel: pd.DataFrame) -> pd.DataFrame:
    """Per (quintile, item, year) supply/demand label. nu_p is national (common
    to all quintiles); only nu_q is group-specific."""
    # national price residual -- computed ONCE per item, shared across quintiles
    cpi = panel[["year", "hh_code", "P"]].drop_duplicates()
    nup = []
    for code, g in cpi.groupby("hh_code"):
        g = g.sort_values("year")
        nup.append(pd.DataFrame({"year": g["year"], "hh_code": code,
                                 "nu_p": _demean_yoy(g["P"]).values}))
    nup = pd.concat(nup, ignore_index=True)

    # group-specific quantity residual
    parts = []
    for (q, code), g in panel.groupby(["quintile", "hh_code"]):
        g = g.sort_values("year")
        parts.append(pd.DataFrame({"year": g["year"], "quintile": q, "hh_code": code,
                                   "nu_q": _demean_yoy(g["Q"]).values}))
    nuq = pd.concat(parts, ignore_index=True)

    r = nuq.merge(nup, on=["year", "hh_code"]).dropna(subset=["nu_p", "nu_q"])
    r["label"] = np.where(np.sign(r["nu_p"]) * np.sign(r["nu_q"]) < 0, "supply", "demand")
    return r


def run(save: bool = True) -> pd.DataFrame:
    panel = build_quintile_panel()
    print(f"Quintile panel: {panel['hh_code'].nunique()} items x "
          f"{panel['year'].nunique()} years x {panel['quintile'].nunique()} groups")

    labels = classify_quintile(panel)

    # GATE (pre-registered): nu_p must be identical across quintiles.
    piv = labels.pivot_table(index=["year", "hh_code"], columns="quintile",
                             values="nu_p", aggfunc="first")
    spread = piv.max(axis=1) - piv.min(axis=1)
    assert spread.abs().max() < 1e-9, "nu_p differs across quintiles -- group Q leaked into price residual!"
    print("GATE OK: nu_p is common across all quintiles (national price).")

    # weights: group-specific expenditure share (fixed, 2015-24 mean)
    xwalk = build_crosswalk(save=False)
    matched = xwalk[xwalk["matched"]]
    exp = _fetch_quintile(EXP_TABLE, matched["hh_code"].tolist(), "quintile_expenditure.csv")
    exp = exp.rename(columns={"cat01_code": "hh_code", "value": "E"})
    exp["year"] = exp["time_code"].map(_annual_year)
    exp = exp[exp["cat03_code"].isin(QUINTILES) & (exp["year"] >= 2015)].dropna(subset=["year"])
    exp["quintile"] = exp["cat03_code"].map(QUINTILES)
    w = exp.groupby(["quintile", "hh_code"])["E"].mean().reset_index().rename(columns={"E": "w"})

    # headline: supply share pooled over shock years, per group
    shock = labels[labels["year"].isin(SHOCK_YEARS)].merge(w, on=["quintile", "hh_code"], how="left")
    shock["w"] = shock["w"].fillna(shock["w"].median())
    shock["is_supply"] = (shock["label"] == "supply").astype(float)
    pooled = shock.groupby("quintile").apply(
        lambda d: pd.Series({
            "supply_share": np.average(d["is_supply"], weights=d["w"]),
            "n_obs": len(d),
        }), include_groups=False
    )
    if save:
        labels.to_csv(OUT_DIR / "quintile_labels.csv", index=False)
        pooled.to_csv(OUT_DIR / "quintile_supply_share.csv")

    print("\n=== Layer-2 group-specific supply share (POOLED 2021-2024, exploratory) ===")
    print("Pre-registered hypothesis: Q1 > Q5 (more contractionary/involuntary response)")
    for q in ["Q1", "Q2", "Q3", "Q4", "Q5"]:
        if q in pooled.index:
            print(f"  {q}: supply_share={pooled.loc[q, 'supply_share']:.3f}  (n={int(pooled.loc[q, 'n_obs'])})")
    gap = pooled.loc["Q1", "supply_share"] - pooled.loc["Q5", "supply_share"]
    print(f"  Q1 - Q5 pooled gap = {gap:+.3f}  (cross-quintile pattern non-monotonic: Q2 highest)")

    # Per-year Q1-vs-Q5: the pooled sign is NOT robust if it flips across shock years.
    print("\nPer-year Q1 vs Q5 (unweighted supply fraction) -- robustness of direction:")
    shock["is_supply"] = (shock["label"] == "supply").astype(float)
    n_hold = 0
    for y in SHOCK_YEARS:
        s = shock[shock["year"] == y].groupby("quintile")["is_supply"].mean()
        hold = s.get("Q1", np.nan) > s.get("Q5", np.nan)
        n_hold += int(hold)
        print(f"  {y}: Q1={s.get('Q1', float('nan')):.2f} Q5={s.get('Q5', float('nan')):.2f}  Q1>Q5={hold}")
    print(f"\nVERDICT: Q1>Q5 holds in only {n_hold}/4 shock years (fails 2022-2023, the core "
          "cost-push years) -> hypothesis NOT robustly supported. Pooled positive is driven "
          "by 2021+2024. Honest read: INCONCLUSIVE at annual quintile resolution.")
    print("This does NOT undermine Phase 2b (effective-inflation gap is weight-based, robust); "
          "layer 2 probes a different margin (quantity response) the coarse annual data can't resolve.")
    return pooled


if __name__ == "__main__":
    run()
