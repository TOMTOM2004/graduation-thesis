"""Unit tests for competitive-import input-output import-content definitions."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.utils.io_utils import (
    compute_import_content,
    compute_induced_import_content,
)
from src.analysis.bridge_matrix_mid import build_bridge_matrix_mid_from_io


def _toy_io(A: np.ndarray, output: list[float], imports: list[float]) -> dict:
    """Build the minimal ``load_io_table``-compatible object from a coefficient matrix."""
    codes = [f"{i + 1:03d}" for i in range(len(output))]
    x = pd.Series(output, index=codes, dtype=float)
    transaction = pd.DataFrame(A, index=codes, columns=codes).multiply(x, axis=1)
    return {
        "transaction": transaction,
        "output": x,
        "imports": pd.Series(imports, index=codes, dtype=float),
        "sector_codes": codes,
    }


def test_zero_imports_produce_zero_content_under_both_definitions() -> None:
    io = _toy_io(
        A=np.array([[0.1, 0.2], [0.0, 0.1]]),
        output=[100.0, 100.0],
        imports=[0.0, 0.0],
    )

    np.testing.assert_allclose(compute_import_content(io), [0.0, 0.0])
    np.testing.assert_allclose(compute_induced_import_content(io), [0.0, 0.0])


def test_fully_imported_final_good_has_unit_direct_import_content() -> None:
    io = _toy_io(
        A=np.array([[0.0]]),
        output=[0.0],
        imports=[10.0],
    )

    np.testing.assert_allclose(compute_import_content(io), [1.0])
    np.testing.assert_allclose(compute_induced_import_content(io), [1.0])


def test_induced_definition_matches_two_sector_hand_calculation() -> None:
    # Sector 1 has import penetration μ1=0.5 and supplies 0.5 units to sector 2.
    # Definition 1 discounts the imported-input chain twice:
    #   μ' Ld = [0.5, 0.5 * (1 - 0.5) * 0.5] = [0.5, 0.125].
    # Definition 2 counts direct final imports plus imported intermediate requirements:
    #   μ + (1-μ) * μ' A Ld = [0.5, 0.5 * 0.5] = [0.5, 0.25].
    io = _toy_io(
        A=np.array([[0.0, 0.5], [0.0, 0.0]]),
        output=[100.0, 100.0],
        imports=[100.0, 0.0],
    )

    np.testing.assert_allclose(compute_import_content(io), [0.5, 0.125])
    np.testing.assert_allclose(compute_induced_import_content(io), [0.5, 0.25])


def test_induced_group_components_sum_to_all_sector_content() -> None:
    io = _toy_io(
        A=np.array(
            [
                [0.0, 0.2, 0.1],
                [0.0, 0.0, 0.3],
                [0.0, 0.0, 0.0],
            ]
        ),
        output=[100.0, 100.0, 100.0],
        imports=[100.0, 25.0, 0.0],
    )

    total = compute_induced_import_content(io)
    group_1 = compute_induced_import_content(io, import_sector_mask=[True, False, False])
    group_2 = compute_induced_import_content(io, import_sector_mask=[False, True, False])
    group_3 = compute_induced_import_content(io, import_sector_mask=[False, False, True])

    np.testing.assert_allclose(group_1 + group_2 + group_3, total)


def test_missing_import_vector_is_rejected() -> None:
    io = _toy_io(A=np.array([[0.0]]), output=[1.0], imports=[0.0])
    io["imports"] = None

    for fn in (compute_import_content, compute_induced_import_content):
        try:
            fn(io)
        except ValueError as exc:
            assert "Import data not found" in str(exc)
        else:
            raise AssertionError(f"{fn.__name__} accepted an IO table without imports")


def test_bridge_weights_use_selected_valuation_private_consumption() -> None:
    io = _toy_io(
        A=np.zeros((2, 2)),
        output=[100.0, 100.0],
        imports=[0.0, 0.0],
    )
    io["final_demand"] = pd.DataFrame(
        {"721": [25.0, 75.0]},
        index=io["sector_codes"],
    )
    category_map = {
        "test category": {
            "io_sectors": io["sector_codes"],
        }
    }

    bridge = build_bridge_matrix_mid_from_io(io, category_map=category_map)

    np.testing.assert_allclose(bridge.loc["test category"], [0.25, 0.75])
    assert bridge.loc["test category"].sum() == 1.0
