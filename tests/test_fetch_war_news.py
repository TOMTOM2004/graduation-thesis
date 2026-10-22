import pandas as pd
import pytest


def test_validate_bilateral_gpr_accepts_complete_public_schema():
    from src.data.fetch_war_news import validate_bilateral_gpr

    dates = pd.date_range("1960-01-01", "2025-12-01", freq="MS")
    frame = pd.DataFrame(
        {
            "Date": dates,
            "Russia|Ukraine": 0.0,
            "Ukraine|Russia": 0.0,
        }
    )

    result = validate_bilateral_gpr(frame)

    assert result["start"] == pd.Timestamp("1960-01-01")
    assert result["end"] == pd.Timestamp("2025-12-01")
    assert result["n_months"] == len(dates)


def test_validate_bilateral_gpr_rejects_missing_directed_pair():
    from src.data.fetch_war_news import validate_bilateral_gpr

    frame = pd.DataFrame(
        {
            "Date": pd.date_range("1960-01-01", periods=800, freq="MS"),
            "Russia|Ukraine": 0.0,
        }
    )

    with pytest.raises(ValueError, match="missing columns"):
        validate_bilateral_gpr(frame)
