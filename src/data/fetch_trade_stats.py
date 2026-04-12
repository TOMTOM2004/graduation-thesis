"""
Fetch trade statistics from e-Stat (財務省貿易統計).

Main purpose: Compute China's import share for clothing (概況品807) and
footwear (概況品809) to justify the competitive-import exclusion in
bridge_matrix_mid.py (DEC-010).

Tables used (概況品別国別表):
  0003313968 : 2016–2020 (confirmed)
  0003425296 : 2021–2024 (confirmed/speed estimate)

Relevant category codes (cat01):
  80700000 : 807_衣類及び同附属品
  80900000 : 809_はき物

Country code (area):
  50105 : 105_中華人民共和国

Value code (cat02):
  120 : 合計_金額 (annual total, 万円)
"""

from pathlib import Path

import pandas as pd

from .estat_api import get_stats_data, search_stats

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "trade-stats"
PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed" / "trade-stats"

# e-Stat table IDs: 概況品別国別表 (輸入)
TABLE_IDS = {
    "2016_2020": "0003313968",
    "2021_2024": "0003425296",
}

# Commodity codes of interest
CLOTHING_CODE = "80700000"   # 807_衣類及び同附属品
FOOTWEAR_CODE = "80900000"   # 809_はき物

# Country code for China
CHINA_CODE = "50105"

# cat02 code for annual total value
VALUE_CODE = "120"  # 合計_金額


def _fetch_one_table(stats_data_id: str, label: str) -> pd.DataFrame:
    """
    Fetch clothing and footwear import data (all countries) from one table.

    Returns long-format DataFrame with columns:
        year, area_code, area_name, commodity_code, commodity_name, value_万円
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = RAW_DIR / f"trade_country_apparel_{label}.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    print(f"Fetching {label} from e-Stat (ID={stats_data_id})...")

    df = get_stats_data(
        stats_data_id,
        cdCat01=f"{CLOTHING_CODE},{FOOTWEAR_CODE}",
        cdCat02=VALUE_CODE,
    )

    if df.empty:
        print(f"Warning: No data returned for {label}")
        return df

    # Rename columns for clarity
    rename_map = {}
    for col in df.columns:
        low = col.lower()
        if "cat01" in low:
            rename_map[col] = col.replace("_code", "_commodity_code").replace("_name", "_commodity_name")
        if "area" in low and "_code" in low:
            rename_map[col] = "area_code"
        if "area" in low and "_name" in low:
            rename_map[col] = "area_name"
        if "time" in low and "_code" in low:
            rename_map[col] = "time_code"

    df = df.rename(columns=rename_map)

    # Parse year from time_code (e.g. "2020000000" → 2020)
    if "time_code" in df.columns:
        df["year"] = df["time_code"].astype(str).str[:4].astype(int)

    df.to_csv(cache_path, index=False)
    print(f"Saved: {cache_path} ({len(df)} rows)")
    return df


def fetch_china_import_share() -> pd.DataFrame:
    """
    Compute China's share of Japan's imports for clothing and footwear.

    Fetches all-country data from two e-Stat tables (2016-2020, 2021-2024),
    sums to world total, and divides China's value by the world total.

    Returns
    -------
    pd.DataFrame with columns:
        year, commodity_code, commodity_label, china_value, world_total,
        china_share (fraction 0-1)

    Cache: data/processed/trade-stats/china_import_share_apparel.csv
    """
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = PROCESSED_DIR / "china_import_share_apparel.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    dfs = []
    for label, table_id in TABLE_IDS.items():
        df = _fetch_one_table(table_id, label)
        if not df.empty:
            dfs.append(df)

    if not dfs:
        raise RuntimeError("No data fetched from e-Stat. Check API key and network.")

    raw = pd.concat(dfs, ignore_index=True)

    # Identify commodity and area columns
    cat01_code_col = next((c for c in raw.columns if "cat01" in c.lower() and "_code" in c.lower()), None)
    cat01_name_col = next((c for c in raw.columns if "cat01" in c.lower() and "_name" in c.lower()), None)

    if cat01_code_col is None:
        # Fallback: check all columns
        print("Available columns:", raw.columns.tolist())
        raise KeyError("Could not identify cat01_code column")

    # Filter to clothing + footwear
    mask = raw[cat01_code_col].isin([CLOTHING_CODE, FOOTWEAR_CODE])
    raw = raw[mask].copy()

    # Ensure value is numeric
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")

    # World total: sum all countries per (year, commodity)
    world = (
        raw.groupby(["year", cat01_code_col])["value"]
        .sum()
        .reset_index()
        .rename(columns={"value": "world_total"})
    )

    # China only
    china = (
        raw[raw["area_code"] == CHINA_CODE]
        .groupby(["year", cat01_code_col])["value"]
        .sum()
        .reset_index()
        .rename(columns={"value": "china_value"})
    )

    result = world.merge(china, on=["year", cat01_code_col], how="left")
    result["china_share"] = result["china_value"] / result["world_total"]

    # Add human-readable labels
    commodity_labels = {
        CLOTHING_CODE: "衣類及び同附属品",
        FOOTWEAR_CODE: "はき物（履物）",
    }
    result["commodity_label"] = result[cat01_code_col].map(commodity_labels)
    result = result.rename(columns={cat01_code_col: "commodity_code"})

    result = result.sort_values(["commodity_code", "year"]).reset_index(drop=True)

    result.to_csv(cache_path, index=False)
    print(f"Saved: {cache_path}")
    return result


def print_china_share_summary(df: pd.DataFrame) -> None:
    """Print a readable summary of China's import share."""
    print("\n=== 衣類・履物の中国輸入シェア（財務省貿易統計） ===")
    print(f"{'年':>6}  {'品目':>18}  {'中国輸入(億円)':>14}  {'総輸入(億円)':>12}  {'中国シェア':>10}")
    print("-" * 68)
    for _, row in df.iterrows():
        china_hyaku = row["china_value"] / 10_000  # 万円 → 億円
        world_hyaku = row["world_total"] / 10_000
        print(
            f"  {int(row['year'])}  {row['commodity_label']:>18}  "
            f"{china_hyaku:>14,.0f}  {world_hyaku:>12,.0f}  "
            f"{row['china_share']:>9.1%}"
        )

    # Summary by commodity
    print("\n--- 年平均中国シェア ---")
    summary = df.groupby("commodity_label")["china_share"].agg(["mean", "min", "max"])
    for label, row in summary.iterrows():
        print(f"  {label}: 平均 {row['mean']:.1%}  (範囲: {row['min']:.1%}–{row['max']:.1%})")


def plot_china_share_trend(
    df: pd.DataFrame,
    output_path: Path | None = None,
) -> None:
    """
    Plot China's import share trend for clothing and footwear (2016–2024).

    Also computes competitive Asian supplier share to show the ~80% stability.
    Output: data/processed/trade-stats/fig_china_share_trend.png
    """
    import matplotlib.pyplot as plt
    import japanize_matplotlib

    if output_path is None:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        output_path = PROCESSED_DIR / "fig_china_share_trend.png"

    # Load raw data to compute competitive Asian supplier share
    raw1 = pd.read_csv(RAW_DIR / "trade_country_apparel_2016_2020.csv")
    raw2 = pd.read_csv(RAW_DIR / "trade_country_apparel_2021_2024.csv")
    raw = pd.concat([raw1, raw2], ignore_index=True)
    raw["year"] = raw["time_code"].astype(str).str[:4].astype(int)
    raw["value"] = pd.to_numeric(raw["value"], errors="coerce")

    competitive_areas = [
        "105_中華人民共和国",
        "110_ベトナム",
        "127_バングラデシュ",
        "120_カンボジア",
        "122_ミャンマー",
    ]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        "衣類・履物の輸入国構成（財務省貿易統計 2016–2024）\n"
        "競争的アジアサプライヤーが一貫して ~80% → 価格デカップリングの構造的根拠",
        fontsize=12,
        fontweight="bold",
    )

    commodity_items = [
        (CLOTHING_CODE, "衣類及び同附属品", axes[0]),
        (FOOTWEAR_CODE, "はき物（履物）", axes[1]),
    ]

    for comm_code, label, ax in commodity_items:
        comm_df = df[df["commodity_code"] == comm_code].sort_values("year")
        comm_df = comm_df[comm_df["year"] <= 2024]

        # Compute competitive Asian share per year
        competitive_shares = []
        for yr in comm_df["year"]:
            sub = raw[(raw["year"] == yr) & (raw["cat01_commodity_code"] == comm_code)]
            total = sub["value"].sum()
            comp = sub[sub["area_name"].isin(competitive_areas)]["value"].sum()
            competitive_shares.append(comp / total if total > 0 else 0)

        years = comm_df["year"].tolist()

        ax.plot(years, comm_df["china_share"].tolist(),
                marker="o", linewidth=2, color="#c0392b", label="中国単体")
        ax.plot(years, competitive_shares,
                marker="s", linewidth=2, linestyle="--", color="#2980b9",
                label="競争的アジア計\n（中国・越・孟・柬・緬）")

        ax.axhline(0.80, color="gray", linestyle=":", alpha=0.6, linewidth=1.2, label="80%水準")
        ax.set_ylim(0.3, 0.95)
        ax.set_xticks(years)
        ax.set_xticklabels(years, rotation=45, fontsize=9)
        ax.set_title(label, fontsize=11)
        ax.set_xlabel("年", fontsize=10)
        ax.set_ylabel("輸入シェア", fontsize=10)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
        ax.legend(fontsize=9, loc="lower left")
        ax.grid(axis="y", alpha=0.25)

    fig.text(
        0.5, -0.04,
        "出所: 財務省貿易統計（e-Stat 概況品別国別表、2016–2024年、確定・確速）。"
        "競争的アジアサプライヤー合計が ~80% で安定していることが、"
        "IO表の輸入含有率と価格転嫁が乖離する構造的理由。",
        ha="center", fontsize=8, color="gray",
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")


def find_trade_table() -> None:
    """Search for trade statistics tables on e-Stat."""
    tables = search_stats("貿易統計 概況品 国別 輸入 年次", limit=20)
    for t in tables:
        tid = t.get("@id", "N/A")
        title = t.get("TITLE", {})
        tname = title.get("$", str(title)) if isinstance(title, dict) else str(title)
        cycle = t.get("CYCLE", "N/A")
        print(f"ID: {tid} | Cycle: {cycle} | {tname}")


if __name__ == "__main__":
    print("=== China Import Share: Clothing & Footwear ===")
    df = fetch_china_import_share()
    print_china_share_summary(df)
