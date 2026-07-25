"""
Oil-supply-shock local projection: monthly panel preparation.

Builds data/processed/oil-lp/monthly_panel.csv — a monthly panel of Japanese
CPI (headline + 10大費目) and quintile-specific effective CPI, plus the BOJ
import energy price index, for local-projection analysis of oil supply shocks.

Column definitions (monthly_panel.csv)
--------------------------------------
date                    : month, YYYY-MM-01
cpi_headline            : CPI 総合 (2020=100, e-Stat monthly index)
cpi_food                : CPI 食料
cpi_housing             : CPI 住居
cpi_energy_utilities    : CPI 光熱・水道
cpi_furniture           : CPI 家具・家事用品
cpi_clothing            : CPI 被服及び履物
cpi_health              : CPI 保健医療
cpi_transport_comms     : CPI 交通・通信
cpi_education           : CPI 教育
cpi_recreation          : CPI 教養娯楽
cpi_other               : CPI 諸雑費 (proxy for その他の消費支出, per HH_TO_CPI_CODE)
eff_cpi_q1 .. eff_cpi_q5: quintile effective CPI index (base: 2020 avg = 100).
                          Built by cumulating pi_{q,t} = sum_c share_{q,c} *
                          dlog(CPI_{c,t}) over the 10大費目, with expenditure
                          shares fixed at 2019 (家計調査 二人以上の世帯,
                          load_expenditure_shares(year=2019, household_type=3)).
                          Shares are renormalized over the 10 categories
                          (they sum to ~1 of 消費支出 already).
dlog_cpi_headline       : MoM log difference of cpi_headline
dlog_cpi_food           : MoM log difference of cpi_food
dlog_cpi_energy_utilities: MoM log difference of cpi_energy_utilities
dlog_eff_cpi_q1..q5     : pi_{q,t} (MoM effective log-inflation per quintile)
gap_q1_q5_mom_dlog      : dlog_eff_cpi_q1 - dlog_eff_cpi_q5 (log points)
gap_q1_q5_yoy           : YoY pct change of eff_cpi_q1 minus YoY pct change of
                          eff_cpi_q5 (pp)
log_import_energy       : log of BOJ import price index, group=energy
                          (円ベース, 2020=100), NaN before 2015
dlog_import_energy      : MoM log difference of log_import_energy

Data notes / deviations
-----------------------
- Panel coverage: 2005-01..2025-12. 総合 + 10大費目 come from a dedicated
  fetch of the 2020-base linked table 0003427113 (指数, 全国), cached to
  data/raw/cpi/cpi_headline_major_2005_2025.csv (fetch-if-missing; the table
  serves back to 1970-01, we cache from 2005-01 per the LP design spec).
  Its overlap with the pre-existing cpi_category_2015_2025.csv cache is
  asserted to agree exactly (2015-01..2025-12, per category-month).
- The cpi_category_2005_2024.csv cache contains ONLY 41 CPI mid-classification
  (中分類) categories, from 2006-01 — no 総合 and no 10大費目 (that old fetch
  requested mid-category codes only).
- log_import_energy / dlog_import_energy are NaN before 2015-01 (BOJ series
  start); gap_q1_q5_yoy is NaN for the first 12 months.
- The splice check (DEC-013 lesson) is also performed on the 41 shared
  mid-classification categories over the overlap 2015-01..2024-12, matched by
  cleaned category name (duplicate names in the 2015 cache, e.g. 電気代 as
  中分類56 vs 品目3500, are resolved by requiring an exact-match candidate).
  Both caches carry tab_code 1/2/3 rows; only tab_code==1 (指数) is used.
- Annual cross-check replicates the repo's established Q1-Q5 gap definition
  (annual-average index minus the category's 2015-19 baseline average,
  weighted by the Q1-Q5 share difference; cost_push_id.compute_cpi_changes +
  quintile_impact) — the established +2.01/+2.06/+2.45/+3.36 pp figures are
  vs-baseline levels, not YoY. The YoY-based gap is also reported for
  reference.

Run: uv run python src/analysis/oil_lp_prep.py
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# allow `uv run python src/analysis/oil_lp_prep.py` (repo root on sys.path)
_ROOT = str(Path(__file__).resolve().parents[2])
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.analysis.cost_push_id import HH_TO_CPI_CODE
from src.analysis.quintile_impact import load_expenditure_shares

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed" / "oil-lp"

CPI_OLD = DATA_RAW / "cpi" / "cpi_category_2005_2024.csv"
CPI_NEW = DATA_RAW / "cpi" / "cpi_category_2015_2025.csv"
CPI_LONG = DATA_RAW / "cpi" / "cpi_headline_major_2005_2025.csv"
BOJ_IMPORT = DATA_RAW / "boj-cgpi" / "import_prices_extracted.csv"

# e-Stat CPI 2020-base table (same as fetch_cpi.CPI_2020_TABLE)
CPI_2020_TABLE = "0003427113"
# cdCat01 codes for 総合 + 10大費目 in table 0003427113
LONG_FETCH_CAT01 = [
    "0001",  # 総合
    "0002",  # 食料
    "0045",  # 住居
    "0054",  # 光熱・水道
    "0060",  # 家具・家事用品
    "0082",  # 被服及び履物
    "0107",  # 保健医療
    "0111",  # 交通・通信
    "0118",  # 教育
    "0122",  # 教養娯楽
    "0145",  # 諸雑費
]

# hh_cat_code -> ascii column suffix for the panel
HH_CODE_TO_COL: dict[int, str] = {
    60: "food",
    102: "housing",
    107: "energy_utilities",
    112: "furniture",
    122: "clothing",
    140: "health",
    145: "transport_comms",
    152: "education",
    156: "recreation",
    165: "other",
}

ESTABLISHED_GAPS = {2022: 2.01, 2023: 2.06, 2024: 2.45, 2025: 3.36}


def _monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to index rows (tab=1, 指数) and calendar-monthly time_codes
    (YYYY00MMMM, [6:8]==[8:10]). The 2005_2024 cache also carries tab_code
    2/3 (前年比 etc.), which must be excluded before date-indexing.
    tab_code is coerced to numeric: fresh API frames carry it as string,
    CSV round-trips as int."""
    df = df[pd.to_numeric(df["tab_code"], errors="coerce") == 1]
    tc = df["time_code"].astype(str)
    mm = [f"{i:02d}" for i in range(1, 13)]
    out = df[tc.str[8:10].isin(mm) & (tc.str[6:8] == tc.str[8:10])].copy()
    tc = out["time_code"].astype(str)
    out["date"] = pd.to_datetime(tc.str[:4] + "-" + tc.str[8:10] + "-01")
    out["name_clean"] = (
        out["cat01_name"].astype(str).str.replace(r"^\d+\s*", "", regex=True)
    )
    return out


def splice_check(lines: list[str]) -> None:
    """
    DEC-013 lesson: assert the two CPI caches agree exactly on their overlap.

    The old cache holds only mid-classification categories, so the check runs
    per shared cleaned category name over 2015-01..2024-12. Duplicate names in
    the new cache (中分類 vs 品目 codes) pass if ANY candidate code matches
    exactly. Raises RuntimeError with full detail on any nonzero diff.
    """
    old = _monthly(pd.read_csv(CPI_OLD))
    new = _monthly(pd.read_csv(CPI_NEW))

    problems = []
    overall_max = 0.0
    n_checked = 0
    for name in sorted(old["name_clean"].unique()):
        o = old[old["name_clean"] == name].set_index("date")["value"].astype(float)
        cand = new[new["name_clean"] == name]
        if cand.empty:
            problems.append(f"  {name}: not present in 2015_2025 cache")
            continue
        best = None
        for code, grp in cand.groupby("cat01_code"):
            s = grp.set_index("date")["value"].astype(float)
            common = o.index.intersection(s.index)
            if len(common) == 0:
                continue
            d = float((o.loc[common] - s.loc[common]).abs().max())
            if best is None or d < best[1]:
                best = (code, d, len(common))
        if best is None:
            problems.append(f"  {name}: no overlapping months in 2015_2025 cache")
            continue
        code, d, n = best
        n_checked += 1
        overall_max = max(overall_max, d)
        if d != 0.0:
            problems.append(
                f"  {name}: max abs diff {d} over {n} months "
                f"(best-matching new-cache cat01_code={code})"
            )

    lines.append(
        f"[splice check] {n_checked} shared mid-classification categories, "
        f"overlap 2015-01..2024-12: max abs diff = {overall_max}"
    )
    lines.append(
        "[splice check] note: 2005_2024 cache holds ONLY 41 中分類 categories "
        "(from 2006-01, no 総合/10大費目) -> headline/10大費目 come from the "
        "dedicated long fetch; this check runs at mid-category level."
    )
    if problems:
        detail = "\n".join(problems)
        raise RuntimeError(
            f"Splice check FAILED — caches disagree on overlap:\n{detail}"
        )
    lines.append("[splice check] PASS (exact agreement on all shared series)")


def fetch_long_cache() -> pd.DataFrame:
    """
    Fetch-if-missing: 総合 + 10大費目 monthly CPI 2005-01..2025-12 from the
    2020-base linked table 0003427113 (指数, 全国), cached to CPI_LONG.
    (The table actually serves back to 1970-01; we cache from 2005-01 per the
    LP design spec.)
    """
    if CPI_LONG.exists():
        return pd.read_csv(CPI_LONG)
    from src.data.estat_api import get_stats_data

    print(f"Fetching {CPI_2020_TABLE} (総合+10大費目, 2005-01..2025-12)...")
    df = get_stats_data(
        CPI_2020_TABLE,
        cdArea="00000",
        cdTab="1",  # 指数のみ
        cdCat01=",".join(LONG_FETCH_CAT01),
        # NOTE: e-Stat compares cdTimeFrom against the leading 6 chars of the
        # 10-digit time code; monthly 2005 codes are 200500MMMM, so "200501"
        # would silently drop all of 2005. Use "200500" (fetch_cpi idiom).
        cdTimeFrom="200500",
        cdTimeTo="202512",
    )
    if df.empty:
        raise RuntimeError("e-Stat returned no data for the long CPI fetch")
    df.to_csv(CPI_LONG, index=False)
    print(f"Saved {CPI_LONG} ({len(df)} rows)")
    return df


def long_cache_overlap_check(lines: list[str]) -> None:
    """
    Verify the long cache agrees exactly with the existing 2015_2025 cache on
    the overlap (2015-01..2025-12), per category-month. STOP on any diff != 0.
    """
    long = _monthly(fetch_long_cache())
    new = _monthly(pd.read_csv(CPI_NEW))

    problems = []
    overall_max = 0.0
    n_pairs = 0
    for code in sorted(long["cat01_code"].astype(int).unique()):
        l = (
            long[long["cat01_code"].astype(int) == code]
            .set_index("date")["value"].astype(float)
        )
        s = (
            new[new["cat01_code"].astype(int) == code]
            .set_index("date")["value"].astype(float)
        )
        common = l.index.intersection(s.index)
        if len(common) == 0:
            problems.append(f"  cat01={code}: no overlap in 2015_2025 cache")
            continue
        d = float((l.loc[common] - s.loc[common]).abs().max())
        overall_max = max(overall_max, d)
        n_pairs += len(common)
        if d != 0.0:
            bad = (l.loc[common] - s.loc[common]).abs()
            bad = bad[bad > 0].head(5)
            problems.append(
                f"  cat01={code}: max abs diff {d} over {len(common)} months; "
                f"first offenders: {bad.to_dict()}"
            )
    lines.append(
        f"[long-cache overlap] 総合+10大費目 vs 2015_2025 cache, "
        f"{n_pairs} category-months compared: max abs diff = {overall_max}"
    )
    if n_pairs < 11 * 120:  # guard against a vacuous pass (11 cats x >=10y)
        problems.append(f"  only {n_pairs} category-months compared — vacuous")
    if problems:
        raise RuntimeError(
            "Long-cache overlap check FAILED:\n" + "\n".join(problems)
        )
    lines.append("[long-cache overlap] PASS (exact agreement)")


def load_cpi_panel() -> pd.DataFrame:
    """Monthly wide CPI: date x [cpi_headline + 10大費目 columns], 2020=100,
    from the long cache (2005-01..2025-12)."""
    new = _monthly(fetch_long_cache())

    frames = {}
    # headline
    h = new[new["name_clean"] == "総合"]
    assert h["cat01_code"].nunique() == 1, "総合 ambiguous match"
    frames["cpi_headline"] = h.set_index("date")["value"].astype(float)

    # 10大費目 via the repo's established name mapping (HH_TO_CPI_CODE)
    for hh_code, cpi_name in HH_TO_CPI_CODE.items():
        sub = new[new["name_clean"] == cpi_name]
        if sub.empty:
            raise RuntimeError(f"CPI category not found: {cpi_name}")
        if sub["cat01_code"].nunique() > 1:
            # keep the lowest code = 中分類/大分類 side (品目 codes are larger)
            keep = sub["cat01_code"].min()
            sub = sub[sub["cat01_code"] == keep]
        frames[f"cpi_{HH_CODE_TO_COL[hh_code]}"] = (
            sub.set_index("date")["value"].astype(float)
        )

    panel = pd.DataFrame(frames).sort_index()
    panel.index.name = "date"
    return panel


def build_effective_cpi(panel: pd.DataFrame) -> pd.DataFrame:
    """
    Quintile effective CPI: pi_{q,t} = sum_c w_{q,c} * dlog(CPI_{c,t}),
    fixed 2019 shares renormalized over the 10大費目; cumulated index with
    2020 average = 100.
    """
    shares = load_expenditure_shares(year=2019, household_type=3)

    dlog = {}
    for hh_code, col in HH_CODE_TO_COL.items():
        dlog[hh_code] = np.log(panel[f"cpi_{col}"]).diff()
    dlog = pd.DataFrame(dlog)

    out = pd.DataFrame(index=panel.index)
    for q in range(1, 6):
        w = shares.loc[q, list(HH_CODE_TO_COL.keys())]
        w = w / w.sum()  # renormalize over the 10 categories
        pi = (dlog * w).sum(axis=1, min_count=len(w))
        out[f"dlog_eff_cpi_{q}"] = pi
        idx = np.exp(pi.fillna(0.0).cumsum())
        base = idx[idx.index.year == 2020].mean()
        out[f"eff_cpi_q{q}"] = idx / base * 100.0
    return out


def load_import_energy() -> pd.DataFrame:
    """BOJ import price index, group=energy (円ベース): log level + dlog."""
    boj = pd.read_csv(BOJ_IMPORT, parse_dates=["date"])
    en = boj[boj["group"] == "energy"].set_index("date")["value"].astype(float)
    en = en.sort_index()
    out = pd.DataFrame({"log_import_energy": np.log(en)})
    out["dlog_import_energy"] = out["log_import_energy"].diff()
    return out


def annual_gap_crosscheck(panel: pd.DataFrame, lines: list[str]) -> None:
    """
    Cross-check vs established Q1-Q5 effective inflation gaps (DEC-023 暦年).

    Established definition (cost_push_id + quintile_impact): per category,
    annual-average index minus the category's own 2015-19 average, weighted by
    (share_Q1 - share_Q5) with fixed 2019 shares (NOT renormalized there —
    replicated identically here). Also reports the YoY-based gap from the
    effective indices for reference.
    """
    shares = load_expenditure_shares(year=2019, household_type=3)
    codes = list(HH_CODE_TO_COL.keys())
    dshare = shares.loc[1, codes] - shares.loc[5, codes]

    ann = panel[[f"cpi_{c}" for c in HH_CODE_TO_COL.values()]].groupby(
        panel.index.year
    ).mean()
    ann.columns = codes
    baseline = ann.loc[2015:2019].mean()
    gap_vs_base = ((ann - baseline) * dshare).sum(axis=1)

    eff = panel[["eff_cpi_q1", "eff_cpi_q5"]].groupby(panel.index.year).mean()
    yoy = (eff / eff.shift(1) - 1) * 100
    gap_yoy = yoy["eff_cpi_q1"] - yoy["eff_cpi_q5"]

    lines.append("\n[annual cross-check] Q1-Q5 effective inflation gap (pp)")
    lines.append(
        f"{'year':>6} {'computed(vs 2015-19 base)':>26} {'established':>12} "
        f"{'diff':>8} {'yoy-based(ref)':>15}"
    )
    max_abs_diff = 0.0
    for yr, want in ESTABLISHED_GAPS.items():
        got = float(gap_vs_base.loc[yr])
        diff = got - want
        max_abs_diff = max(max_abs_diff, abs(diff))
        lines.append(
            f"{yr:>6} {got:>26.3f} {want:>12.2f} {diff:>+8.3f} "
            f"{float(gap_yoy.loc[yr]):>15.3f}"
        )
    lines.append(
        f"[annual cross-check] max |computed - established| = {max_abs_diff:.4f}pp "
        f"({'OK (<0.1pp)' if max_abs_diff < 0.1 else 'FAIL — investigate'})"
    )
    lines.append(
        "[annual cross-check] note: established +2.01/+2.06/+2.45/+3.36 are "
        "vs-2015-19-baseline level gaps (not YoY); the YoY column is a "
        "different quantity shown for reference."
    )
    if max_abs_diff >= 0.1:
        raise RuntimeError("Annual gap cross-check failed (diff >= 0.1pp)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    # 1-2. splice checks (must pass before building the panel)
    splice_check(lines)
    long_cache_overlap_check(lines)

    # 1,3. CPI panel + effective CPI
    cpi = load_cpi_panel()
    eff = build_effective_cpi(cpi)

    # dlog columns for headline / food / energy
    dlogs = pd.DataFrame(index=cpi.index)
    for col in ["cpi_headline", "cpi_food", "cpi_energy_utilities"]:
        dlogs[f"dlog_{col}"] = np.log(cpi[col]).diff()

    # gap series
    gaps = pd.DataFrame(index=cpi.index)
    gaps["gap_q1_q5_mom_dlog"] = eff["dlog_eff_cpi_1"] - eff["dlog_eff_cpi_5"]
    yoy_q1 = (eff["eff_cpi_q1"] / eff["eff_cpi_q1"].shift(12) - 1) * 100
    yoy_q5 = (eff["eff_cpi_q5"] / eff["eff_cpi_q5"].shift(12) - 1) * 100
    gaps["gap_q1_q5_yoy"] = yoy_q1 - yoy_q5

    # 4. import energy
    imp = load_import_energy()

    # 5. merge
    eff_idx_cols = [f"eff_cpi_q{q}" for q in range(1, 6)]
    eff_dlog = eff[[f"dlog_eff_cpi_{q}" for q in range(1, 6)]].rename(
        columns={f"dlog_eff_cpi_{q}": f"dlog_eff_cpi_q{q}" for q in range(1, 6)}
    )
    panel = pd.concat(
        [cpi, eff[eff_idx_cols], dlogs, eff_dlog, gaps], axis=1
    ).join(imp, how="left")
    panel = panel.sort_index()

    # 6. verification
    annual_gap_crosscheck(pd.concat([cpi, eff[eff_idx_cols]], axis=1), lines)

    lines.append(
        f"\n[panel] coverage {panel.index.min():%Y-%m} .. {panel.index.max():%Y-%m}, "
        f"n_months={len(panel)}, n_cols={panel.shape[1]}"
    )
    lines.append(f"[panel] columns: {', '.join(panel.columns)}")
    n_imp = panel["log_import_energy"].notna().sum()
    lines.append(f"[panel] import_energy non-NaN months: {n_imp} (BOJ series 2015+)")

    out_csv = OUT_DIR / "monthly_panel.csv"
    panel.reset_index().assign(date=lambda d: d["date"].dt.strftime("%Y-%m-01")).to_csv(
        out_csv, index=False
    )
    lines.append(f"[panel] saved: {out_csv}")

    report = "\n".join(lines)
    print(report)
    (OUT_DIR / "prep_checks.txt").write_text(report + "\n", encoding="utf-8")
    print(f"\nSaved checks: {OUT_DIR / 'prep_checks.txt'}")


if __name__ == "__main__":
    main()
