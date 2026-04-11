"""
CPI 中分類版ブリッジ行列 + 輸入含有率計算。

既存 bridge_matrix.py の大分類版（10カテゴリー）を
CPI 中分類（41カテゴリー）に拡張した新規モジュール。
下流の cost_push_panel.py で使用する。

既存コードへの影響ゼロ（別ファイル）。
"""

from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.io_utils import load_io_table, compute_import_content

DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"
BRIDGE_DIR = DATA_PROCESSED / "bridge-matrix"

# CPI 中分類 → IO 108部門 マッピング
# key: CPI cat01_name（日本語名）
# cpi_code: cat01_code (4桁ゼロ埋め文字列)
# io_sectors: IO 統合中分類のセクターコード（3桁文字列）
# group: 大分類グループ名
# is_transport_comms: True = 交通・通信（感度分析で除外対象）

CPI_MID_CATEGORY_MAP: dict[str, dict] = {
    # === 食料 (12カテゴリー) ===
    "穀類": {
        "cpi_code": "0003",
        "io_sectors": ["011", "111"],
        "group": "food",
        "is_transport_comms": False,
    },
    "魚介類": {
        "cpi_code": "0008",
        "io_sectors": ["017", "111"],
        "group": "food",
        "is_transport_comms": False,
    },
    "肉類": {
        "cpi_code": "0013",
        "io_sectors": ["012", "111"],
        "group": "food",
        "is_transport_comms": False,
    },
    "乳卵類": {
        "cpi_code": "0016",
        "io_sectors": ["012", "111"],
        "group": "food",
        "is_transport_comms": False,
    },
    "野菜・海藻": {
        "cpi_code": "0021",
        "io_sectors": ["011", "111"],
        "group": "food",
        "is_transport_comms": False,
    },
    "果物": {
        "cpi_code": "0027",
        "io_sectors": ["011", "111"],
        "group": "food",
        "is_transport_comms": False,
    },
    "油脂・調味料": {
        "cpi_code": "0030",
        "io_sectors": ["111", "201", "204"],  # 食料品, 基礎化学, 油脂加工
        "group": "food",
        "is_transport_comms": False,
    },
    "菓子類": {
        "cpi_code": "0033",
        "io_sectors": ["111", "112"],
        "group": "food",
        "is_transport_comms": False,
    },
    "調理食品": {
        "cpi_code": "0034",
        "io_sectors": ["111"],
        "group": "food",
        "is_transport_comms": False,
    },
    "飲料": {
        "cpi_code": "0037",
        "io_sectors": ["112", "111"],
        "group": "food",
        "is_transport_comms": False,
    },
    "酒類": {
        "cpi_code": "0041",
        "io_sectors": ["112"],
        "group": "food",
        "is_transport_comms": False,
    },
    "外食": {
        "cpi_code": "0042",
        "io_sectors": ["671", "111"],  # 宿泊・飲食, 食料品
        "group": "food",
        "is_transport_comms": False,
    },
    # === 住居 (2カテゴリー) ===
    "家賃": {
        "cpi_code": "0046",
        "io_sectors": ["552"],  # 住宅賃貸料
        "group": "housing",
        "is_transport_comms": False,
    },
    "設備修繕・維持": {
        "cpi_code": "0051",
        "io_sectors": ["411", "412"],  # 建設, 修繕
        "group": "housing",
        "is_transport_comms": False,
    },
    # === 光熱・水道 (4カテゴリー) ===
    "電気代": {
        "cpi_code": "0056",
        "io_sectors": ["461"],  # 電気
        "group": "energy",
        "is_transport_comms": False,
    },
    "ガス代": {
        "cpi_code": "0057",
        "io_sectors": ["462"],  # ガス・熱供給
        "group": "energy",
        "is_transport_comms": False,
    },
    "他の光熱": {
        "cpi_code": "0058",
        "io_sectors": ["211", "212"],  # 石油製品, 石炭製品（灯油・プロパン）
        "group": "energy",
        "is_transport_comms": False,
    },
    "上下水道料": {
        "cpi_code": "0059",
        "io_sectors": ["471"],  # 水道
        "group": "energy",
        "is_transport_comms": False,
    },
    # === 家具・家事用品 (4カテゴリー) ===
    "家庭用耐久財": {
        "cpi_code": "0061",
        "io_sectors": ["162", "281", "391"],  # 家具, 金属, その他製造
        "group": "furniture",
        "is_transport_comms": False,
    },
    "室内装備品": {
        "cpi_code": "0073",
        "io_sectors": ["162", "281", "221"],  # 家具, 金属, ゴム
        "group": "furniture",
        "is_transport_comms": False,
    },
    "家事用消耗品": {
        "cpi_code": "0077",
        "io_sectors": ["221", "208", "222"],  # ゴム, 化学, プラスチック
        "group": "furniture",
        "is_transport_comms": False,
    },
    "家事サービス": {
        "cpi_code": "0081",
        "io_sectors": ["679"],  # 対個人サービス
        "group": "furniture",
        "is_transport_comms": False,
    },
    # === 被服及び履物 (3カテゴリー) ===
    "衣料": {
        "cpi_code": "0083",
        "io_sectors": ["151", "152"],  # 繊維, 衣服・繊維製品
        "group": "clothing",
        "is_transport_comms": False,
    },
    "履物類": {
        "cpi_code": "0098",
        "io_sectors": ["152", "231"],  # 衣服・繊維製品, 窯業・土石（革）
        "group": "clothing",
        "is_transport_comms": False,
    },
    "被服関連サービス": {
        "cpi_code": "0106",
        "io_sectors": ["679"],  # クリーニング等
        "group": "clothing",
        "is_transport_comms": False,
    },
    # === 保健医療 (3カテゴリー) ===
    "医薬品・健康保持用摂取品": {
        "cpi_code": "0108",
        "io_sectors": ["207", "208"],  # 医薬品, 農薬・その他化学
        "group": "health",
        "is_transport_comms": False,
    },
    "保健医療用品・器具": {
        "cpi_code": "0109",
        "io_sectors": ["391", "207"],  # その他製造（医療機器等）, 医薬品
        "group": "health",
        "is_transport_comms": False,
    },
    "保健医療サービス": {
        "cpi_code": "0110",
        "io_sectors": ["641", "642"],  # 医療, 保健衛生
        "group": "health",
        "is_transport_comms": False,
    },
    # === 交通・通信 (通信を分離, 3カテゴリー) ===
    "交通": {
        "cpi_code": "0112",
        "io_sectors": ["571", "572", "575"],  # 鉄道, 道路輸送, 航空
        "group": "transport",
        "is_transport_comms": False,
    },
    "自動車等関係費": {
        "cpi_code": "0113",
        "io_sectors": ["351", "352", "353"],  # 乗用車, 自動車部品, 二輪車
        "group": "transport",
        "is_transport_comms": False,
    },
    "通信": {
        "cpi_code": "0117",
        "io_sectors": ["591"],  # 通信（携帯料金政策の外れ値あり）
        "group": "comms",
        "is_transport_comms": True,  # 感度分析で除外対象
    },
    # === 教育 (3カテゴリー) ===
    "授業料等": {
        "cpi_code": "0119",
        "io_sectors": ["631"],  # 教育
        "group": "education",
        "is_transport_comms": False,
    },
    "教科書・学習参考教材": {
        "cpi_code": "0120",
        "io_sectors": ["163", "164"],  # パルプ・紙, 印刷
        "group": "education",
        "is_transport_comms": False,
    },
    "補習教育": {
        "cpi_code": "0121",
        "io_sectors": ["631"],  # 教育
        "group": "education",
        "is_transport_comms": False,
    },
    # === 教養娯楽 (5カテゴリー) ===
    "教養娯楽用耐久財": {
        "cpi_code": "0123",
        "io_sectors": ["595", "391"],  # 映像・音声機器, その他製造
        "group": "recreation",
        "is_transport_comms": False,
    },
    "教養娯楽用品": {
        "cpi_code": "0128",
        "io_sectors": ["163", "164", "391"],  # 紙, 印刷, その他製造
        "group": "recreation",
        "is_transport_comms": False,
    },
    "書籍・他の印刷物": {
        "cpi_code": "0134",
        "io_sectors": ["163", "164"],  # パルプ・紙, 印刷
        "group": "recreation",
        "is_transport_comms": False,
    },
    "教養娯楽サービス": {
        "cpi_code": "0138",
        "io_sectors": ["671", "672", "674"],  # 宿泊・飲食, 娯楽, その他娯楽
        "group": "recreation",
        "is_transport_comms": False,
    },
    "放送受信料": {
        "cpi_code": "0142",
        "io_sectors": ["595", "591"],  # 映像・音声, 通信
        "group": "recreation",
        "is_transport_comms": False,
    },
    # === 諸雑費・その他 (2カテゴリー) ===
    "理美容サービス": {
        "cpi_code": "0146",
        "io_sectors": ["673"],  # 理美容
        "group": "other",
        "is_transport_comms": False,
    },
    "パック旅行費": {
        "cpi_code": "0177",
        "io_sectors": ["571", "572", "675"],  # 鉄道, 道路, 旅行業
        "group": "other",
        "is_transport_comms": False,
    },
}

# cpi_code → name の逆引き辞書
CPI_CODE_TO_NAME: dict[str, str] = {
    v["cpi_code"]: k for k, v in CPI_MID_CATEGORY_MAP.items()
}


def build_bridge_matrix_mid() -> pd.DataFrame:
    """
    Build bridge matrix for CPI middle categories.

    B(cpi_mid_name, io_sector) = weight of IO sector in that CPI category,
    derived from IO private consumption column (column "721").

    Returns
    -------
    pd.DataFrame: index=cpi_mid_name, columns=IO sector codes,
                  values=share of that sector's consumption within the category
    Cache: data/processed/bridge-matrix/bridge_matrix_mid.csv
    """
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = BRIDGE_DIR / "bridge_matrix_mid.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path, index_col=0)

    print("Building mid-level bridge matrix from IO private consumption column...")
    io_data = load_io_table()
    fd = io_data["final_demand"]

    if "721" not in fd.columns:
        raise ValueError("Private consumption column '721' not found in IO table.")

    private_consumption = fd["721"]

    rows = {}
    for cat_name, cat in CPI_MID_CATEGORY_MAP.items():
        sector_values = {}
        for sec in cat["io_sectors"]:
            val = private_consumption.get(sec, 0.0)
            sector_values[sec] = max(0.0, val)

        total = sum(sector_values.values())
        if total > 0:
            row = {sec: v / total for sec, v in sector_values.items()}
        else:
            row = {sec: 0.0 for sec in cat["io_sectors"]}
        rows[cat_name] = row

    all_sectors = io_data["sector_codes"]
    bridge = pd.DataFrame(rows).T.reindex(columns=all_sectors, fill_value=0.0)
    bridge.index.name = "cpi_mid_name"

    bridge.to_csv(cache_path)
    print(f"Saved mid bridge matrix: {bridge.shape} to {cache_path}")
    return bridge


def compute_mid_category_import_content() -> pd.DataFrame:
    """
    Compute import content (IC_c) for each CPI middle category.

    IC_c = Σ_i  B_mid(c, i) × import_content(i)

    Returns
    -------
    pd.DataFrame with columns:
        cpi_mid_name, cpi_code, group, is_transport_comms,
        import_content,    # IC_c: [0, 1]
        pc_value_bn_jpy    # IO private consumption value (billion JPY)
    Cache: data/processed/bridge-matrix/mid_category_import_content.csv
    """
    BRIDGE_DIR.mkdir(parents=True, exist_ok=True)
    cache_path = BRIDGE_DIR / "mid_category_import_content.csv"

    if cache_path.exists():
        print(f"Loading cached: {cache_path}")
        return pd.read_csv(cache_path)

    bridge = build_bridge_matrix_mid()
    io_data = load_io_table()
    import_content = compute_import_content(io_data)

    fd = io_data["final_demand"]
    pc = fd["721"].clip(lower=0)

    rows = []
    for cat_name, cat in CPI_MID_CATEGORY_MAP.items():
        weights = bridge.loc[cat_name]
        ic = (weights * import_content).sum()
        pc_value = sum(max(0.0, pc.get(sec, 0.0)) for sec in cat["io_sectors"])

        rows.append({
            "cpi_mid_name": cat_name,
            "cpi_code": cat["cpi_code"],
            "group": cat["group"],
            "is_transport_comms": cat["is_transport_comms"],
            "import_content": round(ic, 4),
            "pc_value_bn_jpy": round(pc_value, 2),
        })

    df = pd.DataFrame(rows).sort_values("import_content", ascending=False).reset_index(drop=True)
    df.to_csv(cache_path, index=False)
    print(f"Saved mid category import content: {cache_path} ({len(df)} rows)")
    return df


if __name__ == "__main__":
    print("=== Mid-Category Import Content (IC_c) ===")
    ic_df = compute_mid_category_import_content()
    print(ic_df[["cpi_mid_name", "group", "import_content", "is_transport_comms"]].to_string(index=False))
    print(f"\nIC range: {ic_df['import_content'].min():.3f} – {ic_df['import_content'].max():.3f}")
    print(f"IC std: {ic_df['import_content'].std():.3f}")
    print(f"n categories: {len(ic_df)}")
