"""Producer- versus purchaser-price sensitivity for sector and CPI-category IC."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analysis.bridge_matrix_mid import (
    CPI_MID_CATEGORY_MAP,
    build_bridge_matrix_mid_from_io,
)
from src.utils.io_utils import (
    compute_import_content,
    compute_induced_import_content,
    load_io_table,
)


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "processed" / "import-content"


def compute_category_sensitivity() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return long category results and a sector-level valuation comparison."""
    category_rows: list[dict] = []
    sector_parts: list[pd.DataFrame] = []

    for valuation in ("producer", "purchaser"):
        io = load_io_table(valuation)
        bridge = build_bridge_matrix_mid_from_io(io)
        sector_definitions = {
            "definition1_muT_Ld": compute_import_content(io),
            "definition2_induced": compute_induced_import_content(io),
        }

        sector_part = pd.DataFrame(
            {
                f"definition1_{valuation}": sector_definitions["definition1_muT_Ld"],
                f"definition2_{valuation}": sector_definitions["definition2_induced"],
            }
        )
        sector_parts.append(sector_part)

        private_consumption = io["final_demand"]["721"].clip(lower=0.0)
        for category_name, meta in CPI_MID_CATEGORY_MAP.items():
            weights = bridge.loc[category_name]
            pc_value = sum(
                max(0.0, private_consumption.get(sector, 0.0))
                for sector in meta["io_sectors"]
            )
            for definition, sector_ic in sector_definitions.items():
                category_rows.append(
                    {
                        "cpi_mid_name": category_name,
                        "cpi_code": meta["cpi_code"],
                        "group": meta["group"],
                        "valuation": valuation,
                        "definition": definition,
                        "import_content": float((weights * sector_ic).sum()),
                        "pc_value_bn_jpy": float(pc_value),
                    }
                )

    category = pd.DataFrame(category_rows)
    sector = pd.concat(sector_parts, axis=1)
    sector["definition1_purchaser_minus_producer"] = (
        sector["definition1_purchaser"] - sector["definition1_producer"]
    )
    sector["definition2_purchaser_minus_producer"] = (
        sector["definition2_purchaser"] - sector["definition2_producer"]
    )
    sector.index.name = "sector_code"
    return category, sector.reset_index()


def summarize_major_groups(category: pd.DataFrame) -> pd.DataFrame:
    """Aggregate CPI middle categories with the selected valuation's IO consumption values."""
    rows: list[dict] = []
    for (group, valuation, definition), sub in category.groupby(
        ["group", "valuation", "definition"]
    ):
        weights = sub["pc_value_bn_jpy"]
        weight_sum = weights.sum()
        rows.append(
            {
                "group": group,
                "valuation": valuation,
                "definition": definition,
                "n_mid_categories": len(sub),
                "pc_value_bn_jpy": weight_sum,
                "import_content": (
                    float((sub["import_content"] * weights).sum() / weight_sum)
                    if weight_sum > 0
                    else float("nan")
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(["definition", "group", "valuation"])


def build_markdown_report(
    category: pd.DataFrame,
    sector: pd.DataFrame,
    summary: pd.DataFrame,
) -> str:
    """Build a compact, source-linked sensitivity report."""
    lines = [
        "# IC valuation sensitivity — producer vs purchaser prices",
        "",
        "2020年108部門IO表について、同一の競争輸入仮定・同一のCPI対応表を用い、",
        "生産者価格表と購入者価格表の差を測った。購入者価格版では、IO民間消費列721による",
        "ブリッジウェイトも購入者価格表から再構築している。",
        "",
    ]

    for definition in ("definition1", "definition2"):
        producer = sector[f"{definition}_producer"]
        purchaser = sector[f"{definition}_purchaser"]
        diff = purchaser - producer
        lines.extend(
            [
                f"## {definition}",
                "",
                f"- sector correlation: {producer.corr(purchaser):.4f}",
                f"- mean absolute difference: {diff.abs().mean():.4f}",
                f"- maximum absolute difference: {diff.abs().max():.4f}",
                "",
            ]
        )

    pivot = summary.pivot_table(
        index=["group", "definition"],
        columns="valuation",
        values="import_content",
    ).reset_index()
    pivot["difference"] = pivot["purchaser"] - pivot["producer"]
    table_lines = [
        "| group | definition | producer | purchaser | difference |",
        "|---|---|---:|---:|---:|",
    ]
    for row in pivot.itertuples(index=False):
        table_lines.append(
            f"| {row.group} | {row.definition} | {row.producer:.4f} | "
            f"{row.purchaser:.4f} | {row.difference:+.4f} |"
        )
    lines.extend(
        [
            "## CPI group summary",
            "",
            *table_lines,
            "",
            "## Interpretation guardrails",
            "",
            "- これは価格評価基準への感度であり、因果的な価格転嫁率ではない。",
            "- definition2 は全108部門の直接輸入と輸入中間投入の誘発分を含む。",
            "- CPI中分類から大費目への集計はIO民間消費額加重であり、家計調査ウェイトとは異なる。",
            "- 購入者価格差が小さくても、競争輸入比例配分・部門対応・固定技術の仮定は残る。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    category, sector = compute_category_sensitivity()
    summary = summarize_major_groups(category)

    category.to_csv(OUT_DIR / "ic_valuation_sensitivity.csv", index=False)
    sector.to_csv(OUT_DIR / "sector_ic_valuation_sensitivity.csv", index=False)
    summary.to_csv(OUT_DIR / "ic_valuation_summary.csv", index=False)
    report = build_markdown_report(category, sector, summary)
    (OUT_DIR / "ic_valuation_sensitivity.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
