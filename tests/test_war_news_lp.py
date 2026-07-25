import numpy as np
import pandas as pd
import pytest


def _monthly_series(n: int = 120) -> pd.Series:
    idx = pd.date_range("2000-01-01", periods=n, freq="MS")
    values = 2.0 + np.sin(np.arange(n) / 6.0)
    for position, increment in [(30, 4.0), (65, 7.0), (90, 5.0)]:
        if position < n:
            values[position] += increment
    return pd.Series(values, index=idx)


def test_recursive_ar_innovation_does_not_use_future_observations():
    from src.analysis.war_news_lp import recursive_ar_innovation

    original = _monthly_series()
    extended = pd.concat(
        [
            original,
            pd.Series(
                [1000.0, 2000.0],
                index=pd.date_range("2010-01-01", periods=2, freq="MS"),
            ),
        ]
    )

    base = recursive_ar_innovation(original, lags=2, min_train=20)
    with_future = recursive_ar_innovation(extended, lags=2, min_train=20)

    pd.testing.assert_series_equal(base, with_future.reindex(base.index))


def test_prepare_war_news_shock_uses_directed_russia_to_ukraine_index():
    from src.analysis.war_news_lp import prepare_war_news_shock

    idx = pd.date_range("1990-01-01", periods=100, freq="MS")
    frame = pd.DataFrame(
        {
            "Date": idx,
            "Russia|Ukraine": np.linspace(0.0, 20.0, len(idx)),
            "Ukraine|Russia": np.full(len(idx), 999.0),
        }
    )

    shock = prepare_war_news_shock(frame, lags=2, min_train=20)
    changed_reverse = frame.copy()
    changed_reverse["Ukraine|Russia"] = 0.0
    shock_changed_reverse = prepare_war_news_shock(
        changed_reverse, lags=2, min_train=20
    )

    pd.testing.assert_series_equal(shock, shock_changed_reverse)
    assert shock.name == "russia_ukraine_news_innovation"
    assert shock.dropna().index.min() > idx.min()


def test_feasibility_gate_separates_data_feasibility_from_causal_identification():
    from src.analysis.war_news_lp import feasibility_gate

    shock = _monthly_series(252)

    exploratory = feasibility_gate(
        shock,
        identified_externally=False,
        min_observations=120,
    )
    causal = feasibility_gate(
        shock,
        identified_externally=True,
        min_observations=120,
    )

    assert exploratory["data_gate"] == "PASS"
    assert exploratory["causal_gate"] == "FAIL"
    assert exploratory["analysis_tier"] == "exploratory"
    assert causal["causal_gate"] == "PASS"
    assert causal["analysis_tier"] == "causal_candidate"


def test_feasibility_gate_fails_when_effective_sample_is_too_short():
    from src.analysis.war_news_lp import feasibility_gate

    result = feasibility_gate(
        _monthly_series(24),
        identified_externally=True,
        min_observations=120,
    )

    assert result["data_gate"] == "FAIL"
    assert result["causal_gate"] == "FAIL"
    assert result["analysis_tier"] == "descriptive_only"


def test_joint_lp_recovers_two_independent_contemporaneous_shocks():
    from src.analysis.war_news_lp import run_joint_lp

    rng = np.random.default_rng(42)
    idx = pd.date_range("2000-01-01", periods=240, freq="MS")
    oil = pd.Series(rng.normal(size=len(idx)), index=idx)
    war = pd.Series(rng.normal(size=len(idx)), index=idx)
    monthly_change = 2.0 * oil + 3.0 * war + rng.normal(scale=0.05, size=len(idx))
    level = monthly_change.cumsum()

    result = run_joint_lp(
        level,
        {"oil": oil, "war": war},
        start="2001-01-01",
        end="2019-12-01",
        h_max=0,
        n_lags=2,
        standardize=False,
    )

    row = result.iloc[0]
    assert row["beta_oil"] == pytest.approx(2.0, abs=0.08)
    assert row["beta_war"] == pytest.approx(3.0, abs=0.08)


def test_shock_concentration_reports_effective_event_count():
    from src.analysis.war_news_lp import shock_concentration

    idx = pd.date_range("2020-01-01", periods=4, freq="MS")
    metrics = shock_concentration(pd.Series([2.0, 0.0, 0.0, 0.0], index=idx))

    assert metrics["top1_squared_share"] == pytest.approx(1.0)
    assert metrics["effective_event_count"] == pytest.approx(1.0)
