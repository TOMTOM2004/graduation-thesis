"""Downstream sensitivity of the cost-push analysis to IC definition and valuation.

The four IC variants are:

- definition 1: ``mu.T @ Ld``
- definition 2: ``mu + (1-mu) * (mu.T @ A @ Ld)`` (induced-import IC)
- producer-price IO table
- purchaser-price IO table

This module does not promote the panel association to a causal estimate.  It
checks whether the previously documented coefficient, yearly correlations, and
goods/services decomposition survive the IC correction.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analysis.ic_valuation_sensitivity import compute_category_sensitivity


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "processed" / "price-indices"

VARIANT_COLUMNS = [
    "ic_def1_producer",
    "ic_def2_producer",
    "ic_def1_purchaser",
    "ic_def2_purchaser",
]
SHOCK_YEARS = (2021, 2024)
PLACEBO_YEARS = (2015, 2019)


def build_ic_variant_table() -> pd.DataFrame:
    """Return one row per CPI middle category with the four IC variants."""
    category, _ = compute_category_sensitivity()
    wide = category.pivot(
        index="cpi_mid_name",
        columns=["definition", "valuation"],
        values="import_content",
    )
    wide.columns = [
        {
            ("definition1_muT_Ld", "producer"): "ic_def1_producer",
            ("definition2_induced", "producer"): "ic_def2_producer",
            ("definition1_muT_Ld", "purchaser"): "ic_def1_purchaser",
            ("definition2_induced", "purchaser"): "ic_def2_purchaser",
        }[column]
        for column in wide.columns
    ]
    return wide.reset_index()[["cpi_mid_name", *VARIANT_COLUMNS]]


def attach_ic_variants(panel: pd.DataFrame, variants: pd.DataFrame) -> pd.DataFrame:
    """Attach IC variants and rebuild each shift-share regressor."""
    variant_columns = [column for column in variants if column.startswith("ic_")]
    merged = panel.drop(
        columns=["ic", "shift_share", *variant_columns], errors="ignore"
    ).merge(variants, on="cpi_mid_name", how="left", validate="many_to_one")

    missing = merged.loc[
        merged[variant_columns].isna().any(axis=1), "cpi_mid_name"
    ].unique()
    if len(missing):
        raise ValueError(f"Missing IC variants for categories: {sorted(missing)}")

    for column in variant_columns:
        merged[f"shift_share_{column}"] = (
            merged[column] * (merged["p_import"] - 100.0)
        )
    return merged


def panel_for_variant(panel: pd.DataFrame, variant: str) -> pd.DataFrame:
    """Return a copy using one IC variant under the existing regression API."""
    out = panel.copy()
    out["ic"] = out[variant]
    out["shift_share"] = out[f"shift_share_{variant}"]
    return out


def yearly_correlations(
    panel: pd.DataFrame,
    variants: list[str] | tuple[str, ...] = VARIANT_COLUMNS,
) -> pd.DataFrame:
    """Compute year-specific Pearson correlations for every IC variant."""
    rows: list[dict] = []
    for variant in variants:
        for year, sub in panel.groupby("year"):
            valid = sub[[variant, "delta_cpi"]].dropna()
            rows.append(
                {
                    "ic_variant": variant,
                    "year": int(year),
                    "correlation": (
                        float(valid[variant].corr(valid["delta_cpi"]))
                        if len(valid) >= 2
                        else float("nan")
                    ),
                    "n_categories": len(valid),
                }
            )
    return pd.DataFrame(rows)


def regression_sensitivity(panel: pd.DataFrame) -> pd.DataFrame:
    """Re-estimate the main association and first-difference specification."""
    from src.analysis.cost_push_panel import (
        run_cross_section_fd,
        run_panel_regression,
    )

    rows: list[dict] = []
    for variant in VARIANT_COLUMNS:
        data = panel_for_variant(panel, variant)
        specifications = [
            (
                "all_categories",
                run_panel_regression(data, se_type="cluster", years=SHOCK_YEARS),
            ),
            (
                "competitive_imports_excluded",
                run_panel_regression(
                    data,
                    se_type="cluster",
                    exclude_competitive_imports=True,
                    years=SHOCK_YEARS,
                ),
            ),
            (
                "first_difference_2021_2022",
                run_cross_section_fd(data, year_from=2021, year_to=2022),
            ),
        ]
        for specification, result in specifications:
            rows.append(
                {
                    "ic_variant": variant,
                    "specification": specification,
                    **{
                        key: result[key]
                        for key in (
                            "beta",
                            "se",
                            "tstat",
                            "pval",
                            "n_obs",
                            "n_categories",
                            "r2_within",
                        )
                    },
                }
            )
    return pd.DataFrame(rows)


def goods_services_sensitivity(panel: pd.DataFrame) -> pd.DataFrame:
    """Repeat existing S0-S3 goods/services diagnostics for each IC variant."""
    from src.analysis.cost_push_panel import run_panel_regression
    from src.analysis.goods_services_contrast import (
        GOODS_SERVICES_MAP,
        _bucket_frames,
    )

    base = panel[~panel["is_competitive_import"]].copy()
    base["bucket"] = base["cpi_mid_name"].map(GOODS_SERVICES_MAP)
    if base["bucket"].isna().any():
        missing = sorted(base.loc[base["bucket"].isna(), "cpi_mid_name"].unique())
        raise ValueError(f"Missing goods/services buckets: {missing}")

    rows: list[dict] = []
    for variant in VARIANT_COLUMNS:
        data = panel_for_variant(base, variant)
        for specification, buckets in _bucket_frames(data).items():
            for bucket, bucket_data in buckets.items():
                for year, sub in bucket_data.groupby("year"):
                    valid = sub[["ic", "delta_cpi"]].dropna()
                    rows.append(
                        {
                            "ic_variant": variant,
                            "spec": specification,
                            "bucket": bucket,
                            "metric": "correlation",
                            "year_or_window": str(int(year)),
                            "value": (
                                float(valid["ic"].corr(valid["delta_cpi"]))
                                if len(valid) >= 8
                                else float("nan")
                            ),
                            "n": len(valid),
                        }
                    )
                for window, years in (
                    ("shock", SHOCK_YEARS),
                    ("placebo", PLACEBO_YEARS),
                ):
                    result = run_panel_regression(
                        bucket_data, se_type="cluster", years=years
                    )
                    for metric, key in (("beta", "beta"), ("beta_p", "pval")):
                        rows.append(
                            {
                                "ic_variant": variant,
                                "spec": specification,
                                "bucket": bucket,
                                "metric": metric,
                                "year_or_window": window,
                                "value": result[key],
                                "n": result["n_categories"],
                            }
                        )
    return pd.DataFrame(rows)


def build_report(
    regressions: pd.DataFrame,
    correlations: pd.DataFrame,
    goods_services: pd.DataFrame,
) -> str:
    """Build a compact report from generated result tables."""
    main = regressions[
        regressions["specification"] == "competitive_imports_excluded"
    ]
    lines = [
        "# Cost-push results under four IC variants",
        "",
        "## Main panel association (2021–2024; competitive imports excluded)",
        "",
        "| IC variant | beta | SE | p | within R2 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in main.itertuples(index=False):
        lines.append(
            f"| {row.ic_variant} | {row.beta:.4f} | {row.se:.4f} | "
            f"{row.pval:.4f} | {row.r2_within:.3f} |"
        )

    shock_corr = correlations[correlations["year"].between(2021, 2024)]
    lines.extend(["", "## Yearly IC–CPI correlations, 2021–2024", ""])
    for variant, sub in shock_corr.groupby("ic_variant"):
        values = ", ".join(
            f"{int(row.year)} {row.correlation:+.3f}"
            for row in sub.sort_values("year").itertuples(index=False)
        )
        lines.append(f"- {variant}: {values}")

    within = goods_services[
        (goods_services["spec"] == "S1")
        & (goods_services["metric"] == "correlation")
        & goods_services["year_or_window"].isin(["2021", "2022", "2023", "2024"])
    ]
    lines.extend(["", "## Within-goods / within-services correlations", ""])
    for (variant, bucket), sub in within.groupby(["ic_variant", "bucket"]):
        values = ", ".join(
            f"{row.year_or_window} {row.value:+.3f}"
            for row in sub.sort_values("year_or_window").itertuples(index=False)
        )
        lines.append(f"- {variant} / {bucket}: {values}")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- definition2 is the canonical mathematical IC because it separately "
            "counts direct imports and import requirements induced by domestic production.",
            "- producer-price definition2 is the matching exposure for production-network "
            "propagation; purchaser-price definition2 is the household-facing descriptive exposure.",
            "- all regression coefficients remain associational diagnostics. A favorable p-value "
            "under one IC variant does not repair the single-shock or goods/services confounding.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    from src.analysis.cost_push_panel import build_panel_dataset

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    panel = build_panel_dataset()
    variants = build_ic_variant_table()
    enriched = attach_ic_variants(panel, variants)

    regressions = regression_sensitivity(enriched)
    correlations = yearly_correlations(
        enriched[~enriched["is_competitive_import"]], VARIANT_COLUMNS
    )
    goods_services = goods_services_sensitivity(enriched)

    regressions.to_csv(OUT_DIR / "cost_push_ic_definition_sensitivity.csv", index=False)
    correlations.to_csv(
        OUT_DIR / "yearly_correlation_ic_definition_sensitivity.csv", index=False
    )
    goods_services.to_csv(
        OUT_DIR / "goods_services_ic_definition_sensitivity.csv", index=False
    )
    report = build_report(regressions, correlations, goods_services)
    (OUT_DIR / "ic_definition_downstream_sensitivity.md").write_text(
        report, encoding="utf-8"
    )
    print(report)


if __name__ == "__main__":
    main()
