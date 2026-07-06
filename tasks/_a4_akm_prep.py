"""A-4: AKM入力（_akm_cross.csv）の再生成コード。

tasks/_a4_akm.R / _a4_akm2.R の入力を再生成（DEC-019: 生成コード欠落の解消）。

data/processed/price-indices/_akm_cross.csv は実在するが、それを作った生成コードが
リポジトリに存在しなかった。本スクリプトは以下の手順でそれを再生成する:

入力:
  - data/processed/price-indices/panel_groupspec.csv
      （tasks/_a4_groupspec.py が出力。列: cpi_mid_name, year, delta_cpi, ic_energy..ic_wood ほか）
  - data/processed/trade-loss/annual_price_index.csv
      （src/analysis/trade_loss.py compute_annual_price_index() が出力。列: year, group, price_index）

手順:
  1. panel_groupspec の year==2022 断面を取る
  2. y = delta_cpi
  3. ic_{g} 5列（g in GROUPS）はそのまま転記
  4. dp_{g} = annual_price_index の (g, 2022) 行の price_index − 100.0（全行同値）

出力: data/processed/price-indices/_akm_cross.csv
列順: cpi_mid_name, y, ic_energy, ic_metals, ic_chemicals, ic_food, ic_wood,
      dp_energy, dp_metals, dp_chemicals, dp_food, dp_wood

このスクリプトは実行しない（Phase 3 で実行担当者が実行する）。
--check オプション: 本体ツリーの既存 _akm_cross.csv と再生成結果を比較し、
float は np.allclose、行順・行数一致を確認して PASS/FAIL を出力する。
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.analysis.import_content import GROUPS

DATA_PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"
PRICE_DIR = DATA_PROCESSED / "price-indices"

PANEL_GROUPSPEC_PATH = PRICE_DIR / "panel_groupspec.csv"
ANNUAL_PRICE_INDEX_PATH = DATA_PROCESSED / "trade-loss" / "annual_price_index.csv"
OUTPUT_PATH = PRICE_DIR / "_akm_cross.csv"

TARGET_YEAR = 2022

COLUMN_ORDER = (
    ["cpi_mid_name", "y"]
    + [f"ic_{g}" for g in GROUPS]
    + [f"dp_{g}" for g in GROUPS]
)


def build_akm_cross(year: int = TARGET_YEAR) -> pd.DataFrame:
    """panel_groupspec.csv + annual_price_index.csv から _akm_cross.csv 相当を再構築する。"""
    panel = pd.read_csv(PANEL_GROUPSPEC_PATH)
    cross = panel[panel["year"] == year].copy()

    annual = pd.read_csv(ANNUAL_PRICE_INDEX_PATH)
    p_t = annual[annual["year"] == year].set_index("group")["price_index"].to_dict()

    cross["y"] = cross["delta_cpi"]
    for g in GROUPS:
        if g not in p_t:
            raise RuntimeError(
                f"annual_price_index.csv に year={year} group={g} の行が無い"
            )
        cross[f"dp_{g}"] = p_t[g] - 100.0

    cross = cross[COLUMN_ORDER].reset_index(drop=True)
    return cross


def check_against_existing(rebuilt: pd.DataFrame) -> bool:
    """既存の _akm_cross.csv と再生成結果を比較し、一致すれば True。"""
    if not OUTPUT_PATH.exists():
        print(f"FAIL: 既存ファイルが無い: {OUTPUT_PATH}")
        return False

    existing = pd.read_csv(OUTPUT_PATH)

    if len(existing) != len(rebuilt):
        print(f"FAIL: 行数不一致（既存={len(existing)} / 再生成={len(rebuilt)}）")
        return False

    if list(existing.columns) != list(rebuilt.columns):
        print(f"FAIL: 列不一致（既存={list(existing.columns)} / 再生成={list(rebuilt.columns)}）")
        return False

    if not existing["cpi_mid_name"].equals(rebuilt["cpi_mid_name"]):
        print("FAIL: cpi_mid_name の行順が不一致")
        return False

    numeric_cols = [c for c in existing.columns if c != "cpi_mid_name"]
    ok = np.allclose(
        existing[numeric_cols].to_numpy(dtype=float),
        rebuilt[numeric_cols].to_numpy(dtype=float),
        equal_nan=True,
    )
    if not ok:
        print("FAIL: 数値列が一致しない")
        return False

    print(f"PASS: {OUTPUT_PATH} と再生成結果は一致（{len(existing)} 行）")
    return True


def main() -> None:
    rebuilt = build_akm_cross()

    if "--check" in sys.argv:
        ok = check_against_existing(rebuilt)
        sys.exit(0 if ok else 1)

    # 実行はしない方針だが、明示的に --write を渡された場合のみ上書き保存する
    if "--write" in sys.argv:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        rebuilt.to_csv(OUTPUT_PATH, index=False)
        print(f"Saved: {OUTPUT_PATH} ({len(rebuilt)} rows)")
    else:
        print(rebuilt.to_string(index=False))
        print("\n(--write を渡すと data/processed/price-indices/_akm_cross.csv に保存)")
        print("(--check を渡すと既存ファイルとの一致検証のみ行う)")


if __name__ == "__main__":
    main()
