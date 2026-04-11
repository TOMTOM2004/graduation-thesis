"""
Phase 1 Step 1-1: Import content analysis by commodity group.

Maps IO table sectors to 5 analysis groups (energy, metals, chemicals, food, wood)
and computes import content ratios via the Leontief framework.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.io_utils import (
    load_io_table,
    compute_input_coefficients,
    compute_leontief_inverse,
    compute_import_content,
)

DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed" / "import-content"

# Mapping from IO sector codes to 5 analysis groups
# Based on BOJ CGPI commodity classification for imports
SECTOR_GROUP_MAP: dict[str, str] = {
    # energy: 石油・石炭・天然ガス
    "061": "energy",  # 石炭・原油・天然ガス
    "211": "energy",  # 石油製品
    "212": "energy",  # 石炭製品
    "461": "energy",  # 電気（間接的なエネルギー）
    "462": "energy",  # ガス・熱供給
    # metals: 金属・同製品
    "261": "metals",  # 銑鉄・粗鋼
    "262": "metals",  # 鋼材
    "263": "metals",  # 鋳鍛造品（鉄）
    "269": "metals",  # その他の鉄鋼製品
    "271": "metals",  # 非鉄金属製錬・精製
    "272": "metals",  # 非鉄金属加工製品
    "281": "metals",  # 建設用・建築用金属製品
    "289": "metals",  # その他の金属製品
    # chemicals: 化学製品
    "201": "chemicals",  # 化学肥料
    "202": "chemicals",  # 無機化学工業製品
    "203": "chemicals",  # 石油化学系基礎製品
    "204": "chemicals",  # 有機化学工業製品
    "205": "chemicals",  # 合成樹脂
    "206": "chemicals",  # 化学繊維
    "207": "chemicals",  # 医薬品
    "208": "chemicals",  # 化学最終製品
    "221": "chemicals",  # プラスチック製品
    "222": "chemicals",  # ゴム製品
    # food: 飲食料品・食料用農水産物
    "011": "food",  # 耕種農業
    "012": "food",  # 畜産
    "017": "food",  # 漁業
    "111": "food",  # 食料品
    "112": "food",  # 飲料
    "113": "food",  # 飼料・有機質肥料
    "114": "food",  # たばこ
    # wood: 木材・木製品・林産物
    "015": "wood",  # 林業
    "161": "wood",  # 木材・木製品
    "162": "wood",  # 家具・装備品
    "163": "wood",  # パルプ・紙・板紙・加工紙
    "164": "wood",  # 紙加工品
}

GROUPS = ["energy", "metals", "chemicals", "food", "wood"]
GROUP_JA = {
    "energy": "石油・石炭・天然ガス",
    "metals": "金属・同製品",
    "chemicals": "化学製品",
    "food": "飲食料品・食料用農水産物",
    "wood": "木材・木製品・林産物",
}


def compute_sector_import_content() -> pd.DataFrame:
    """
    Compute import content ratio by IO sector and analysis group.

    Returns
    -------
    pd.DataFrame with columns: sector_code, sector_name, group, group_ja,
                                import_content, direct_import_ratio,
                                import_value_100mn_jpy
    """
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    cache_path = DATA_PROCESSED / "sector_import_content.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    print("Computing import content by sector...")
    io_data = load_io_table()

    import_content = compute_import_content(io_data)

    # Direct import penetration ratio
    x = io_data["output"]
    imports = io_data["imports"].abs()
    total_supply = x + imports
    direct_import_ratio = imports / total_supply.replace(0, np.inf)

    # Compile results
    rows = []
    sector_names = dict(zip(io_data["sector_codes"], io_data["sector_names"]))
    for code in io_data["sector_codes"]:
        rows.append({
            "sector_code": code,
            "sector_name": sector_names.get(code, ""),
            "group": SECTOR_GROUP_MAP.get(code, "other"),
            "group_ja": GROUP_JA.get(SECTOR_GROUP_MAP.get(code, "other"), "その他"),
            "import_content": import_content.get(code, np.nan),
            "direct_import_ratio": direct_import_ratio.get(code, np.nan),
            # IO table unit: billion JPY (十億円)
            "import_value_bn_jpy": imports.get(code, 0.0),
        })

    df = pd.DataFrame(rows)
    df.to_csv(cache_path, index=False)
    print(f"Saved to {cache_path} ({len(df)} rows)")
    return df


def compute_group_import_content() -> pd.DataFrame:
    """
    Aggregate import content and import values to 5 analysis groups.

    Returns
    -------
    pd.DataFrame with columns: group, group_ja, n_sectors,
                                import_value_total, import_value_share,
                                avg_import_content, avg_direct_ratio
    """
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    cache_path = DATA_PROCESSED / "group_import_content.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    sector_df = compute_sector_import_content()

    # Filter to 5 groups only
    in_scope = sector_df[sector_df["group"].isin(GROUPS)].copy()

    group_df = (
        in_scope.groupby(["group", "group_ja"])
        .agg(
            n_sectors=("sector_code", "count"),
            import_value_total=("import_value_bn_jpy", "sum"),
            avg_import_content=("import_content", "mean"),
            avg_direct_ratio=("direct_import_ratio", "mean"),
        )
        .reset_index()
    )

    total_import = in_scope["import_value_bn_jpy"].sum()
    group_df["import_value_share"] = group_df["import_value_total"] / total_import

    # Sort by import value (descending)
    group_df = group_df.sort_values("import_value_total", ascending=False).reset_index(drop=True)

    group_df.to_csv(cache_path, index=False)
    print(f"Saved to {cache_path}")
    return group_df


if __name__ == "__main__":
    sector_df = compute_sector_import_content()
    print("\n=== Sector Import Content (selected) ===")
    for group in GROUPS:
        sub = sector_df[sector_df["group"] == group]
        print(f"\n[{GROUP_JA[group]}] ({len(sub)} sectors)")
        print(sub[["sector_code", "sector_name", "direct_import_ratio", "import_content"]].to_string(index=False))

    print("\n=== Group-level Summary ===")
    group_df = compute_group_import_content()
    print(group_df[["group_ja", "n_sectors", "import_value_total", "import_value_share",
                     "avg_import_content"]].to_string(index=False))
