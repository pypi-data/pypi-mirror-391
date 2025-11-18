"""
SQL builders for market.stocks, market.stock_quotes, and market.stock_candles.

These builders accept validated parameters and return SQL strings.
They:
- Fully qualify schema (market.*)
- Always join stocks so users can filter by symbol
- Apply date filters, resolution filters, quote type filters
- Provide safe defaults (latest first ordering, sane limits)
- Keep API layer simple and pure
"""

from __future__ import annotations

from typing import Optional

from enode_quant.sql.utils import (
    sql_literal,
    apply_date_filters,
    apply_limit,
    combine_where,
    order_by,
)


# ---------------------------------------------------------------------------
# STOCK LIST
# ---------------------------------------------------------------------------

def build_get_stocks_query(
    symbol: Optional[str] = None,
    limit: Optional[int] = None,   # default: return *all* unless user restricts
) -> str:
    """
    Build SQL for the stocks master table.

    Default behavior: return all symbols alphabetically.
    This makes sense because the rows are few (e.g. ~8000 max).

    Parameters
    ----------
    symbol : str, optional
    limit : int, optional

    Returns
    -------
    str
    """
    clauses = []

    if symbol:
        clauses.append(f"s.symbol = {sql_literal(symbol)}")

    where_clause = combine_where(clauses)
    order_clause = order_by(column="s.symbol", desc=False)
    limit_clause = apply_limit(limit)

    return f"""
    SELECT
        s.stock_id,
        s.symbol
    FROM market.stocks AS s
    {where_clause}
    {order_clause}
    {limit_clause}
    """.strip()



# ---------------------------------------------------------------------------
# QUOTES (L1)
# ---------------------------------------------------------------------------

def build_stock_quotes_query(
    symbol: Optional[str] = None,
    stock_id: Optional[int] = None,
    start_timestamp: Optional[str] = None,
    end_timestamp: Optional[str] = None,
    quote_type: Optional[str] = None,
    limit: int = 100,  # default: retrieve last 100 rows (reasonable + safe)
) -> str:
    """
    Default behavior:
        get_stock_quotes("AAPL") -> last 100 AAPL quotes, latest-first.

    Parameters
    ----------
    symbol : optional
        Human-friendly filter (preferred).
    stock_id : optional
        Internal filter (ETL / advanced usage).
    start_timestamp, end_timestamp : optional
    quote_type : optional
        e.g. 'bid', 'ask', 'mid', 'last'
    limit : int
        Must be > 0. Defaults to 100 for safety.

    Returns
    -------
    str
    """

    clauses = []

    # Support both symbol and stock_id
    if stock_id is not None:
        clauses.append(f"q.stock_id = {sql_literal(stock_id)}")

    if symbol:
        clauses.append(f"s.symbol = {sql_literal(symbol)}")

    if quote_type:
        clauses.append(f"q.quote_type = {sql_literal(quote_type)}")

    # Timestamp filters
    clauses.extend(
        apply_date_filters(
            start_date=start_timestamp,
            end_date=end_timestamp,
            column="q.timestamp",
        )
    )

    where_clause = combine_where(clauses)
    order_clause = order_by(column="q.timestamp", desc=True)
    limit_clause = apply_limit(limit)

    return f"""
    SELECT
        q.quote_id,
        q.stock_id,
        s.symbol,
        q.timestamp,
        q.quote_type,
        q.bid,
        q.bid_size,
        q.ask,
        q.ask_size,
        q.mid,
        q.last
    FROM market.stock_quotes AS q
    JOIN market.stocks AS s
        ON q.stock_id = s.stock_id
    {where_clause}
    {order_clause}
    {limit_clause}
    """.strip()



# ---------------------------------------------------------------------------
# OHLCV CANDLES
# ---------------------------------------------------------------------------

def build_stock_candles_query(
    symbol: Optional[str] = None,
    stock_id: Optional[int] = None,
    resolution: Optional[str] = None,
    start_timestamp: Optional[str] = None,
    end_timestamp: Optional[str] = None,
    limit: int = 500,  # default: return last 500 candles (safe for charts)
) -> str:
    """
    Default behavior:
        get_stock_candles("AAPL") -> last 500 candles (latest-first).

    Parameters
    ----------
    symbol : optional
    stock_id : optional
    resolution : str, optional  (e.g. '1H', '1D')
    start_timestamp, end_timestamp : optional
    limit : int (default=500)

    Returns
    -------
    str
    """

    clauses = []

    if stock_id is not None:
        clauses.append(f"c.stock_id = {sql_literal(stock_id)}")

    if symbol:
        clauses.append(f"s.symbol = {sql_literal(symbol)}")

    if resolution:
        clauses.append(f"c.resolution = {sql_literal(resolution)}")

    clauses.extend(
        apply_date_filters(
            start_date=start_timestamp,
            end_date=end_timestamp,
            column="c.timestamp",
        )
    )

    where_clause = combine_where(clauses)
    order_clause = order_by(column="c.timestamp", desc=True)
    limit_clause = apply_limit(limit)

    return f"""
    SELECT
        c.stock_id,
        s.symbol,
        c.timestamp,
        c.resolution,
        c.open,
        c.high,
        c.low,
        c.close,
        c.volume
    FROM market.stock_candles AS c
    JOIN market.stocks AS s
        ON c.stock_id = s.stock_id
    {where_clause}
    {order_clause}
    {limit_clause}
    """.strip()
