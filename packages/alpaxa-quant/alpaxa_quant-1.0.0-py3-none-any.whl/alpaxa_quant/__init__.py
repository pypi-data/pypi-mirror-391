"""
AlpaxaQuant — Quantitative Finance & Data Acquisition Library
=============================================================

AlpaxaQuant is a unified quantitative finance framework designed for
developers, researchers, and traders who require programmatic access to
financial, macroeconomic, and insider datasets. It integrates multiple
trusted data providers — EODHD, FINRA, and FRED — under a consistent,
modular Python interface.

Each submodule corresponds to a specialized data domain:
    - utils: Core request and data-handling utilities
    - eodhd: Market and fundamentals API wrapper
    - insider_trades: Insider transaction scraper and analyzer
    - finra: Market-structure and fixed-income data interface
    - fred: Macroeconomic and commodity time-series access layer
"""

from .insider_trades import insider_trades
from .eodhd import eodhd
from .finra import finra
from .utils import utils
from .fred import fred

__all__ = [
    'utils',
    'eodhd',
    'insider_trades',
    'finra',
    'fred',
]

__version__ = "1.0"


def describe():
    description = f"""
AlpaxaQuant Library
Version: {__version__}
------------------------------------------------------------

Overview:
    AlpaxaQuant is an end-to-end quantitative finance library built for
    data-driven research, trading system development, and econometric
    modeling. It unifies access to financial, fundamental, insider, and
    macroeconomic data under a single API layer.

Modules:
    • utils
        Core infrastructure for safe HTTP requests, JSON normalization,
        and authentication handling. Powers all data retrieval logic.

    • eodhd
        Direct interface with the EODHD API, providing:
            – OHLCV market data
            – Fundamentals (balance sheets, income statements, cash flow)
            – Technical indicators and sentiment metrics
            – Analyst ratings and news sentiment

    • insider_trades
        Advanced OpenInsider scraper delivering insider transactions for
        all U.S.-listed equities. Features:
            – Multi-threaded scraping
            – Intelligent caching
            – Extensive filtering (transaction type, min value, etc.)

    • finra
        Integrates FINRA’s fixed-income and equity datasets, including:
            – Short interest, block trades, OTC summaries
            – Debt market sentiment and breadth
            – Treasury aggregates and capped volume data

    • fred
        Comprehensive access to FRED’s macroeconomic and commodity datasets:
            – Inflation, GDP, employment, and housing indicators
            – Yields, credit spreads, monetary aggregates
            – Commodities and volatility indices (VIX family)

Usage:
    >>> import alpaxa_quant as aq
    >>> aq.describe()

License:
    Apache License 2.0 © 2025 Joan Mas Castella
    https://github.com/Joanmascastella/AlpaxaQuant
"""
    print(description.strip())
