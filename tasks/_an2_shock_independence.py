"""
案2 feasibility load-bearing test: does extending the sample period actually
add *independent* import-price shocks, or just more (co-moving) observations?

Premise of 案2 (todo / design-review A-3): identification is weak because the
2021-24 surge is effectively ONE shock. Extending to ~2005-08 is only worth the
3x IO-table rebuild IF the added years bring shocks that are independent across
the 5 groups (energy/metals/chemicals/food/wood).

TWO axes matter, for TWO different estimands (AKM eff#shocks ~= pr_group x pr_time,
multiplicative under a separable/Kronecker shock covariance):

  (1) CROSS-GROUP (pr_group): can we separate beta_g across the 5 groups?
      -> participation ratio of the 5x5 covariance of annual log-changes.
      This is the test for the A-4 GROUP-SPECIFIC (heterogeneity) rationale.
  (2) TEMPORAL (pr_time): how many INDEPENDENT shock EPISODES over time?
      -> inverse-Herfindahl of squared annual innovations of the aggregate
      exposure-weighted shifter, + sign-run episode count.
      This is the test for the POOLED single-beta (headline beta=0.431),
      identified off IC_c x aggregate P_t. 案2's literal premise ("独立ショック
      事象 ~1->~3-4") lives on THIS axis, not the cross-group one.

Data: data/raw/boj-cgpi/cgpilink1.csv (BOJ long-term linked CGPI, shift_jis,
1960- monthly, 2020-base) spliced with import_prices_extracted.csv (2020-base,
yen-basis, 2015-2024). Splice overlap diff verified ~0.

Verdict (2026-05-31, after advisor catch): the two estimands SPLIT.
  - GROUP-SPECIFIC beta_g: groups co-move (pr_group ~1.3-1.5 even over 1977-2019);
    collinearity is fatal and time does NOT fix it -> heterogeneity path killed.
  - POOLED beta: temporal episodes DO multiply with period extension --
    pr_time 1.88 (2021-24) -> 6.35 (2006-24). 案2's premise HOLDS for pooled beta.
    Data does NOT refute 案2; the rejection (if any) is a cost/risk CHOICE
    (beta-stability across breaks, A-1 confound, data effort), not a refutation.
Definitive test (cheap, no IO rebuild): extend CPI-by-category to ~2005 with
constant 2020 IC, re-run AKM, read p directly. See design-review A-5 / DEC-013.
"""
import pandas as pd
import numpy as np

LINK = "data/raw/boj-cgpi/cgpilink1.csv"
RECENT = "data/raw/boj-cgpi/import_prices_extracted.csv"
GROUPS = ["energy", "metals", "chemicals", "food", "wood"]
# cgpilink1 row indices (0-based) by basis
YEN = {"food": 60, "metals": 62, "wood": 63, "energy": 64, "chemicals": 65}
CONTRACT = {"food": 49, "metals": 51, "wood": 52, "energy": 53, "chemicals": 54}


def _load_link():
    link = pd.read_csv(LINK, header=None, low_memory=False, encoding="shift_jis")
    months = link.iloc[0, 3:].astype(float).astype(int).values
    idx = pd.to_datetime([f"{m // 100}-{m % 100:02d}-01" for m in months])
    return link, idx


def _series(link, idx, r):
    return pd.Series(pd.to_numeric(link.iloc[r, 3:], errors="coerce").values, index=idx)


def _diag(d, label):
    """Cross-group axis: participation ratio of the 5x5 covariance (pr_group)."""
    C = d.corr()
    X = (d - d.mean()) / d.std()
    ev = np.linalg.eigvalsh(np.cov(X.T))[::-1]
    off = C.values[np.triu_indices(len(d.columns), 1)]
    pc1 = ev[0] / ev.sum()
    eff = ev.sum() ** 2 / (ev ** 2).sum()
    print(f"=== {label} (n={len(d)}) mean|corr|={np.abs(off).mean():.3f} "
          f"meancorr={off.mean():.3f} PC1={pc1:.3f} pr_group={eff:.2f}")
    return eff


def _temporal(x, label):
    """Temporal axis: independent shock EPISODES of the aggregate shifter (pr_time)."""
    x = x.dropna().values
    pr = (x ** 2).sum() ** 2 / (x ** 4).sum()      # inverse-Herfindahl of innovations
    runs = 1 + (np.diff(np.sign(x)) != 0).sum()    # sign-run episode count
    print(f"--- {label} (n={len(x)}) pr_time(invHerf)={pr:.2f} sign-run episodes={runs}")
    return pr


def main():
    link, idx = _load_link()

    # yen-basis spliced (link <2020-01 + recent >=2020-01), 2020-base both
    yen = pd.DataFrame({g: _series(link, idx, r) for g, r in YEN.items()})
    yen = yen[yen.index <= "2019-12-01"]
    rec = pd.read_csv(RECENT, parse_dates=["date"])
    rec = rec[rec.group.isin(GROUPS)].pivot(index="date", columns="group", values="value")
    ov = yen.index.intersection(rec.index)
    assert (yen.loc[ov] - rec.loc[ov]).abs().mean().max() < 1e-6, "splice mismatch"
    spliced = pd.concat([yen[yen.index < "2020-01-01"], rec[rec.index >= "2020-01-01"]])
    spliced = spliced.sort_index()[GROUPS]
    a = spliced.resample("YE").mean(); a.index = a.index.year
    dln = np.log(a).diff().dropna()

    print("\n### AXIS 1: CROSS-GROUP (identifies group-specific beta_g; A-4 heterogeneity)")
    print("--- YEN-BASIS (current design) ---")
    g_short = _diag(dln.loc[2021:2024], "2021-2024 current window")
    g_ext = _diag(dln.loc[2006:2024], "2006-2024 extended window")
    # contract-currency basis (案1; link only, 1976-2019)
    cc = pd.DataFrame({g: _series(link, idx, r) for g, r in CONTRACT.items()})
    cc = cc[(cc.index >= "1976-01-01") & (cc.index <= "2019-12-01")][GROUPS]
    ca = cc.resample("YE").mean(); ca.index = ca.index.year
    cdln = np.log(ca).diff().dropna()
    print("--- CONTRACT-CURRENCY (案1, strips common yen factor) ---")
    _diag(cdln.loc[2007:2019], "2007-2019 realistic window")
    _diag(cdln.loc[1977:2019], "1977-2019 full (infeasible on IO/HH/CPI side)")
    print(">> verdict: groups co-move; group-specific beta_g NOT separable; time does not help.")

    # AXIS 2: temporal episodes of the aggregate exposure-weighted shifter
    ic = pd.read_csv("data/processed/import-content/mid_category_ic_by_group.csv")
    w = np.array([ic[f"ic_{g}"].mean() for g in GROUPS]); w = w / w.sum()
    aggchg = (dln[GROUPS] * w).sum(axis=1)
    print("\n### AXIS 2: TEMPORAL (identifies POOLED beta; 案2's actual premise)")
    pt_short = _temporal(aggchg.loc[2021:2024], "2021-2024 current window")
    pt_ext = _temporal(aggchg.loc[2006:2024], "2006-2024 extended window")
    print(f">> Kronecker eff#shocks ~ pr_group x pr_time:")
    print(f"   2021-24: {g_short:.2f} x {pt_short:.2f} = {g_short*pt_short:.2f}    "
          f"2006-24: {g_ext:.2f} x {pt_ext:.2f} = {g_ext*pt_ext:.2f}")
    print(f">> verdict: temporal episodes multiply with extension -> pooled beta identification")
    print(f"   DOES improve (pr_time {pt_short:.2f}->{pt_ext:.2f}). 案2 premise holds; not refuted.")
    print("\nannual Dln aggregate shifter 2006-2024 (episodes visible):")
    print(aggchg.loc[2006:2024].round(3).to_string())


if __name__ == "__main__":
    main()
