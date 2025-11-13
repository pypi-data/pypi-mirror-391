"""
Helpers to convert API row dictionaries into pandas DataFrames.

Design goals:
- Always succeed (return an empty DataFrame if rows == []).
- Normalize data types (timestamps, numerics).
- Provide a single location where all DataFrame normalization happens.
"""

from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


def to_dataframe(rows: List[Dict[str, Any]]) -> "pd.DataFrame":
    """
    Convert a list of dictionaries (rows) into a pandas DataFrame.

    Behaviors:
    - If rows is empty -> return empty DataFrame.
    - Inconsistent keys -> pandas automatically aligns them.
    - Auto-convert:
        * timestamp/date-like columns -> pandas datetime
        * numeric-like strings -> numeric dtype where appropriate

    Parameters
    ----------
    rows : List[Dict[str, Any]]
        Raw results from run_query(sql).

    Returns
    -------
    pd.DataFrame
    """

    # ------------------------------
    # Empty case
    # ------------------------------
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # ---------------------------------------------------------
    # Identify date-like columns
    #
    # Matches:
    #   - exact: timestamp, time, date, datetime
    #   - suffix-based: *_timestamp, *_date
    # This catches expiration_date, first_seen, etc.
    # ---------------------------------------------------------
    date_like_cols = []
    for col in df.columns:
        lower = col.lower()
        if (
            lower in ("timestamp", "time", "date", "datetime")
            or lower.endswith("_timestamp")
            or lower.endswith("_date")
        ):
            date_like_cols.append(col)

    # Convert date-like columns to datetime
    for col in date_like_cols:
        try:
            df[col] = pd.to_datetime(df[col])
        except Exception:
            # Leave column unchanged if conversion fails
            pass

    # ---------------------------------------------------------
    # Auto-convert numeric-like columns
    #
    # Only attempt conversion for object dtype (strings, mixed types)
    # ---------------------------------------------------------
    for col in df.columns:
        if df[col].dtype == "object":
            # Attempt safe numeric conversion
            try:
                df[col] = pd.to_numeric(df[col], errors="ignore")
            except Exception:
                # Leave unchanged if conversion fails
                pass

    return df
