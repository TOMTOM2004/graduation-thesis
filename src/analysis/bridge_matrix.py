"""
Phase 2 Step 2a-1/2: Bridge matrix and necessity/discretionary classification.

Maps IO sectors (108) to household survey expenditure categories (大分類, 10 groups)
using the IO table's private consumption column (721 = 民間消費支出).
Then classifies each category as necessity or discretionary (Jaravel 2019 approach).
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.io_utils import load_io_table, compute_import_content

DATA_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
BRIDGE_DIR = DATA_PROCESSED / "bridge-matrix"

# Household survey expenditure codes (cat01 in 家計調査)
# We use major categories (大分類) and key sub-categories
# Format: {hh_code: (hh_name, [IO sector codes that contribute to this category])}
# Weights within each group come from IO private consumption column (721)

HH_CATEGORY_MAP: dict[int, dict] = {
    # --- 食料 (Food) ---
    60: {
        "name": "食料",
        "io_sectors": ["011", "012", "017", "111", "112", "113", "114"],
        "group": "food",
    },
    # --- 住居 (Housing) ---
    102: {
        "name": "住居",
        "io_sectors": ["552", "411", "412"],  # 住宅賃貸料, 建築, 建設補修
        "group": "housing",
    },
    # --- 光熱・水道 (Energy & utilities) ---
    107: {
        "name": "光熱・水道",
        "io_sectors": ["461", "462", "471"],  # 電気, ガス・熱供給, 水道
        "group": "energy_util",
    },
    # --- 家具・家事用品 (Furniture & household goods) ---
    112: {
        "name": "家具・家事用品",
        "io_sectors": ["162", "281", "289", "221", "222", "391"],  # 家具, 金属製品, プラスチック, ゴム, その他
        "group": "furniture",
    },
    # --- 被服及び履物 (Clothing & footwear) ---
    122: {
        "name": "被服及び履物",
        "io_sectors": ["151", "152", "231"],  # 繊維, 衣服, なめし革
        "group": "clothing",
    },
    # --- 保健医療 (Health) ---
    140: {
        "name": "保健医療",
        "io_sectors": ["207", "641", "642"],  # 医薬品, 医療, 保健衛生
        "group": "health",
    },
    # --- 交通・通信 (Transport & communications) ---
    145: {
        "name": "交通・通信",
        "io_sectors": ["351", "352", "353", "571", "572", "575", "591"],  # 自動車, 鉄道, 道路, 航空, 通信
        "group": "transport",
    },
    # --- 教育 (Education) ---
    152: {
        "name": "教育",
        "io_sectors": ["631"],  # 教育
        "group": "education",
    },
    # --- 教養娯楽 (Recreation & culture) ---
    156: {
        "name": "教養娯楽",
        "io_sectors": ["595", "674", "671", "672"],  # 映像・音声・文字, 娯楽, 宿泊, 飲食
        "group": "recreation",
    },
    # --- その他の消費支出 (Other) ---
    165: {
        "name": "その他の消費支出",
        "io_sectors": ["673", "679", "669", "662"],  # 理美容, 対個人, 対事業所, 広告
        "group": "other",
    },
}

# Household survey quintile codes
QUINTILE_CODES = {0: "平均", 1: "1分位（最低）", 2: "2分位", 3: "3分位", 4: "4分位", 5: "5分位（最高）"}


def build_bridge_matrix(force: bool = False) -> pd.DataFrame:
    """
    Build bridge matrix: household category × IO sector.

    B(hh_cat, io_sector) = weight of IO sector in that household category,
    derived from IO private consumption column (column "721").

    force: キャッシュを無視して再計算（再現性検証用）

    Returns
    -------
    pd.DataFrame: index=hh_cat_code, columns=io_sector_codes,
                  values=share of that IO sector's consumption in the category
    """
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = BRIDGE_DIR / "bridge_matrix.csv"

    if cache_path.exists() and not force:
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path, index_col=0)

    print("Building bridge matrix from IO private consumption column...")
    io_data = load_io_table()
    fd = io_data["final_demand"]

    # Private consumption column (721)
    if "721" not in fd.columns:
        raise ValueError("Private consumption column '721' not found in IO table.")

    private_consumption = fd["721"]  # Series: sector_code → consumption value

    rows = {}
    for hh_code, cat in HH_CATEGORY_MAP.items():
        sector_values = {}
        for sec in cat["io_sectors"]:
            val = private_consumption.get(sec, 0.0)
            if val < 0:
                val = 0.0  # Some sectors have negative values (e.g., imputed rent correction)
            sector_values[sec] = val

        total = sum(sector_values.values())
        if total > 0:
            row = {sec: v / total for sec, v in sector_values.items()}
        else:
            row = {sec: 0.0 for sec in cat["io_sectors"]}

        rows[hh_code] = row

    # All IO sectors as columns
    all_sectors = io_data["sector_codes"]
    bridge = pd.DataFrame(rows).T.reindex(columns=all_sectors, fill_value=0.0)
    bridge.index.name = "hh_cat_code"

    bridge.to_csv(cache_path)
    print(f"Saved bridge matrix: {bridge.shape} to {cache_path}")
    return bridge


def compute_hh_category_import_content(force: bool = False) -> pd.DataFrame:
    """
    Compute import content for each household expenditure category.

    import_content_hh(cat) = sum_i B(cat, i) × import_content(i)

    force: キャッシュを無視して再計算（再現性検証用）

    Returns
    -------
    pd.DataFrame with columns: hh_cat_code, hh_cat_name, group,
                                import_content, pc_value_bn_jpy
    """
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = BRIDGE_DIR / "hh_category_import_content.csv"

    if cache_path.exists() and not force:
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    bridge = build_bridge_matrix(force=force)
    io_data = load_io_table()
    import_content = compute_import_content(io_data)

    # Private consumption values by IO sector (billion JPY)
    fd = io_data["final_demand"]
    pc = fd["721"].clip(lower=0)  # private consumption, non-negative

    rows = []
    for hh_code, cat in HH_CATEGORY_MAP.items():
        weights = bridge.loc[hh_code]

        # Import content for this category (weighted average of sector import contents)
        ic = (weights * import_content).sum()

        # Total private consumption value for this category's sectors (billion JPY)
        pc_value = sum(max(0, pc.get(sec, 0.0)) for sec in cat["io_sectors"])

        rows.append({
            "hh_cat_code": hh_code,
            "hh_cat_name": cat["name"],
            "group": cat["group"],
            "import_content": round(ic, 4),
            "pc_value_bn_jpy": round(pc_value, 2),
        })

    df = pd.DataFrame(rows).sort_values("import_content", ascending=False).reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    print(f"Saved: {cache_path}")
    return df


def classify_necessity_discretionary(force: bool = False) -> pd.DataFrame:
    """
    Classify household expenditure categories as necessity or discretionary.

    Jaravel (2019) approach: a category is a NECESSITY if the expenditure share
    in the lowest quintile (Q1) exceeds that in the highest quintile (Q5).

    Uses 家計調査 2019 (pre-COVID baseline) for classification.

    force: キャッシュを無視して再計算（再現性検証用）

    Returns
    -------
    pd.DataFrame with columns: hh_cat_code, hh_cat_name, group,
                                share_q1, share_q5, is_necessity, import_content
    """
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = BRIDGE_DIR / "necessity_classification.csv"

    if cache_path.exists() and not force:
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    hh_file = DATA_RAW / "household-survey" / "household_quintile_2015_2024.csv"
    hh = pd.read_csv(hh_file)

    # Filter to 2019 (pre-COVID baseline) and consumption expenditure categories
    hh_2019 = hh[hh["time_code"] == 2019000000].copy()

    # Get total consumption expenditure (cat01_code=59) per quintile for share calculation
    total_cons = (
        hh_2019[hh_2019["cat01_code"] == 59]
        .set_index("cat03_code")["value"]
        .to_dict()  # avoid Series ambiguity
    )

    # For each household category, get expenditure share by quintile
    ic_df = compute_hh_category_import_content(force=force)

    rows = []
    for _, cat_row in ic_df.iterrows():
        hh_code = int(cat_row["hh_cat_code"])

        # Get expenditure values for Q1 (cat03=1) and Q5 (cat03=5)
        cat_data = hh_2019[hh_2019["cat01_code"] == hh_code]

        q1_val = cat_data[cat_data["cat03_code"] == 1]["value"]
        q5_val = cat_data[cat_data["cat03_code"] == 5]["value"]

        if q1_val.empty or q5_val.empty:
            continue

        q1_val = q1_val.iloc[0]
        q5_val = q5_val.iloc[0]

        q1_total = total_cons.get(1, np.nan)
        q5_total = total_cons.get(5, np.nan)

        share_q1 = (float(q1_val) / float(q1_total)) if pd.notna(q1_total) and float(q1_total) > 0 else np.nan
        share_q5 = (float(q5_val) / float(q5_total)) if pd.notna(q5_total) and float(q5_total) > 0 else np.nan

        # Necessity if Q1 share > Q5 share (Engel criterion)
        is_necessity = share_q1 > share_q5 if pd.notna(share_q1) and pd.notna(share_q5) else None

        rows.append({
            "hh_cat_code": hh_code,
            "hh_cat_name": cat_row["hh_cat_name"],
            "group": cat_row["group"],
            "share_q1": round(share_q1, 4) if pd.notna(share_q1) else np.nan,
            "share_q5": round(share_q5, 4) if pd.notna(share_q5) else np.nan,
            "is_necessity": is_necessity,
            "import_content": cat_row["import_content"],
            "pc_value_bn_jpy": cat_row["pc_value_bn_jpy"],
        })

    df = pd.DataFrame(rows)
    df.to_csv(cache_path, index=False)
    print(f"Saved: {cache_path}")
    return df


if __name__ == "__main__":
    print("=== Bridge Matrix ===")
    bridge = build_bridge_matrix()
    print(f"Shape: {bridge.shape}")

    print("\n=== Import Content by Household Category ===")
    ic_df = compute_hh_category_import_content()
    print(ic_df[["hh_cat_name", "group", "import_content", "pc_value_bn_jpy"]].to_string(index=False))

    print("\n=== Necessity vs. Discretionary Classification (2019 base) ===")
    nd_df = classify_necessity_discretionary()
    print(nd_df[["hh_cat_name", "share_q1", "share_q5", "is_necessity", "import_content"]].to_string(index=False))
