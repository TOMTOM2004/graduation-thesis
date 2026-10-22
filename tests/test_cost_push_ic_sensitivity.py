import pandas as pd
import pytest


def test_attach_ic_variants_recomputes_shift_share_for_each_variant():
    from src.analysis.cost_push_ic_sensitivity import attach_ic_variants

    panel = pd.DataFrame(
        {
            "cpi_mid_name": ["A", "B"],
            "year": [2022, 2022],
            "p_import": [150.0, 150.0],
            "delta_cpi": [2.0, 4.0],
        }
    )
    variants = pd.DataFrame(
        {
            "cpi_mid_name": ["A", "B"],
            "ic_def1_producer": [0.1, 0.2],
            "ic_def2_producer": [0.3, 0.4],
        }
    )

    out = attach_ic_variants(panel, variants)

    assert out["shift_share_ic_def1_producer"].tolist() == pytest.approx([5.0, 10.0])
    assert out["shift_share_ic_def2_producer"].tolist() == pytest.approx([15.0, 20.0])


def test_attach_ic_variants_rejects_unmatched_categories():
    from src.analysis.cost_push_ic_sensitivity import attach_ic_variants

    panel = pd.DataFrame(
        {
            "cpi_mid_name": ["A", "B"],
            "year": [2022, 2022],
            "p_import": [150.0, 150.0],
        }
    )
    variants = pd.DataFrame(
        {"cpi_mid_name": ["A"], "ic_def2_producer": [0.3]}
    )

    with pytest.raises(ValueError, match="Missing IC variants"):
        attach_ic_variants(panel, variants)


def test_yearly_correlations_are_computed_by_variant():
    from src.analysis.cost_push_ic_sensitivity import yearly_correlations

    panel = pd.DataFrame(
        {
            "year": [2022] * 4,
            "delta_cpi": [1.0, 2.0, 3.0, 4.0],
            "ic_a": [1.0, 2.0, 3.0, 4.0],
            "ic_b": [4.0, 3.0, 2.0, 1.0],
        }
    )

    out = yearly_correlations(panel, ["ic_a", "ic_b"])

    got = out.set_index("ic_variant")["correlation"].to_dict()
    assert got["ic_a"] == pytest.approx(1.0)
    assert got["ic_b"] == pytest.approx(-1.0)
