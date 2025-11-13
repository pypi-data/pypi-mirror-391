# 📦 Enode Quant SDK

**Author:** Oscar Thiele Serrano

**Context:** ESADE ENODE Association – Quant Finance Team (student quant fund)

A lightweight, beginner-friendly Python SDK for accessing Enode's internal **market data** (stocks, options, and candles) stored in our AWS RDS PostgreSQL database.

This library is for **our team**: it standardises how we fetch data for research, prototyping, and strategy development.

---

## 🧭 Overview

The Enode Quant SDK lets researchers work with market data using simple Python functions instead of SQL.

Example:

```python
from enode_quant import get_stock_quotes, get_option_contracts

get_stock_quotes("AAPL")
get_option_contracts("AAPL", option_type="call")
get_stock_candles("AAPL")
```

The SDK provides:

- High-level Python functions for stocks, options, and candles
- A built-in CLI for authentication (`enode login`)
- Secure local credential storage
- SQL query builders (users never write SQL)
- Optional pandas DataFrame output
- Clean error handling and a simple API surface

Designed to be usable by both beginners and more advanced quants in the ENODE team.

---

## 🌳 Project Structure

```
enode_quant/
├── __init__.py            # Public shortcuts (lazy imports)
│
├── api/                   # High-level data access (researcher-facing)
│   ├── candles.py         # Stock OHLCV / candles helper functions
│   ├── options.py         # Option contracts & option quotes
│   └── stocks.py          # Stocks, L1 quotes, stock metadata
│
├── cli/                   # Authentication CLI (`enode login`, `whoami`)
│   ├── login.py
│   ├── logout.py
│   ├── main.py            # Defines the `enode` CLI entrypoint
│   └── whoami.py
│
├── client.py              # Core HTTP client → API Gateway → Lambda → RDS
├── config.py              # Loads/stores ~/.enode/credentials
├── errors.py              # Custom SDK exception classes
│
├── sql/                   # SQL query builders
│   ├── option_queries.py
│   ├── stock_queries.py
│   └── utils.py
│
└── utils/                 # Internal helpers
    ├── df_helpers.py      # Convert raw rows → pandas DataFrame
    └── validation.py      # Validation for symbols, dates, limits, etc.

# Top-level project files
├── pyproject.toml         # Package metadata & dependencies
├── README.md              # Main SDK documentation
├── DATABASE_SCHEMA.md     # Internal description of the market schema
└── test.ipynb             # Local notebook for testing the SDK

```

---

## 🔐 Authentication & Credentials

Each team member authenticates once using the CLI:

```bash
enode login
```

You will be prompted for:

- **API URL** (our API Gateway endpoint)
- **API Key** (hidden input)

Credentials are stored securely in:

```
~/.enode/credentials
```

Check the current login:

```bash
enode whoami
```

Log out:

```bash
enode logout
```

This keeps our fund's data secure while staying simple for everyone.

---

## 🧪 Quick Start

### 1. Install

From PyPI:

```bash
pip install enode-quant
```

or

```bash
uv add enode-quant  # if using uv (recommended)
```

### 2. Fetch Stock Quotes

```python
from enode_quant import get_stock_quotes

df = get_stock_quotes(
    symbol="AAPL",
    start_date="2024-01-01",
    end_date="2024-02-01",
    limit=200,
    as_dataframe=True,
)

print(df.head())
```

### 3. Fetch Option Contracts

```python
from enode_quant import get_option_contracts

contracts = get_option_contracts(
    symbol="AAPL",
    option_type="call",         # "put" or "both"
    expiration_before="2025-12-01",
    as_dataframe=True,
)

print(contracts.head())
```

### 4. Fetch Candles (OHLCV)

```python
from enode_quant import get_stock_candles

candles = get_stock_candles(
    symbol="AAPL",
    resolution="1D",            # depends on how we store data
    start_date="2024-01-01",
    end_date="2024-02-01",
    limit=200,
    as_dataframe=True,
)

print(candles.head())
```

All high-level functions support flexible filters, such as:

- `symbol` or `stock_id`
- `start_date` and `end_date`
- `option_type` (call / put / both)
- expiration windows
- `resolution` (for candles)
- `limit`
- `as_dataframe` (True/False)

---

## 🧱 How the SDK Works (Short Version)

When you call something like:

```python
get_stock_quotes("AAPL")
```

internally the SDK:

1. Loads your credentials from `~/.enode/credentials`
2. Builds a safe SQL query (using the `sql` helpers)
3. Sends the query to API Gateway via HTTP
4. API Gateway triggers the Lambda DB worker
5. Lambda executes the query on PostgreSQL (RDS)
6. The result is returned as JSON and (optionally) converted into a pandas DataFrame

Errors are mapped to clear Python exceptions:

- `MissingCredentialsError`
- `AuthenticationError`
- `APIConnectionError`
- `ServerError`

So researchers don't have to debug HTTP or SQL directly.

---

## 🧰 Available Modules

### Stocks (`enode_quant.api.stocks`)

- `get_stock_quotes(...)`

### Options (`enode_quant.api.options`)

- `get_option_contracts(...)`
- `get_option_quotes(...)`

### Candles (`enode_quant.api.candles`)

- `get_stock_candles(...)`

### Core

- `run_query(sql)` – low-level query runner (normally not needed by beginners)
- `sql_literal(...)` – helper for building safe SQL values
- `apply_date_filters(...)` – shared date filter helper

### CLI

- `enode login`
- `enode whoami`
- `enode logout`

---

## 🎯 Design Principles (for the ENODE Quant Team)

- **Beginner-friendly** – new members can get data with just a few lines of Python
- **Flexible** – advanced users can control filters and parameters
- **Safe** – validated inputs and no raw SQL from users
- **Extensible** – easy to add new functions as our database grows

Planned future extensions (not implemented yet, but on the roadmap):

- A backtesting module that uses the same data layer
- A quant-finance utilities module (risk, stats, indicators) for research

---

## 🛠️ Troubleshooting

| Problem           | Error                     | Solution                    |
|-------------------|---------------------------|-----------------------------|
| Not logged in     | `MissingCredentialsError` | Run `enode login`           |
| Wrong API key     | `AuthenticationError`     | Re-run `enode login`        |
| Bad URL / network | `APIConnectionError`      | Check URL and connectivity  |
| Schema mismatch   | `ServerError`             | Update SDK or fix the query |
