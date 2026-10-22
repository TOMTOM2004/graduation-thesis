"""Fetch the public AI-GPR directed bilateral monthly index.

Source:
Iacoviello, Matteo and Jonathan Tong (2026), "The AI-GPR Index:
Measuring Geopolitical Risk using Artificial Intelligence."

The raw file is write-once: an existing destination is validated and never
overwritten, consistent with the repository's immutable ``data/raw`` rule.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
URL = (
    "https://www.matteoiacoviello.com/ai_gpr_files/"
    "ai_gpr_bilateral_monthly.csv"
)
DESTINATION = (
    ROOT / "data" / "raw" / "war-news" / "ai_gpr_bilateral_monthly.csv"
)
REQUIRED_COLUMNS = {"Date", "Russia|Ukraine", "Ukraine|Russia"}


def validate_bilateral_gpr(frame: pd.DataFrame) -> dict[str, object]:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    dates = pd.to_datetime(frame["Date"])
    if dates.duplicated().any():
        raise ValueError("Date contains duplicates")
    if not dates.is_monotonic_increasing:
        raise ValueError("Date must be sorted")
    expected = pd.date_range(dates.min(), dates.max(), freq="MS")
    if not dates.reset_index(drop=True).equals(pd.Series(expected)):
        raise ValueError("Date must be a complete monthly-start sequence")
    if dates.min() > pd.Timestamp("1960-01-01"):
        raise ValueError("series starts later than the documented 1960 coverage")
    if dates.max() < pd.Timestamp("2025-12-01"):
        raise ValueError("series ends before the documented 2025 coverage")

    for column in REQUIRED_COLUMNS - {"Date"}:
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any() or (values < 0).any():
            raise ValueError(f"{column} must be complete and non-negative")

    return {
        "start": dates.min(),
        "end": dates.max(),
        "n_months": int(len(dates)),
    }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch() -> Path:
    if DESTINATION.exists():
        validate_bilateral_gpr(pd.read_csv(DESTINATION))
        print(f"Raw file already exists; preserved: {DESTINATION}")
        print(f"sha256={file_sha256(DESTINATION)}")
        return DESTINATION

    response = requests.get(URL, timeout=60)
    response.raise_for_status()
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    temporary = DESTINATION.with_suffix(".tmp")
    temporary.write_bytes(response.content)
    try:
        validate_bilateral_gpr(pd.read_csv(temporary))
        temporary.replace(DESTINATION)
    finally:
        if temporary.exists():
            temporary.unlink()

    print(f"Saved immutable raw file: {DESTINATION}")
    print(f"sha256={file_sha256(DESTINATION)}")
    return DESTINATION


if __name__ == "__main__":
    fetch()
