# enode_quant/__init__.py

"""
Public shortcuts for Enode Quant SDK.
These use lazy imports to avoid circular dependencies.
"""

def get_stock_quotes(*args, **kwargs):
    from enode_quant.api.stocks import get_stock_quotes as _impl
    return _impl(*args, **kwargs)

def get_stock_candles(*args, **kwargs):
    from enode_quant.api.stocks import get_stock_candles as _impl
    return _impl(*args, **kwargs)

def get_option_contracts(*args, **kwargs):
    from enode_quant.api.options import get_option_contracts as _impl
    return _impl(*args, **kwargs)

def get_option_quotes(*args, **kwargs):
    from enode_quant.api.options import get_option_quotes as _impl
    return _impl(*args, **kwargs)

def get_stocks(*args, **kwargs):
    from enode_quant.api.stocks import get_stocks as _impl
    return _impl(*args, **kwargs)

__all__ = [
    "get_stock_quotes",
    "get_stock_candles",
    "get_option_contracts",
    "get_option_quotes",
    "get_stocks"
]
