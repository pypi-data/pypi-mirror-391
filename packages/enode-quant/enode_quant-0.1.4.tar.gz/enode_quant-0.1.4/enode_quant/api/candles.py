"""
Public API functions for working with OHLCV candles.

This module focuses on time-series price data from market.stock_candles,
joined with market.stocks so that the human-friendly `symbol` is always
available.

Typical usage:

    from enode_quant.api.candles import get_stock_candles

    df = get_stock_candles(
        symbol="AAPL",
        resolution="1H",
        start_date="2025-01-01",
        limit=500,
    )

Design:
- Parameters are validated & normalized here.
- SQL is built by enode_quant.sql.stock_queries.build_stock_candles_query.
- HTTP & JSON handled by enode_quant.client.run_query.
- Results are converted to pandas.DataFrame by enode_quant.utils.df_helpers
  (unless as_dataframe=False is requested).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from enode_quant.client import run_query
from enode_quant.sql.stock_queries import build_stock_candles_query
from enode_quant.utils.df_helpers import to_dataframe
from enode_quant.utils.validation import (
    validate_symbol,
    validate_limit,
    validate_date,
    validate_date_range,
)
from enode_quant.errors import InvalidQueryError


DataRows = List[Dict[str, Any]]

__all__ = ["get_stock_candles"]

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
    Fetch OHLCV candles from market.stock_candles, joined with market.stocks.

    Default behavior:
        get_stock_candles(symbol="AAPL")
        -> last 500 candles for AAPL, ordered by timestamp DESC.

    Parameters
    ----------
    symbol : str, optional
        Underlying equity symbol to filter by. Normalized to uppercase.
    stock_id : int, optional
        Underlying stock_id (advanced usage). If both provided, filters intersect.
    resolution : str, optional
        Candle resolution filter (e.g. "1H", "1D").
    start_date : str, optional
        Inclusive lower bound on c.timestamp ('YYYY-MM-DD').
    end_date : str, optional
        Inclusive upper bound on c.timestamp ('YYYY-MM-DD').
    limit : int, optional
        Maximum number of rows to return. Must be > 0.
    as_dataframe : bool, optional
        If True (default), return pandas.DataFrame; otherwise list-of-dicts.

    Returns
    -------
    pandas.DataFrame or List[Dict[str, Any]]

    Raises
    ------
    InvalidQueryError
        If parameters are invalid.
    MissingCredentialsError, AuthenticationError, APIConnectionError, ServerError
        From underlying run_query() calls.
    """

    # -----------------------------
    # 1) Normalize & validate input
    # -----------------------------

    # Symbol normalization
    if symbol is not None:
        symbol = validate_symbol(symbol)

    # Enforce limit must be > 0 (no unbounded queries allowed)
    if limit is None:
        raise InvalidQueryError("limit must be > 0 (not None).")
    validate_limit(limit)

    # Normalize date strings first
    if start_date is not None:
        start_date = validate_date(start_date)
    if end_date is not None:
        end_date = validate_date(end_date)

    # Now that dates are normalized, validate ordering
    validate_date_range(start_date, end_date)

    # -----------------------------
    # 2) Build SQL
    # -----------------------------
    sql = build_stock_candles_query(
        symbol=symbol,
        stock_id=stock_id,
        resolution=resolution,
        start_timestamp=start_date,
        end_timestamp=end_date,
        limit=limit,
    )

    # -----------------------------
    # 3) Execute and convert
    # -----------------------------
    rows: DataRows = run_query(sql)

    if as_dataframe:
        return to_dataframe(rows)

    return rows
