"""
Fetch household survey data from e-Stat.
- Family Income and Expenditure Survey (家計調査): income quintile x expenditure category
- National Survey of Family Income, Consumption and Wealth (全国家計構造調査 2019)
"""

from pathlib import Path

import httpx

RAW_DIR_SURVEY = Path(__file__).resolve().parents[2] / "data" / "raw" / "household-survey"
RAW_DIR_STRUCTURE = Path(__file__).resolve().parents[2] / "data" / "raw" / "household-structure"


def fetch_household_survey_quintile():
    """
    Download household survey data by income quintile from e-Stat.

    Target: 家計調査 > 家計収支編 > 二人以上の世帯のうち勤労者世帯
    > 年間収入五分位階級別 > 1世帯当たり年平均1か月間の収入と支出

    The data needs to be downloaded from e-Stat DB or file download.
    e-Stat dataset IDs need to be confirmed for the specific tables.
    """
    RAW_DIR_SURVEY.mkdir(parents=True, exist_ok=True)

    print("Household Survey (家計調査) - Income Quintile data")
    print("=" * 60)
    print()
    print("Manual download required from e-Stat:")
    print("  https://www.e-stat.go.jp/stat-search/files?toukei=00200561")
    print()
    print("Target tables:")
    print("  - 家計収支編 > 二人以上の世帯のうち勤労者世帯")
    print("  - 年間収入五分位階級別")
    print("  - 1世帯当たり年平均1か月間の収入と支出")
    print("  - Years: 2015-2024")
    print()
    print(f"Save files to: {RAW_DIR_SURVEY}/")


def fetch_household_structure_survey():
    """
    Download National Survey of Family Income, Consumption and Wealth (2019).

    Target: 全国家計構造調査 2019年
    > 所得十分位(五分位)階級別 > 1世帯当たりの消費支出

    This provides a more detailed breakdown by income decile/quintile,
    covering all household types (not just worker households).
    """
    RAW_DIR_STRUCTURE.mkdir(parents=True, exist_ok=True)

    print("National Survey of Family Income (全国家計構造調査 2019)")
    print("=" * 60)
    print()
    print("Manual download required from e-Stat:")
    print("  https://www.e-stat.go.jp/stat-search/files?toukei=00200564")
    print()
    print("Target tables:")
    print("  - 所得十分位(五分位)階級別")
    print("  - 1世帯当たりの消費支出（費目別）")
    print()
    print(f"Save files to: {RAW_DIR_STRUCTURE}/")


if __name__ == "__main__":
    fetch_household_survey_quintile()
    print()
    fetch_household_structure_survey()
