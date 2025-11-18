"""
Validation utilities for Enode Quant SDK.

All bad inputs from users should be caught here before they reach
the SQL builders. This ensures:
    - The SQL layer receives only valid, normalized values.
    - Errors are consistent (InvalidQueryError).
    - API functions remain clean and readable.
    - Researchers never accidentally issue meaningless queries.

Every function returns a normalized value (e.g., uppercase symbol)
or raises InvalidQueryError.
"""


from __future__ import annotations

import math
from typing import Optional

from enode_quant.errors import InvalidQueryError



# ---------------------------------------------------------------------------
# SYMBOL VALIDATION
# ---------------------------------------------------------------------------

def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize an equity symbol.

    Rules:
    - Must be non-empty string
    - Must contain alphanumerics (AAPL, MSFT, SPY, etc.)
    - Normalize to uppercase (standard in finance)

    Returns
    -------
    str
        Normalized uppercase symbol.
    """
    if not isinstance(symbol, str):
        raise InvalidQueryError(f"symbol must be a string, got {type(symbol)}")

    symbol = symbol.strip().upper()

    if not symbol:
        raise InvalidQueryError("symbol cannot be empty")

    if not symbol.replace(".", "").isalnum():
        raise InvalidQueryError(
            f"symbol '{symbol}' contains invalid characters"
        )

    return symbol



# ---------------------------------------------------------------------------
# LIMIT VALIDATION
# ---------------------------------------------------------------------------

def validate_limit(limit: Optional[int]) -> None:
    """
    Validate limit parameter.

    Rules:
    - If None -> allowed (means no LIMIT clause)
    - If not None -> must be int > 0
    """
    if limit is None:
        return

    try:
        limit_int = int(limit)
    except (TypeError, ValueError):
        raise InvalidQueryError(f"limit must be an integer, got {limit!r}")

    if limit_int <= 0:
        raise InvalidQueryError("limit must be > 0")



# ---------------------------------------------------------------------------
# DATE VALIDATION
# ---------------------------------------------------------------------------

def validate_date(date_str: str) -> str:
    """
    Validate a date string (YYYY-MM-DD).

    This checks:
    - type is str
    - length is 10
    - splits into exactly 3 components with '-'
    - components are numeric

    It does *not* validate that the date actually exists on the calendar
    (e.g. 2024-13-99); that will be enforced by the database.
    """
    if not isinstance(date_str, str):
        raise InvalidQueryError("date must be a string in 'YYYY-MM-DD' format")

    date_str = date_str.strip()

    if len(date_str) != 10:
        raise InvalidQueryError(
            f"date '{date_str}' must be in 'YYYY-MM-DD' format (10 characters)."
        )

    try:
        parts = date_str.split("-")
        if len(parts) != 3:
            raise ValueError
        year, month, day = parts
    except ValueError:
        raise InvalidQueryError(
            f"date '{date_str}' must be in 'YYYY-MM-DD' format."
        )

    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        raise InvalidQueryError(
            f"date '{date_str}' must be numeric in 'YYYY-MM-DD' format."
        )

    return date_str




def validate_date_range(start: Optional[str], end: Optional[str]) -> None:
    """
    Validate that a date range is properly ordered.

    Rules:
    - Both None -> allowed
    - If one is None -> allowed
    - If both exist: start <= end

    Raises
    ------
    InvalidQueryError
    """
    if start is None or end is None:
        return

    if start > end:
        raise InvalidQueryError(
            f"Invalid date range: start_date '{start}' "
            f"cannot be after end_date '{end}'."
        )



# ---------------------------------------------------------------------------
# STRIKE VALIDATION
# ---------------------------------------------------------------------------

def validate_strike_range(
    min_strike: Optional[float],
    max_strike: Optional[float],
) -> None:
    """
    Ensure strike inputs are valid floats and properly ordered.

    Rules:
    - Either may be None
    - If both exist -> min_strike <= max_strike
    - No NaN or Infinity allowed
    """
    # Check numeric validity
    for val, name in [(min_strike, "min_strike"), (max_strike, "max_strike")]:
        if val is None:
            continue

        if not isinstance(val, (int, float)):
            raise InvalidQueryError(f"{name} must be numeric, got {type(val)}")

        if math.isnan(val) or math.isinf(val):
            raise InvalidQueryError(f"{name} cannot be NaN or Infinity.")

    # Order check
    if min_strike is not None and max_strike is not None:
        if min_strike > max_strike:
            raise InvalidQueryError(
                f"min_strike ({min_strike}) cannot be greater than max_strike ({max_strike})."
            )



# ---------------------------------------------------------------------------
# OPTION TYPE VALIDATION
# ---------------------------------------------------------------------------

def validate_option_type(option_type: str) -> str:
    """
    Validate and normalize option type.

    Acceptable values:
        - "call"
        - "put"
        - any case variants ("CALL", "Put", etc.)

    Returns normalized lowercase string.
    """
    if not isinstance(option_type, str):
        raise InvalidQueryError("option_type must be a string ('call'/'put')")

    option_type = option_type.strip().lower()

    if option_type not in {"call", "put"}:
        raise InvalidQueryError(
            f"Invalid option_type '{option_type}'. Must be 'call' or 'put'."
        )

    return option_type



# ---------------------------------------------------------------------------
# BOOLEAN VALIDATION
# ---------------------------------------------------------------------------

def validate_bool(b: Optional[bool]) -> Optional[bool]:
    """
    Validate a boolean parameter (for in-the-money filter, etc.)

    Only None, True, False allowed.
    """
    if b is None:
        return None

    if not isinstance(b, bool):
        raise InvalidQueryError("parameter must be True, False, or None")

    return b



# ---------------------------------------------------------------------------
# QUOTE TYPE VALIDATION
# ---------------------------------------------------------------------------



def validate_quote_type(qtype: str) -> str:
    """
    Validate quote type (e.g. 'bid', 'ask', 'mid', 'last').

    Normalizes to lowercase.
    """
    if not isinstance(qtype, str):
        raise InvalidQueryError("quote_type must be a string")

    q = qtype.strip().lower()
    allowed = {"bid", "ask", "mid", "last"}

    if q not in allowed:
        raise InvalidQueryError(
            f"Invalid quote_type '{q}'. Must be one of {sorted(allowed)}"
        )

    return q
