"""
Public API functions for working with stocks, stock quotes, and candles.

Intended usage (researcher side):

    from enode_quant.api.stocks import (
        get_stocks,
        get_stock_quotes,
        get_stock_candles,
    )

Design:
- Parameters are validated and normalized in this layer.
- SQL strings are built by enode_quant.sql.stock_queries.
- HTTP + JSON handling is done by enode_quant.client.run_query.
- Results are converted to pandas.DataFrame by enode_quant.utils.df_helpers
  (unless as_dataframe=False is requested).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from enode_quant.client import run_query
from enode_quant.sql.stock_queries import (
    build_get_stocks_query,
    build_stock_quotes_query,
    build_stock_candles_query,
)
from enode_quant.utils.df_helpers import to_dataframe
from enode_quant.utils.validation import (
    validate_symbol,
    validate_limit,
    validate_date,
    validate_date_range,
)

from enode_quant.errors import InvalidQueryError


DataRows = List[Dict[str, Any]]

__all__ = [
    "get_stocks",
    "get_stock_quotes",
    "get_stock_candles",
]


# ---------------------------------------------------------------------------
# STOCK MASTER LIST
# ---------------------------------------------------------------------------

def get_stocks(
    symbol: Optional[str] = None,
    limit: Optional[int] = None,
    as_dataframe: bool = True,
) -> Union["DataFrame", DataRows]:
    """
    Fetch rows from the stock master table (market.stocks).

    Default behavior:
        get_stocks()
        -> all stocks, ordered alphabetically by symbol.

    Common usage:
        get_stocks(symbol="AAPL")
        -> the AAPL row only.

    Parameters
    ----------
    symbol : str, optional
        Symbol to filter by. If provided, it will be normalized
        to uppercase (e.g. "aapl" -> "AAPL").
    limit : int, optional
        Maximum number of rows to return. If None, no LIMIT is applied.
        If not None, must be > 0.
    as_dataframe : bool, optional
        If True (default), return a pandas.DataFrame.
        If False, return the raw list of row dictionaries.

    Returns
    -------
    pandas.DataFrame or List[Dict[str, Any]]

    Raises
    ------
    InvalidQueryError
        If parameters are invalid.
    MissingCredentialsError, AuthenticationError, APIConnectionError, ServerError
        Propagated from the HTTP client if the API call fails.
    """
    # 1) Validate parameters
    if symbol is not None:
        symbol = validate_symbol(symbol)

    validate_limit(limit)

    # 2) Build SQL using the stock_queries builder
    sql = build_get_stocks_query(
        symbol=symbol,
        limit=limit,
    )

    # 3) Execute query and convert
    rows: DataRows = run_query(sql)

    if as_dataframe:
        return to_dataframe(rows)

    return rows


# ---------------------------------------------------------------------------
# STOCK QUOTES (L1)
# ---------------------------------------------------------------------------

def get_stock_quotes(
    symbol: Optional[str] = None,
    stock_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    quote_type: Optional[str] = None,
    limit: int = 100,
    as_dataframe: bool = True,
) -> Union["DataFrame", DataRows]:
    """
    Fetch L1 stock quotes (market.stock_quotes), joined with market.stocks
    so that `symbol` is always available in the result.

    Default behavior:
        get_stock_quotes(symbol="AAPL")
        -> last 100 AAPL quotes, ordered by timestamp DESC.

    Parameters
    ----------
    symbol : str, optional
        Underlying symbol to filter by (preferred). Normalized to uppercase.
    stock_id : int, optional
        Underlying stock_id (internal/advanced usage). Can be used alongside
        symbol; both filters will be applied if provided.
    start_date : str, optional
        Inclusive lower bound on quote timestamp (q.timestamp), as a
        'YYYY-MM-DD' date string. For now, we accept date-only strings
        which the database will cast appropriately.
    end_date : str, optional
        Inclusive upper bound on quote timestamp (q.timestamp), as
        'YYYY-MM-DD'.
    quote_type : str, optional
        Optional quote type filter, e.g. 'bid', 'ask', 'mid', 'last'.
        No strict validation yet; if it doesn't match a stored value,
        the query will simply return zero rows.
    limit : int, optional
        Maximum number of rows to return. Must be > 0. Default is 100.
    as_dataframe : bool, optional
        If True (default), return a pandas.DataFrame.
        If False, return raw list-of-dicts rows.

    Returns
    -------
    pandas.DataFrame or List[Dict[str, Any]]

    Raises
    ------
    InvalidQueryError
        If parameters (limit, dates, etc.) are invalid.
    MissingCredentialsError, AuthenticationError, APIConnectionError, ServerError
        Propagated from lower layers if the API call fails.
    """
    # 1) Validate parameters
    if symbol is not None:
        symbol = validate_symbol(symbol)

    validate_limit(limit)

    # Date range validation (lexicographic is safe with YYYY-MM-DD format)
    validate_date_range(start_date, end_date)

    if start_date is not None:
        start_date = validate_date(start_date)
    if end_date is not None:
        end_date = validate_date(end_date)

    # 2) Build SQL using the stock_queries builder
    sql = build_stock_quotes_query(
        symbol=symbol,
        stock_id=stock_id,
        start_timestamp=start_date,
        end_timestamp=end_date,
        quote_type=quote_type,
        limit=limit,
    )

    # 3) Execute query and convert
    rows: DataRows = run_query(sql)

    if as_dataframe:
        return to_dataframe(rows)

    return rows


# ---------------------------------------------------------------------------
# STOCK CANDLES (OHLCV)
# ---------------------------------------------------------------------------

def get_stock_candles(
    symbol: Optional[str] = None,
    stock_id: Optional[int] = None,
    resolution: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 500,
    as_dataframe: bool = True,
) -> Union["DataFrame", DataRows]:
    """
    Fetch OHLCV candles (market.stock_candles), joined with market.stocks.

    Default behavior:
        get_stock_candles(symbol="AAPL")
        -> last 500 candles for AAPL, ordered by timestamp DESC.

    Parameters
    ----------
    symbol : str, optional
        Underlying symbol to filter by. Normalized to uppercase.
    stock_id : int, optional
        Underlying stock_id (internal/advanced).
    resolution : str, optional
        Candle resolution filter (e.g. '1H', '1D'). No strict validation
        yet; invalid resolutions will typically result in zero rows.
    start_date : str, optional
        Inclusive lower bound on c.timestamp, as 'YYYY-MM-DD'.
    end_date : str, optional
        Inclusive upper bound on c.timestamp, as 'YYYY-MM-DD'.
    limit : int, optional
        Maximum number of rows to return. Must be > 0. Default is 500.
    as_dataframe : bool, optional
        If True (default), return a pandas.DataFrame.
        If False, return raw list-of-dicts rows.

    Returns
    -------
    pandas.DataFrame or List[Dict[str, Any]]

    Raises
    ------
    InvalidQueryError
        If parameters are invalid.
    MissingCredentialsError, AuthenticationError, APIConnectionError, ServerError
        Propagated from lower layers if the API call fails.
    """
    # 1) Validate parameters
    if symbol is not None:
        symbol = validate_symbol(symbol)

    validate_limit(limit)

    validate_date_range(start_date, end_date)

    if start_date is not None:
        start_date = validate_date(start_date)
    if end_date is not None:
        end_date = validate_date(end_date)

    # 2) Build SQL using the stock_queries builder
    sql = build_stock_candles_query(
        symbol=symbol,
        stock_id=stock_id,
        resolution=resolution,
        start_timestamp=start_date,
        end_timestamp=end_date,
        limit=limit,
    )

    # 3) Execute query and convert
    rows: DataRows = run_query(sql)

    if as_dataframe:
        return to_dataframe(rows)

    return rows
