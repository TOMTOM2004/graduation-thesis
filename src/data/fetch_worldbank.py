"""
Fetch World Bank indicator series (API v2) used for the cross-country / industry-structure
comparison analyses.

既存 raw は 2026-06 に手動 curl 取得。本スクリプトはその再現手段（DEC-019）。

対象ファイルと indicator の対応表:

    data/raw/crosscountry/cpi.json                          FP.CPI.TOTL.ZG      (Inflation, consumer prices, annual %)
    data/raw/crosscountry/0.json                             FP.CPI.TOTL.ZG      (cpi.json と同一内容。手動取得時の重複/レガシーファイル。再取得は cpi.json 側で代替可)
    data/raw/crosscountry/eimp.json                          EG.IMP.CONS.ZS      (Energy imports, net, % of energy use)
    data/raw/crosscountry/fuelimp.json                       TM.VAL.FUEL.ZS.UN   (Fuel imports, % of merchandise imports)
    data/raw/crosscountry/gdppc.json                         NY.GDP.PCAP.KD      (GDP per capita, constant 2015 US$)
    data/raw/crosscountry/mfgva.json                         NV.IND.MANF.ZS      (Manufacturing, value added, % of GDP)
    data/raw/crosscountry/tot.json                           TT.PRI.MRCH.XD.WD   (Net barter terms of trade index, 2015=100)
    data/raw/crosscountry/trade.json                         NE.TRD.GNFS.ZS      (Trade, % of GDP)
    data/raw/industry-structure/wb_NE.IMP.GNFS.ZS.json       NE.IMP.GNFS.ZS      (Imports of goods and services, % of GDP; Japan only)
    data/raw/industry-structure/wb_NV.IND.MANF.ZS.json       NV.IND.MANF.ZS      (Manufacturing, value added, % of GDP; Japan only)
    data/raw/industry-structure/wb_SL.IND.EMPL.ZS.json       SL.IND.EMPL.ZS      (Employment in industry, % of total employment; Japan only)

crosscountry/* は country=all（全世界パネル、per_page=4000）、
industry-structure/wb_* は country=JP（日本単独の時系列、per_page=500）で取得している。

このスクリプトは実行しない（既存 raw を上書きしないこと・再現手段としての提供のみ）。
実行する場合: `python -m src.data.fetch_worldbank --force` で全ファイルを再取得する。
"""

from pathlib import Path

import httpx

DATA_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
CROSSCOUNTRY_DIR = DATA_RAW / "crosscountry"
INDUSTRY_STRUCTURE_DIR = DATA_RAW / "industry-structure"

WB_API_BASE = "https://api.worldbank.org/v2/country"

# indicator 定義: 出力ファイル → (indicator code, country scope, per_page)
INDICATORS: dict[str, dict] = {
    "crosscountry/cpi.json": {
        "code": "FP.CPI.TOTL.ZG",
        "country": "all",
        "per_page": 4000,
    },
    "crosscountry/eimp.json": {
        "code": "EG.IMP.CONS.ZS",
        "country": "all",
        "per_page": 4000,
    },
    "crosscountry/fuelimp.json": {
        "code": "TM.VAL.FUEL.ZS.UN",
        "country": "all",
        "per_page": 4000,
    },
    "crosscountry/gdppc.json": {
        "code": "NY.GDP.PCAP.KD",
        "country": "all",
        "per_page": 4000,
    },
    "crosscountry/mfgva.json": {
        "code": "NV.IND.MANF.ZS",
        "country": "all",
        "per_page": 4000,
    },
    "crosscountry/tot.json": {
        "code": "TT.PRI.MRCH.XD.WD",
        "country": "all",
        "per_page": 4000,
    },
    "crosscountry/trade.json": {
        "code": "NE.TRD.GNFS.ZS",
        "country": "all",
        "per_page": 4000,
    },
    "industry-structure/wb_NE.IMP.GNFS.ZS.json": {
        "code": "NE.IMP.GNFS.ZS",
        "country": "JP",
        "per_page": 500,
    },
    "industry-structure/wb_NV.IND.MANF.ZS.json": {
        "code": "NV.IND.MANF.ZS",
        "country": "JP",
        "per_page": 500,
    },
    "industry-structure/wb_SL.IND.EMPL.ZS.json": {
        "code": "SL.IND.EMPL.ZS",
        "country": "JP",
        "per_page": 500,
    },
}

DEFAULT_YEAR_RANGE = (1960, 2026)


def fetch_indicator(
    indicator_code: str,
    country: str = "all",
    year_range: tuple[int, int] = DEFAULT_YEAR_RANGE,
    per_page: int = 4000,
    out_path: Path | None = None,
    force: bool = False,
) -> Path:
    """
    Fetch one World Bank indicator series and save as raw JSON
    (World Bank API v2 [metadata, data] 形式のまま保存).

    force: 既存ファイルがあっても再取得する（再現性検証用。デフォルトは既存 raw を保護して skip）。

    Returns
    -------
    Path to the saved JSON file.
    """
    if out_path is None:
        out_path = DATA_RAW / "crosscountry" / f"{indicator_code}.json"

    if out_path.exists() and not force:
        print(f"Already exists (skip): {out_path}")
        return out_path

    date_param = f"{year_range[0]}:{year_range[1]}"
    url = f"{WB_API_BASE}/{country}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": per_page, "date": date_param}

    print(f"Fetching {indicator_code} (country={country}, date={date_param})...")
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.content)
    print(f"Saved to {out_path} ({len(resp.content) / 1024:.1f} KB)")
    return out_path


def main(force: bool = False) -> None:
    """
    Re-fetch all existing World Bank raw JSON files listed in INDICATORS.

    デフォルト（force=False）では既存ファイルが保護され再取得されない。
    明示的に force=True（または --force）を渡した場合のみ上書き取得する。
    """
    for rel_path, spec in INDICATORS.items():
        out_path = DATA_RAW / rel_path
        fetch_indicator(
            indicator_code=spec["code"],
            country=spec["country"],
            per_page=spec["per_page"],
            out_path=out_path,
            force=force,
        )


if __name__ == "__main__":
    import sys

    main(force="--force" in sys.argv)
