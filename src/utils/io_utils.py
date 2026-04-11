"""
Utilities for parsing and manipulating Japan's Input-Output Table (2020).
"""

import numpy as np
import pandas as pd
from pathlib import Path

DATA_RAW = Path(__file__).resolve().parents[2] / "data" / "raw"
DATA_PROCESSED = Path(__file__).resolve().parents[2] / "data" / "processed"


def load_io_table(price_type: str = "producer") -> dict:
    """
    Load and parse the 2020 IO table (integrated medium classification, 108 sectors).

    Parameters
    ----------
    price_type : str
        "producer" or "purchaser"

    Returns
    -------
    dict with keys:
        - "transaction": pd.DataFrame — intermediate transaction matrix (108 x 108)
        - "final_demand": pd.DataFrame — final demand columns
        - "value_added": pd.DataFrame — value added rows
        - "output": pd.Series — domestic output by sector
        - "imports": pd.Series — imports by sector (from final demand columns)
        - "sector_codes": list — sector code list
        - "sector_names": list — sector name list
    """
    filename = {
        "producer": "io2020_producer_price_108.xlsx",
        "purchaser": "io2020_purchaser_price_108.xlsx",
    }[price_type]

    filepath = DATA_RAW / "io-table" / filename
    df = pd.read_excel(filepath, sheet_name="Sheet1", header=None)

    # Extract sector codes and names from row headers (column 0, 1)
    # Rows 3 onwards are data rows; find where sectors end
    sector_codes = []
    sector_names = []
    data_start_row = 3

    for i in range(data_start_row, len(df)):
        code = str(df.iloc[i, 0]).strip()
        name = str(df.iloc[i, 1]).strip()
        # Sector codes are 3-digit numbers below 700 (700+ are summary rows)
        if code.isdigit() and len(code) == 3 and int(code) < 700:
            sector_codes.append(code)
            sector_names.append(name)
        else:
            break

    n_sectors = len(sector_codes)
    sector_set = set(sector_codes)

    # Column headers: row 1 has codes, row 2 has names
    # Data columns start at column 2
    col_codes = [str(df.iloc[1, j]).strip() for j in range(2, df.shape[1])]
    col_names = [str(df.iloc[2, j]).strip() for j in range(2, df.shape[1])]

    # Find the range of intermediate demand columns
    # Intermediate columns end at "700" (内生部門計) or the first non-sector code
    n_intermediate = 0
    for code in col_codes:
        if code in sector_set:
            n_intermediate += 1
        elif code == "700":  # 内生部門計 marks end of intermediate sector columns
            break
        else:
            break

    # Extract data as numpy arrays to avoid iloc issues with pandas 3.0
    raw = df.values

    # Intermediate transaction matrix
    transaction_data = raw[
        data_start_row : data_start_row + n_sectors,
        2 : 2 + n_intermediate,
    ].astype(float)

    transaction = pd.DataFrame(
        transaction_data,
        index=sector_codes,
        columns=sector_codes[:n_intermediate],
    )

    # Final demand columns
    fd_start_col = 2 + n_intermediate
    fd_col_codes = col_codes[n_intermediate:]
    fd_col_names = col_names[n_intermediate:]

    final_demand_data = raw[
        data_start_row : data_start_row + n_sectors,
        fd_start_col :,
    ].astype(float)

    final_demand = pd.DataFrame(
        final_demand_data,
        index=sector_codes,
        columns=fd_col_codes,
    )
    final_demand.columns.name = "final_demand_code"

    # Domestic output (row with code "970" = 国内生産額)
    output_row_idx = None
    for i in range(data_start_row + n_sectors, len(df)):
        code = str(raw[i, 0]).strip()
        if code == "970":
            output_row_idx = i
            break

    output = pd.Series(
        raw[output_row_idx, 2 : 2 + n_sectors].astype(float),
        index=sector_codes,
        name="domestic_output",
    )

    # Imports (column with code "870" = 輸入計)
    imports = None
    for fd_idx, code in enumerate(fd_col_codes):
        if code == "870":
            imports = pd.Series(
                final_demand_data[:, fd_idx].astype(float),
                index=sector_codes,
                name="imports",
            )
            break

    # Value added rows
    va_start = data_start_row + n_sectors
    va_data = {}
    for i in range(va_start, len(df)):
        code = str(raw[i, 0]).strip()
        name = str(raw[i, 1]).strip()
        if code.isdigit():
            va_data[code] = pd.Series(
                raw[i, 2 : 2 + n_sectors].astype(float),
                index=sector_codes,
                name=name,
            )

    value_added = pd.DataFrame(va_data).T
    value_added.columns = sector_codes

    return {
        "transaction": transaction,
        "final_demand": final_demand,
        "value_added": value_added,
        "output": output,
        "imports": imports,
        "sector_codes": sector_codes,
        "sector_names": sector_names,
    }


def compute_input_coefficients(io_data: dict) -> pd.DataFrame:
    """
    Compute input coefficient matrix A = Z * diag(x)^{-1}.

    Parameters
    ----------
    io_data : dict from load_io_table()

    Returns
    -------
    pd.DataFrame — input coefficient matrix A (108 x 108)
    """
    Z = io_data["transaction"]
    x = io_data["output"]

    # Avoid division by zero for sectors with zero output
    x_inv = x.copy()
    x_inv[x_inv == 0] = np.inf
    x_inv = 1.0 / x_inv

    A = Z.multiply(x_inv, axis=1)
    return A


def compute_leontief_inverse(A: pd.DataFrame) -> pd.DataFrame:
    """
    Compute Leontief inverse L = (I - A)^{-1}.

    Parameters
    ----------
    A : pd.DataFrame — input coefficient matrix

    Returns
    -------
    pd.DataFrame — Leontief inverse matrix
    """
    n = A.shape[0]
    I = np.eye(n)
    L = np.linalg.inv(I - A.values)
    return pd.DataFrame(L, index=A.index, columns=A.columns)


def compute_import_content(io_data: dict) -> pd.Series:
    """
    Compute import content ratio by sector.

    Method: Use the import ratio (imports / total supply) as a proxy for
    import dependence per unit of domestic demand. Then apply Leontief inverse
    to capture indirect import dependence through supply chains.

    Import content of sector j = sum_i (m_i * L_ij)
    where m_i = |imports_i| / (output_i + |imports_i|) is the import penetration ratio
    and L is the Leontief inverse.

    Returns
    -------
    pd.Series — import content ratio for each sector (0 to 1)
    """
    A = compute_input_coefficients(io_data)
    L = compute_leontief_inverse(A)
    x = io_data["output"]
    imports = io_data["imports"]

    if imports is None:
        raise ValueError("Import data not found in IO table")

    # Import penetration ratio: |imports| / (output + |imports|)
    # This gives the share of imports in total supply for each sector
    abs_imports = imports.abs()
    total_supply = x + abs_imports
    import_ratio = abs_imports / total_supply.replace(0, np.inf)

    # Total import content per unit of final demand:
    # For each sector j, sum over all sectors i of (import_ratio_i * L_ij)
    import_content = import_ratio.values @ L.values

    return pd.Series(import_content, index=io_data["sector_codes"], name="import_content")
