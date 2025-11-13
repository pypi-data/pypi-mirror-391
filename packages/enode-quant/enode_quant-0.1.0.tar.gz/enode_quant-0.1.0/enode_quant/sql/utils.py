"""
Utility helpers for building safe, consistent SQL strings
for the Enode Quant SDK.

All SQL construction is centralized here so that the query
builders (stock_queries, option_queries, etc.) stay simple,
predictable, and robust.

This module does NOT perform user input validation — that
happens in enode_quant/utils/validation.py. Instead, it
assumes parameters have already been validated and only
focuses on clean SQL assembly.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from enode_quant.errors import InvalidQueryError


# ---------------------------------------------------------------------------
# SQL literal conversion
# ---------------------------------------------------------------------------

def sql_literal(value: Any) -> str:
    """
    Convert a Python value into a SQL-safe literal.

    This is not a SQL injection prevention mechanism; users never pass raw SQL
    strings. Instead, this ensures consistent formatting of values in SQL
    builders.

    Examples:
        sql_literal("AAPL") -> "'AAPL'"
        sql_literal(42)     -> "42"
        sql_literal(True)   -> "TRUE"
        sql_literal(None)   -> "NULL"
    """

    # Explicit boolean handling (bool is a subclass of int!)
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"

    # None → NULL
    if value is None:
        return "NULL"

    # Numeric types
    if isinstance(value, (int, float)):
        return str(value)

    # Strings — SQL escape single quotes
    if isinstance(value, str):
        escaped = value.replace("'", "''")
        return f"'{escaped}'"

    # Fallback: convert arbitrary types to quoted strings
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


# ---------------------------------------------------------------------------
# WHERE clause tools
# ---------------------------------------------------------------------------

def combine_where(clauses: List[str]) -> str:
    """
    Combine a list of SQL conditions into a single WHERE clause.

    Example:
        ["stock_id = 5", "timestamp >= '2024-01-01'"]
        -> "WHERE stock_id = 5 AND timestamp >= '2024-01-01'"
    """
    if not clauses:
        return ""

    return "WHERE " + " AND ".join(clauses)


# ---------------------------------------------------------------------------
# Date filtering
# ---------------------------------------------------------------------------

def apply_date_filters(
    start_date: Optional[str],
    end_date: Optional[str],
    column: str = "timestamp",
) -> List[str]:
    """
    Create SQL date range filters based on start_date and end_date.

    Both parameters must already be validated as ISO date strings.
    """
    filters: List[str] = []

    if start_date:
        filters.append(f"{column} >= {sql_literal(start_date)}")

    if end_date:
        filters.append(f"{column} <= {sql_literal(end_date)}")

    return filters


# ---------------------------------------------------------------------------
# LIMIT clause
# ---------------------------------------------------------------------------

def apply_limit(limit: Optional[int]) -> str:
    """
    Build a LIMIT clause.

    Behavior:
        - limit=None    -> ""
        - limit <= 0    -> InvalidQueryError
        - limit > 0     -> "LIMIT N"
    """
    if limit is None:
        return ""

    try:
        limit_int = int(limit)
    except (TypeError, ValueError):
        raise InvalidQueryError(f"limit must be an integer, got {limit!r}")

    if limit_int <= 0:
        raise InvalidQueryError("limit must be > 0")

    return f"LIMIT {limit_int}"


# ---------------------------------------------------------------------------
# ORDER BY clause
# ---------------------------------------------------------------------------

def order_by(column: str = "timestamp", desc: bool = True) -> str:
    """
    Build an ORDER BY clause.

    Parameters
    ----------
    column : str
        Column to order by. Defaults to 'timestamp'.
    desc : bool
        True for descending (default), False for ascending.

    Returns
    -------
    str
        e.g. "ORDER BY timestamp DESC"
    """
    direction = "DESC" if desc else "ASC"
    return f"ORDER BY {column} {direction}"
