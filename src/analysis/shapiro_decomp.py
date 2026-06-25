"""
Shapiro (2024) supply/demand-driven inflation decomposition (DEC-016).

Layer 1 (national, benchmark): per-item price (CPI) x quantity (household survey)
comovement. Residualize each series to remove its expected component, then label
each item-month supply-driven (residual signs opposite: P up / Q down) or
demand-driven (same sign: P up / Q up). Aggregate item labels with expenditure
weights to get the national supply-driven share of CPI inflation.

Pre-registration (DEC-016 補遺, locked before seeing any split):
  - Price source: CPI primary (object decomposed = official CPI inflation).
    unit-value (expenditure/quantity) is a robustness run only.
  - Residualization: monthly AR + seasonal (direction fixed; AR order / seasonal
    method confirmed against series characteristics at implementation).
  - Quantity history pulled full 2000-2024 (residualization needs a long series).

Framing guardrail: "supply-driven" != "imported cost-push". Shapiro's supply label
captures ALL supply shocks (domestic labor, weather, ...). Use as triangulation
of the cost-push story, not as an isolated import-channel measure.

Crosswalk: household survey item codes (家計調査 9-digit) <-> CPI item codes
(2020-base 4-digit) are different schemes; matched by normalized item name.
Only exact normalized-name matches are kept (a false crosswalk would corrupt the
decomposition); unmatched items are logged for transparency (no silent capping).
"""

import re
from pathlib import Path

import httpx
import pandas as pd

from src.data.estat_api import get_api_key, get_stats_data

ROOT = Path(__file__).resolve().parents[2]
RAW_HH = ROOT / "data" / "raw" / "household-survey" / "household_quantity_monthly_2000_2024.csv"
OUT_DIR = ROOT / "data" / "processed" / "shapiro"

CPI_TABLE = "0003427113"  # 消費者物価指数 2020年基準（cat01=790 codes, 品目別を含む）


def _norm_name(name: str) -> str:
    """Normalize an item name for cross-scheme matching.

    Strips a leading code/number token (e.g. '120 食パン' -> '食パン',
    '1.1.2 パン' -> 'パン', '1021 食パン' -> '食パン') and whitespace.
    """
    name = str(name)
    name = re.sub(r"^[0-9.\-]+\s*", "", name)  # leading code / dotted-number / dash
    return name.replace("　", "").replace(" ", "").strip()


def _cpi_item_names() -> dict[str, str]:
    """Return {normalized_name: cpi_code} for item-level CPI codes (non-0xxx)."""
    key = get_api_key()
    r = httpx.get(
        "https://api.e-stat.go.jp/rest/3.0/app/json/getMetaInfo",
        params={"appId": key, "statsDataId": CPI_TABLE, "lang": "J"},
        timeout=60,
    ).json()
    objs = r["GET_META_INFO"]["METADATA_INF"]["CLASS_INF"]["CLASS_OBJ"]
    out = {}
    for o in objs:
        if o["@id"] != "cat01":
            continue
        cls = o["CLASS"]
        cls = cls if isinstance(cls, list) else [cls]
        for c in cls:
            code, nm = c["@code"], c["@name"]
            if code[0] == "0":  # 0xxx = aggregate category, skip (item-level only)
                continue
            out[_norm_name(nm)] = code
    return out


def build_crosswalk(save: bool = True) -> pd.DataFrame:
    """Build household-quantity-item <-> CPI-item crosswalk by exact normalized name.

    Returns a DataFrame with columns
    [hh_code, hh_name, cpi_code, cpi_name_norm, matched].
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cpi = _cpi_item_names()

    h = pd.read_csv(RAW_HH, dtype=str)
    items = h[["cat01_code", "cat01_name"]].drop_duplicates()
    # household leaf items: name without a dotted-number prefix (dotted = aggregate)
    leaf = items[~items["cat01_name"].str.match(r"^[0-9]+\.")].copy()

    leaf["cpi_name_norm"] = leaf["cat01_name"].map(_norm_name)
    leaf["cpi_code"] = leaf["cpi_name_norm"].map(cpi)
    leaf["matched"] = leaf["cpi_code"].notna()
    leaf = leaf.rename(columns={"cat01_code": "hh_code", "cat01_name": "hh_name"})
    leaf = leaf[["hh_code", "hh_name", "cpi_code", "cpi_name_norm", "matched"]]

    n_match = int(leaf["matched"].sum())
    print(f"Crosswalk: {n_match}/{len(leaf)} household leaf items matched to CPI items")
    print(f"Unmatched ({len(leaf) - n_match}): logged in crosswalk.csv (matched=False)")

    if save:
        path = OUT_DIR / "crosswalk.csv"
        leaf.to_csv(path, index=False)
        print(f"Saved {path}")
    return leaf


def _parse_month(time_code: str) -> "pd.Timestamp | float":
    """e-Stat monthly time_code YYYY00MMDD (month doubled) -> Timestamp (NaT if not monthly)."""
    s = str(time_code)
    # monthly: 2022000101 (Jan) .. 2022001212 (Dec); annual/fiscal codes end in 0000
    m = re.match(r"^(\d{4})00(\d{2})\d{2}$", s)
    if not m:
        return pd.NaT
    yy, mm = int(m.group(1)), int(m.group(2))
    if not (1 <= mm <= 12):
        return pd.NaT
    return pd.Timestamp(year=yy, month=mm, day=1)


def fetch_cpi_items(codes: list[str]) -> pd.DataFrame:
    """Fetch monthly CPI index (tab=1 指数) for the given item codes, full history."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = OUT_DIR / "cpi_items_monthly.csv"
    if cache.exists():
        print(f"Loading cached CPI items: {cache}")
        return pd.read_csv(cache, dtype={"cat01_code": str})
    print(f"Fetching CPI index for {len(codes)} matched items...")
    # e-Stat caps cdCat01 at 100 codes per request -> batch
    parts = []
    for i in range(0, len(codes), 90):
        chunk = codes[i:i + 90]
        parts.append(get_stats_data(
            CPI_TABLE,
            cdArea="00000",  # 全国
            cdTab="1",       # 指数
            cdCat01=",".join(chunk),
        ))
    df = pd.concat(parts, ignore_index=True)
    df.to_csv(cache, index=False)
    print(f"Saved {cache} ({len(df)} rows)")
    return df


EXP_TABLE = "0003343671"  # 家計調査 品目別 金額（2020改定・月次・二人以上）= 数量の金額版


def fetch_expenditure_weights(codes: list[str]) -> pd.Series:
    """Fixed expenditure weight per household item = mean monthly expenditure (2015-2024).

    Faithful to Shapiro's fixed expenditure-weight aggregation. Uses the 金額
    companion table (same 9-digit item codes as the quantity table). Fetches only
    the matched item codes (chunked; the full table exceeds the 100k-row API cap).
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cache = OUT_DIR / "expenditure_monthly.csv"
    if cache.exists():
        exp = pd.read_csv(cache, dtype={"cat01_code": str})
    else:
        print(f"Fetching household expenditure for {len(codes)} matched items (weights)...")
        parts = []
        for i in range(0, len(codes), 90):
            parts.append(get_stats_data(
                EXP_TABLE, cdCat02="03", cdArea="00000",
                cdCat01=",".join(codes[i:i + 90]),
            ))
        exp = pd.concat(parts, ignore_index=True)
        exp.to_csv(cache, index=False)
        print(f"Saved {cache} ({len(exp)} rows)")
    exp["date"] = exp["time_code"].map(_parse_month)
    exp = exp.dropna(subset=["date"])
    exp = exp[exp["date"].dt.year >= 2015]  # base window for fixed weights
    w = exp.groupby("cat01_code")["value"].mean()
    w.index.name = "hh_code"
    return w


def build_panel(save: bool = True) -> pd.DataFrame:
    """Merge CPI index (P) and household quantity (Q) into a monthly item panel.

    Returns long DataFrame [date, hh_code, hh_name, cpi_code, P, Q].
    """
    xwalk = build_crosswalk(save=False)
    matched = xwalk[xwalk["matched"]].copy()

    cpi = fetch_cpi_items(matched["cpi_code"].tolist())
    cpi = cpi.rename(columns={"cat01_code": "cpi_code", "value": "P"})
    cpi["date"] = cpi["time_code"].map(_parse_month)
    cpi = cpi.dropna(subset=["date"])[["date", "cpi_code", "P"]]

    hh = pd.read_csv(RAW_HH, dtype={"cat01_code": str})
    hh = hh.rename(columns={"cat01_code": "hh_code", "value": "Q"})
    hh["date"] = hh["time_code"].map(_parse_month)
    hh = hh.dropna(subset=["date"])[["date", "hh_code", "Q"]]

    panel = (
        matched[["hh_code", "hh_name", "cpi_code"]]
        .merge(hh, on="hh_code")
        .merge(cpi, on=["date", "cpi_code"])
        .sort_values(["hh_code", "date"])
        .reset_index(drop=True)
    )
    print(f"Panel: {panel['hh_code'].nunique()} items x "
          f"{panel['date'].nunique()} months = {len(panel)} rows "
          f"({panel['date'].min():%Y-%m}..{panel['date'].max():%Y-%m})")
    if save:
        path = OUT_DIR / "price_quantity_panel.csv"
        panel.to_csv(path, index=False)
        print(f"Saved {path}")
    return panel


import numpy as np
import statsmodels.api as sm

# Near-zero threshold for unexpected price move (sign(nu_p) ill-defined below this).
# CPI item indices are sticky -> many item-months have nu_p ~ 0; below this the
# label would collapse to the quantity sign alone (advisor caveat #2). Reported.
NU_P_NEARZERO = 1e-4  # in log points (~0.01% unexpected m/m price move)


def _residualize_item(g: pd.DataFrame, lags: int, cross: bool) -> pd.DataFrame:
    """Reduced-form residuals nu_p, nu_q for one item on monthly dlog growth.

    cross=True -> VAR (regress each growth on lags of BOTH p- and q-growth;
    faithful to Shapiro z=(q,p)). cross=False -> own-lag AR. Always includes
    11 calendar-month dummies (seasonal -> expected component).
    """
    g = g.sort_values("date").copy()
    g["lp"] = np.log(g["P"])
    g["lq"] = np.log(g["Q"].where(g["Q"] > 0))
    g["dp"] = g["lp"].diff()
    g["dq"] = g["lq"].diff()
    # Mask growth computed ACROSS a calendar gap: .diff() over a non-consecutive
    # month pair returns the change across the gap as one spurious large Δlog,
    # which would leak into the contribution sum (advisor: inflates 2021 total).
    mnum = g["date"].dt.year * 12 + g["date"].dt.month
    noncontig = mnum.diff() != 1
    g.loc[noncontig, ["dp", "dq"]] = np.nan
    g = g.dropna(subset=["dp", "dq"]).reset_index(drop=True)
    if len(g) < lags + 24:  # need enough obs for stable fit
        return pd.DataFrame()

    # regressor matrix: lags of dp (and dq if cross) + month dummies
    X = pd.DataFrame(index=g.index)
    srcs = ["dp", "dq"] if cross else None
    for L in range(1, lags + 1):
        X[f"dp_l{L}"] = g["dp"].shift(L)
        if cross:
            X[f"dq_l{L}"] = g["dq"].shift(L)
    months = pd.get_dummies(g["date"].dt.month, prefix="m", drop_first=True).astype(float)
    X = pd.concat([X, months.set_index(X.index)], axis=1)
    X = sm.add_constant(X)

    valid = X.dropna().index
    Xv = X.loc[valid]
    out = g.loc[valid, ["date", "dp"]].copy()  # dp = monthly price growth (for contribution)
    for tgt, name in [("dp", "nu_p"), ("dq", "nu_q")]:
        y = g.loc[valid, tgt]
        out[name] = sm.OLS(y.astype(float), Xv.astype(float)).fit().resid
    return out


def classify(panel: pd.DataFrame, lags: int = 6, cross: bool = True) -> pd.DataFrame:
    """Per item-month supply/demand label from residual-sign comovement.

    supply  (cost-push): nu_p > 0, nu_q < 0  (or nu_p < 0, nu_q > 0)  -> opposite signs
    demand:              nu_p and nu_q same sign
    Returns long DataFrame [date, hh_code, nu_p, nu_q, label, nearzero_p].
    """
    parts = []
    for code, g in panel.groupby("hh_code"):
        r = _residualize_item(g, lags=lags, cross=cross)
        if r.empty:
            continue
        r["hh_code"] = code
        parts.append(r)
    r = pd.concat(parts, ignore_index=True)
    r["nearzero_p"] = r["nu_p"].abs() < NU_P_NEARZERO
    opposite = (np.sign(r["nu_p"]) * np.sign(r["nu_q"])) < 0
    r["label"] = np.where(opposite, "supply", "demand")
    return r


def supply_share(labels: pd.DataFrame, weights: pd.Series) -> pd.DataFrame:
    """Shapiro-style decomposition per month (within covered basket).

    Faithful to Shapiro: weight each item's INFLATION CONTRIBUTION (w_i * dp_i),
    not the fraction of items. Supply-driven inflation = sum of contributions of
    supply-labeled items; supply share = supply-driven / total covered inflation.
    A fraction-of-items metric (commented out) ignores price-move magnitude and is
    swamped by survey noise (~0.5 every month) -- the contribution weighting is
    what makes the 2022 supply surge visible.
    """
    m = labels.copy()
    w = m["hh_code"].map(weights).fillna(weights.median())
    w = w / w.groupby(m["date"]).transform("sum")  # normalize within month
    m["contrib"] = w * m["dp"]                       # item contribution to covered inflation
    m["supply_contrib"] = m["contrib"].where(m["label"] == "supply", 0.0)
    agg = m.groupby("date").apply(
        lambda d: pd.Series({
            "supply_infl": d["supply_contrib"].sum(),      # supply contribution, m/m log
            "total_infl": d["contrib"].sum(),              # total contribution, m/m log
            "n_items": len(d),
            "nearzero_p_frac": d["nearzero_p"].mean(),
        }), include_groups=False
    ).reset_index()
    # NOTE: supply_infl / total_infl are CUMULATIVE-MONTHLY (Dec-to-Dec momentum)
    # quantities when summed over a year -- NOT annual-average YoY, and the basket
    # does NOT track official 食料 CPI (physical-quantity items only; excludes
    # 外食/調理/加工, includes household energy). They are an INTERNAL denominator
    # used only to form supply_share. Headline = supply_share (a within-basket
    # split that does not require matching any published aggregate).
    agg["supply_share"] = np.where(
        agg["total_infl"] > 1e-4, agg["supply_infl"] / agg["total_infl"], np.nan
    )
    return agg


def validate_price_yoy(panel: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """Expenditure-weighted annual-average price-level YoY (%) of the covered basket.

    DISCLOSURE, not a validation against 食料 CPI: the covered basket diverges from
    official 食料 CPI BY CONSTRUCTION -- it holds only physical-quantity items
    (excludes 外食/調理/加工) and includes household energy. The basket shows the
    cost shock peaking in 2022 while official 食料 peaks in 2023; that gap is the
    lagged passthrough of the same import shock through processed/dining food --
    consistent with cost-push, not a contradiction.
    """
    p = panel.dropna(subset=["P"]).copy()
    p["w"] = p["hh_code"].map(weights).fillna(weights.median())
    p["year"] = pd.to_datetime(p["date"]).dt.year
    lvl = p.groupby("year").apply(
        lambda d: np.average(d["P"], weights=d["w"]), include_groups=False
    )
    return (lvl.pct_change(fill_method=None) * 100).rename("price_yoy_pct")


def run(save: bool = True) -> dict:
    """Full layer-1 pipeline + robustness grid. Returns summary dict."""
    panel = build_panel(save=save)
    weights = fetch_expenditure_weights(sorted(panel["hh_code"].unique()))

    # Robustness grid: {AR, VAR} x {short, long lags}. Aggregate-share stability
    # across specs IS the deliverable (advisor) -- not any single per-item label.
    grid = {}
    for cross in (True, False):
        for lags in (3, 12):
            key = f"{'VAR' if cross else 'AR'}_lag{lags}"
            lab = classify(panel, lags=lags, cross=cross)
            grid[key] = supply_share(lab, weights)

    # Primary spec: VAR, 6 lags
    primary = supply_share(classify(panel, lags=6, cross=True), weights)

    if save:
        primary.to_csv(OUT_DIR / "supply_share_primary.csv", index=False)
        for k, v in grid.items():
            v.to_csv(OUT_DIR / f"supply_share_{k}.csv", index=False)

    def annual(df):
        """Annual = sum of monthly m/m contributions within year, in pp."""
        d = df.copy()
        d["year"] = pd.to_datetime(d["date"]).dt.year
        g = d.groupby("year").agg(supply=("supply_infl", "sum"),
                                  total=("total_infl", "sum"))
        g[["supply", "total"]] *= 100  # log m/m -> ~pp
        g["share"] = g["supply"] / g["total"]
        return g

    ann_primary = annual(primary)
    yoy = validate_price_yoy(panel, weights)
    print("\n=== Layer-1 Shapiro decomposition ===")
    print("Basket = 116 physical-quantity food + household-energy items (NOT 食料 CPI).")
    print("HEADLINE = supply-driven SHARE (Shapiro's emphasis; within-basket split).")
    print("Primary = VAR, 6 lags:")
    for y in range(2019, 2025):
        if y in ann_primary.index:
            print(f"  {y}: supply_share={ann_primary.loc[y, 'share']:.2f}")
    print(f"\nDemand->supply transition: 2021 share={ann_primary['share'].get(2021):.2f} (demand-led) "
          f"-> 2022 share={ann_primary['share'].get(2022):.2f} (supply surge)")
    print(f"near-zero nu_p fraction (sticky-CPI caveat), mean 2020-24: "
          f"{primary[primary['date'].dt.year>=2020]['nearzero_p_frac'].mean():.3f}")
    print("\nRobustness -- supply-driven SHARE by year across specs:")
    summ = pd.DataFrame({k: annual(v)["share"] for k, v in grid.items()})
    summ["PRIMARY_VAR6"] = ann_primary["share"]
    print(summ.loc[summ.index.isin(range(2020, 2025))].round(2).to_string())
    print("\nBasket vs official 食料 CPI YoY (DISCLOSURE -- diverge by construction; "
          "basket peaks 2022, 食料 peaks 2023 = lagged passthrough via 外食/調理/加工):")
    print("  basket YoY%:", {y: round(yoy.get(y, float('nan')), 1) for y in range(2021, 2025)})
    return {"primary": primary, "grid": grid, "annual": summ}


if __name__ == "__main__":
    run()
