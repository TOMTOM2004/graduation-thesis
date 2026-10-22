import pandas as pd
import pytest


def test_load_beta_empirical_prefers_canonical_producer_ic(tmp_path):
    from src.analysis.io_price_model import load_beta_empirical

    result = tmp_path / "sensitivity.csv"
    pd.DataFrame(
        {
            "ic_variant": [
                "ic_def1_producer",
                "ic_def2_producer",
                "ic_def2_purchaser",
            ],
            "specification": [
                "competitive_imports_excluded",
                "competitive_imports_excluded",
                "competitive_imports_excluded",
            ],
            "beta": [0.373, 0.633, 0.586],
        }
    ).to_csv(result, index=False)

    assert load_beta_empirical(result) == pytest.approx(0.633)


def test_load_beta_empirical_rejects_missing_canonical_variant(tmp_path):
    from src.analysis.io_price_model import load_beta_empirical

    result = tmp_path / "sensitivity.csv"
    pd.DataFrame(
        {
            "ic_variant": ["ic_def1_producer"],
            "specification": ["competitive_imports_excluded"],
            "beta": [0.373],
        }
    ).to_csv(result, index=False)

    with pytest.raises(RuntimeError, match="ic_def2_producer"):
        load_beta_empirical(result)
