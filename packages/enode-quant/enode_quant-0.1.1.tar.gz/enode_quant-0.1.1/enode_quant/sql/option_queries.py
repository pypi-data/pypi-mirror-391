"""
SQL builders for option contracts and option quotes.

These builders:
- Fully qualify tables in the `market` schema.
- Join through `market.stocks` so users can work with symbols instead
  of stock_id.
- For quotes, also join market.option_contract so expiry/strike filters
  can be applied even when only quote data is stored in option_quotes.
- Provide safe defaults for ordering (latest-first) and limits.

Input validation (e.g., symbol format, date ranges, strike ranges,
option_type) is handled in enode_quant/utils/validation.py.
This module assumes parameters are already validated and only focuses
on generating correct SQL.
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
# NOTE: if you later add validation-specific behavior (e.g., enforcing that
# either symbol or stock_id is required), that should live in the validation
# layer or API functions, not here.


# ---------------------------------------------------------------------------
# OPTION CONTRACTS
# ---------------------------------------------------------------------------

def build_option_contracts_query(
    symbol: Optional[str] = None,
    stock_id: Optional[int] = None,
    option_type: Optional[str] = None,          # "call" or "put"
    expiration_date: Optional[str] = None,      # exact expiry
    expiration_after: Optional[str] = None,     # lower bound (>=)
    expiration_before: Optional[str] = None,    # upper bound (<=)
    min_strike: Optional[float] = None,
    max_strike: Optional[float] = None,
    occ_symbol: Optional[str] = None,
    limit: int = 200,
) -> str:
    """
    Build a SQL query for option contracts from market.option_contract,
    joined with market.stocks so symbol-based filtering is always available.

    Default behavior:
        build_option_contracts_query()  ->  latest contracts, up to `limit`.

    Parameters
    ----------
    symbol : str, optional
        Underlying equity symbol. If provided, joins stocks and filters
        on s.symbol.
    stock_id : int, optional
        Underlying stock_id. Can be used instead of or in addition to symbol.
    option_type : str, optional
        "call" or "put".
    expiration_date : str, optional
        Exact expiration date (ISO string). If provided, takes precedence
        over expiration_before/expiration_after for equality.
    expiration_after : str, optional
        Lower bound on expiration date (>=).
    expiration_before : str, optional
        Upper bound on expiration date (<=).
    min_strike : float, optional
        Minimum strike (>=).
    max_strike : float, optional
        Maximum strike (<=).
    occ_symbol : str, optional
        OCC-style symbol, if you store it (e.g. for US options).
    limit : int, optional
        Maximum number of rows to return. Defaults to 200.

    Returns
    -------
    str
        SQL string selecting option contracts with underlying symbol.
    """
    clauses = []

    if stock_id is not None:
        clauses.append(f"c.stock_id = {sql_literal(stock_id)}")

    if symbol:
        clauses.append(f"s.symbol = {sql_literal(symbol)}")

    if option_type:
        clauses.append(f"c.option_type = {sql_literal(option_type)}")

    if occ_symbol:
        clauses.append(f"c.occ_symbol = {sql_literal(occ_symbol)}")

    # Expiration filters
    if expiration_date:
        clauses.append(f"c.expiration_date = {sql_literal(expiration_date)}")
    else:
        # Use date range if no exact expiry is specified
        clauses.extend(
            apply_date_filters(
                start_date=expiration_after,
                end_date=expiration_before,
                column="c.expiration_date",
            )
        )

    # Strike range filters
    if min_strike is not None:
        clauses.append(f"c.strike_price >= {sql_literal(min_strike)}")

    if max_strike is not None:
        clauses.append(f"c.strike_price <= {sql_literal(max_strike)}")

    where_clause = combine_where(clauses)
    # Ordering: group by underlying, then expiry, then strike
    order_clause = (
        "ORDER BY s.symbol ASC, c.expiration_date ASC, c.strike_price ASC"
    )
    limit_clause = apply_limit(limit)

    return f"""
    SELECT
        c.option_id,
        c.stock_id,
        s.symbol,
        c.occ_symbol,
        c.expiration_date,
        c.strike_price,
        c.option_type,
        c.first_seen
    FROM market.option_contracts AS c
    JOIN market.stocks AS s
        ON c.stock_id = s.stock_id
    {where_clause}
    {order_clause}
    {limit_clause}
    """.strip()



# ---------------------------------------------------------------------------
# OPTION QUOTES (TIME SERIES)
# ---------------------------------------------------------------------------

def build_option_quotes_query(
    symbol: Optional[str] = None,
    stock_id: Optional[int] = None,
    option_id: Optional[int] = None,
    option_type: Optional[str] = None,
    expiration_date: Optional[str] = None,
    expiration_after: Optional[str] = None,
    expiration_before: Optional[str] = None,
    min_strike: Optional[float] = None,
    max_strike: Optional[float] = None,
    start_timestamp: Optional[str] = None,
    end_timestamp: Optional[str] = None,
    in_the_money: Optional[bool] = None,
    limit: int = 500,
) -> str:
    """
    Build a SQL query for option quotes from market.option_quotes,
    joined with market.option_contract and market.stocks.

    This allows users to filter quotes by:
        - underlying symbol or stock_id
        - option_id
        - expiration (exact or range)
        - strike range
        - option_type (call/put)
        - in_the_money flag
        - time window on quote timestamp

    Default behavior:
        build_option_quotes_query(symbol="AAPL")
        -> last `limit` quotes for all AAPL options (all expiries/strikes),
           ordered by timestamp DESC.

    Parameters
    ----------
    symbol : str, optional
        Underlying equity symbol.
    stock_id : int, optional
        Underlying stock_id.
    option_id : int, optional
        Specific option contract ID.
    option_type : str, optional
        "call" or "put".
    expiration_date : str, optional
        Exact expiration date (column c.expiration_date).
    expiration_after : str, optional
        Lower bound on expiry.
    expiration_before : str, optional
        Upper bound on expiry.
    min_strike, max_strike : float, optional
        Strike range filters.
    start_timestamp, end_timestamp : str, optional
        Time window on q.timestamp.
    in_the_money : bool, optional
        Filter on q.in_the_money column if present (True/False).
    limit : int, optional
        Maximum number of rows to return. Defaults to 500.

    Returns
    -------
    str
        SQL string selecting option quotes, with contract and symbol info.
    """
    clauses = []

    # Direct option_id filter, if provided
    if option_id is not None:
        clauses.append(f"q.option_id = {sql_literal(option_id)}")

    # Underlying filters
    if stock_id is not None:
        clauses.append(f"c.stock_id = {sql_literal(stock_id)}")

    if symbol:
        clauses.append(f"s.symbol = {sql_literal(symbol)}")

    # Contract-level filters
    if option_type:
        clauses.append(f"c.option_type = {sql_literal(option_type)}")

    if expiration_date:
        clauses.append(f"c.expiration_date = {sql_literal(expiration_date)}")
    else:
        clauses.extend(
            apply_date_filters(
                start_date=expiration_after,
                end_date=expiration_before,
                column="c.expiration_date",
            )
        )

    if min_strike is not None:
        clauses.append(f"c.strike_price >= {sql_literal(min_strike)}")

    if max_strike is not None:
        clauses.append(f"c.strike_price <= {sql_literal(max_strike)}")

    if in_the_money is not None:
        clauses.append(f"q.in_the_money = {sql_literal(in_the_money)}")

    # Time filters on quote timestamp
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
        q.option_quote_id,
        q.option_id,
        c.stock_id,
        s.symbol,
        c.occ_symbol,
        c.expiration_date,
        c.strike_price,
        c.option_type,
        q.timestamp,
        q.bid,
        q.bid_size,
        q.mid,
        q.ask,
        q.ask_size,
        q.last,
        q.volume,
        q.open_interest,
        q.underlying_price,
        q.in_the_money,
        q.intrinsic_value,
        q.iv,
        q.delta,
        q.gamma,
        q.theta,
        q.vega
    FROM market.option_quotes AS q
    JOIN market.option_contracts AS c
        ON q.option_id = c.option_id
    JOIN market.stocks AS s
        ON c.stock_id = s.stock_id
    {where_clause}
    {order_clause}
    {limit_clause}
    """.strip()
