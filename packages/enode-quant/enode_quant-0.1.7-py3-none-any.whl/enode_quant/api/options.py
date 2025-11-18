"""
Public API functions for working with options.

These functions are what researchers will actually call, e.g.:

    from enode_quant.api.options import (
        get_option_contracts,
        get_option_quotes,
    )

They:

- Accept high-level, user-friendly parameters (symbol, expiry window, strikes…)
- Delegate validation to enode_quant.utils.validation
- Build SQL via enode_quant.sql.option_queries
- Execute queries via enode_quant.client.run_query
- Convert results into pandas DataFrames via enode_quant.utils.df_helpers

By default, they return pandas.DataFrame objects, but can optionally return
the raw list-of-dicts rows by setting as_dataframe=False.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from enode_quant.client import run_query
from enode_quant.errors import InvalidQueryError
from enode_quant.sql.option_queries import (
    build_option_contracts_query,
    build_option_quotes_query,
)
from enode_quant.utils.df_helpers import to_dataframe
from enode_quant.utils.validation import (
    validate_symbol,
    validate_limit,
    validate_date,
    validate_date_range,
    validate_strike_range,
    validate_option_type,
)


DataRows = List[Dict[str, Any]]


__all__ = [
    "get_option_contracts",
    "get_option_quotes",
]


# ---------------------------------------------------------------------------
# OPTION CONTRACTS
# ---------------------------------------------------------------------------

def get_option_contracts(
    symbol: Optional[str] = None,
    stock_id: Optional[int] = None,
    option_type: Optional[str] = None,
    expiration_date: Optional[str] = None,
    expiration_after: Optional[str] = None,
    expiration_before: Optional[str] = None,
    min_strike: Optional[float] = None,
    max_strike: Optional[float] = None,
    occ_symbol: Optional[str] = None,
    limit: int = 200,
    as_dataframe: bool = True,
) -> Union["DataFrame", DataRows]:
    """
    Fetch option contracts from the database, joined with the underlying
    stocks table so that `symbol` is always available.

    Default behavior:
        get_option_contracts(symbol="AAPL")
        -> up to 200 AAPL option contracts, ordered by
           symbol, expiration_date, strike (ascending).

    Parameters
    ----------
    symbol : str, optional
        Underlying equity symbol (e.g., "AAPL"). Preferred way to scope
        contracts for most users.
    stock_id : int, optional
        Underlying stock_id (internal/advanced usage).
    option_type : str, optional
        "call" or "put".
    expiration_date : str, optional
        Exact expiration date (YYYY-MM-DD). If provided, takes precedence
        over expiration_after / expiration_before.
    expiration_after : str, optional
        Lower bound on expiration_date (>=).
    expiration_before : str, optional
        Upper bound on expiration_date (<=).
    min_strike : float, optional
        Minimum strike (>=).
    max_strike : float, optional
        Maximum strike (<=).
    occ_symbol : str, optional
        OCC-style contract symbol if stored.
    limit : int, optional
        Maximum number of rows to return. Must be > 0. Default is 200.
    as_dataframe : bool, optional
        If True (default), return a pandas.DataFrame. If False, return
        the raw list of row dictionaries.

    Returns
    -------
    pandas.DataFrame or List[Dict[str, Any]]
        Contracts with underlying symbol and basic metadata.

    Raises
    ------
    MissingCredentialsError
        If the user has not run `enode login`.
    InvalidQueryError
        If parameters are invalid (limit <= 0, bad date range, etc.).
    AuthenticationError, APIConnectionError, ServerError
        Propagated from the HTTP client if the API call fails.
    """

    # -------------------------
    # 1) Validate parameters
    # -------------------------
    if symbol is not None:
        symbol = validate_symbol(symbol)

    validate_limit(limit)

    if option_type is not None:
        option_type = validate_option_type(option_type)

    # Expiration dates
    if expiration_date is not None:
        expiration_date = validate_date(expiration_date)
    else:
        # Only validate range if no exact date is provided
        validate_date_range(expiration_after, expiration_before)

        if expiration_after is not None:
            expiration_after = validate_date(expiration_after)

        if expiration_before is not None:
            expiration_before = validate_date(expiration_before)

    # Strike range
    validate_strike_range(min_strike, max_strike)

    # -------------------------
    # 2) Build SQL
    # -------------------------
    sql = build_option_contracts_query(
        symbol=symbol,
        stock_id=stock_id,
        option_type=option_type,
        expiration_date=expiration_date,
        expiration_after=expiration_after,
        expiration_before=expiration_before,
        min_strike=min_strike,
        max_strike=max_strike,
        occ_symbol=occ_symbol,
        limit=limit,
    )

    # -------------------------
    # 3) Execute & normalize
    # -------------------------
    rows: DataRows = run_query(sql)

    if as_dataframe:
        return to_dataframe(rows)

    return rows


# ---------------------------------------------------------------------------
# OPTION QUOTES
# ---------------------------------------------------------------------------

def get_option_quotes(
    symbol: Optional[str] = None,
    stock_id: Optional[int] = None,
    option_id: Optional[int] = None,
    option_type: Optional[str] = None,
    expiration_date: Optional[str] = None,
    expiration_after: Optional[str] = None,
    expiration_before: Optional[str] = None,
    min_strike: Optional[float] = None,
    max_strike: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    in_the_money: Optional[bool] = None,
    limit: int = 500,
    as_dataframe: bool = True,
) -> Union["DataFrame", DataRows]:
    """
    Fetch option quotes (time-series) from the database, joined with both
    option contracts and underlying stocks.

    This lets you ask for things like:

        - All AAPL call quotes expiring before 2025-12-01
        - Quotes for a specific option_id
        - All put quotes in a given strike and expiry window
        - All quotes in a certain time window for an underlying

    Default behavior:
        get_option_quotes(symbol="AAPL")
        -> last `limit` quotes for all AAPL options, all expiries/strikes,
           ordered by timestamp DESC.

    Parameters
    ----------
    symbol : str, optional
        Underlying equity symbol.
    stock_id : int, optional
        Underlying stock_id (advanced/internal).
    option_id : int, optional
        Specific option contract ID. If provided, all other contract filters
        are optional.
    option_type : str, optional
        "call" or "put".
    expiration_date : str, optional
        Exact expiration date (YYYY-MM-DD).
    expiration_after : str, optional
        Lower bound on expiry (>=).
    expiration_before : str, optional
        Upper bound on expiry (<=).
    min_strike, max_strike : float, optional
        Strike range filters.
    start_date, end_date : str, optional
        Time window on the quote timestamp (q.timestamp). If both are None,
        you get the last `limit` quotes by timestamp.
    in_the_money : bool, optional
        Filter by in-the-money flag if stored.
    limit : int, optional
        Maximum number of rows to return. Must be > 0. Default is 500.
    as_dataframe : bool, optional
        If True (default), return a pandas.DataFrame. If False, return
        raw list-of-dicts rows.

    Returns
    -------
    pandas.DataFrame or List[Dict[str, Any]]
        Option quotes with contract & underlying metadata.

    Raises
    ------
    InvalidQueryError
        If no scoping parameter is provided (e.g., calling this with all
        filters None can be too broad), or if any parameter is invalid.
    MissingCredentialsError, AuthenticationError, APIConnectionError, ServerError
        Propagated from lower layers if the API call fails.
    """

    # -------------------------------------------------
    # 1) Basic safety: require *some* scoping condition
    # -------------------------------------------------
    if symbol is None and stock_id is None and option_id is None:
        # You *could* allow this, but it can become a massive query; we nudge
        # users towards specifying at least one filter.
        raise InvalidQueryError(
            "get_option_quotes requires at least one of "
            "symbol, stock_id, or option_id to avoid unbounded queries."
        )

    # -------------------------------------------------
    # 2) Validate parameters
    # -------------------------------------------------
    if symbol is not None:
        symbol = validate_symbol(symbol)

    validate_limit(limit)

    if option_type is not None:
        option_type = validate_option_type(option_type)

    # Expiry validation
    if expiration_date is not None:
        expiration_date = validate_date(expiration_date)
    else:
        validate_date_range(expiration_after, expiration_before)

        if expiration_after is not None:
            expiration_after = validate_date(expiration_after)

        if expiration_before is not None:
            expiration_before = validate_date(expiration_before)

    # Strike range
    validate_strike_range(min_strike, max_strike)

    # Timestamp range
    validate_date_range(start_date, end_date)
    if start_date is not None:
        start_date = validate_date(start_date)
    if end_date is not None:
        end_date = validate_date(end_date)

    # -------------------------------------------------
    # 3) Build SQL
    # -------------------------------------------------
    sql = build_option_quotes_query(
        symbol=symbol,
        stock_id=stock_id,
        option_id=option_id,
        option_type=option_type,
        expiration_date=expiration_date,
        expiration_after=expiration_after,
        expiration_before=expiration_before,
        min_strike=min_strike,
        max_strike=max_strike,
        start_timestamp=start_date,
        end_timestamp=end_date,
        in_the_money=in_the_money,
        limit=limit,
    )

    # -------------------------------------------------
    # 4) Execute & normalize
    # -------------------------------------------------
    rows: DataRows = run_query(sql)

    if as_dataframe:
        return to_dataframe(rows)

    return rows
