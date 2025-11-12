from .insider_trades import get_insider_trades

__all__ = [
    # insider_trades
    'get_insider_trades',
]

__version__ = "1.0"

def describe_insider_trades():
    description = """
    AlpaxaQuant — Insider Trades Module Overview
    ============================================

    Provides structured access to insider trading data sourced from OpenInsider,
    enabling detection of ownership patterns, executive buy/sell behavior, and
    market-aligned sentiment shifts across thousands of equities.

    --------------------------------------------------------------------
    ▸ Core Functionality
    --------------------------------------------------------------------
    • get_insider_trades(config)
        Launches a fully configurable insider-trade scraper using multi-threaded
        batch execution and dynamic caching.

        Returns a pandas.DataFrame containing all insider transactions that
        match user-defined filters.

    --------------------------------------------------------------------
    ▸ Key Features
    --------------------------------------------------------------------
    • Multi-Threaded Collection
        Concurrent month-by-month scraping with automatic parallelization via
        ThreadPoolExecutor.

    • Smart Caching System
        Stores previously fetched monthly data in `.json` format to prevent
        redundant network requests and reduce API load.

    • Configurable Filters
        Define trade type, minimum value, ticker inclusion/exclusion, and
        minimum share count thresholds directly in the configuration dictionary.

    • Resilient Networking
        Integrated retry logic ensures reliable data retrieval with exponential
        backoff for transient network issues.

    • Data Cleaning and Standardization
        Automatically normalizes ticker symbols, trade dates, insider names,
        and numeric transaction fields (price, shares, value).

    --------------------------------------------------------------------
    ▸ Output Schema
    --------------------------------------------------------------------
    Each returned record includes:

        filing_date        — SEC filing date
        trade_date         — Actual trade execution date
        ticker             — Stock ticker symbol
        owner_name         — Insider name
        Title              — Insider’s corporate title
        transaction_type   — Transaction code (P, S, M, etc.)
        last_price         — Stock price at transaction
        Qty                — Shares traded
        shares_held        — Shares held after transaction
        Owned              — Ownership percentage (if available)
        Value              — Total transaction value in USD

    --------------------------------------------------------------------
    ▸ Supported Transaction Codes
    --------------------------------------------------------------------
    P — Purchase
    S — Sale
    A — Award or grant
    D — Disposition to issuer
    M — Option exercise
    G — Gift
    X — Exercise of derivative
    C — Conversion
    F — Payment of tax
    W — Will / Inheritance
    O — Other

    --------------------------------------------------------------------
    ▸ Example Usage
    --------------------------------------------------------------------
    >>> from alpaxa_quant.insider_trades import get_insider_trades
    >>> config = {
    ...     "scraping": {"start_year": 2024, "start_month": 6, "max_workers": 5, "retry_attempts": 3, "timeout": 30},
    ...     "filters": {"min_transaction_value": 10000, "transaction_types": ["P", "S"], "include_companies": ["TSLA", "NVDA"], "min_shares_traded": 500},
    ...     "cache": {"enabled": True, "directory": ".cache", "max_age": 12}
    ... }
    >>> df = get_insider_trades(config)
    >>> print(df.head())

    --------------------------------------------------------------------
    ▸ Integration & Design
    --------------------------------------------------------------------
    • Compatible with AlpaxaQuant’s event-driven ingestion pipelines
    • Returns normalized pandas DataFrames for direct use in model training
    • Provides detailed runtime logging and progress visualization (tqdm)

    --------------------------------------------------------------------
    ▸ Citation
    --------------------------------------------------------------------
    Inspired by and adapted from the openinsiderData project
    (https://github.com/sd3v/openinsiderData), modernized for robust modularity,
    reproducibility, and direct integration into AlpaxaQuant.
    """

    print(description)
