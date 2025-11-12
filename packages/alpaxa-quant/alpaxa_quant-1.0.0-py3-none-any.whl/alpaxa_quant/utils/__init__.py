from .utils import make_safe_request, request_util, make_yf_request

__all__ = [
    # utils
    'make_safe_request',
    'request_util',
    'make_yf_request'
]

__version__ = "1.0"

def describe_utils():
    description = """
    AlpaxaQuant — Utils Module Overview
    ===================================

    Provides foundational helper functions for making secure, consistent, and
    well-structured API requests, ensuring that all AlpaxaQuant submodules share
    a common interface for request execution and data normalization.

    --------------------------------------------------------------------
    ▸ Core Functions
    --------------------------------------------------------------------
    • make_safe_request(endpoint, timeout=30, params=None, json=None, auth=False, jwt_key="")
        Performs a secure HTTP GET or POST request with optional bearer authentication.
        Returns the response as a pandas.DataFrame when JSON data is valid.

        - Handles both GET and POST methods transparently
        - Supports JWT bearer tokens for authenticated APIs (e.g., FINRA)
        - Provides debug logging and timeout control
        - Gracefully catches and reports network or parsing errors

    • request_util(params, base_url, verbose)
        Specialized wrapper for FRED API calls.
        Handles FRED-style JSON responses with nested "observations" and
        converts them into date-indexed DataFrames.

        - Ensures proper type conversion for date and value fields
        - Filters by observation start date
        - Integrates directly with FRED-related functions

    • make_yf_request(ticker, start_date, end_date, interval='1d', timeout=30)
        Executes a Yahoo Finance request for tickers not supported by other
        AlpaxaQuant data providers.

        - Uses the yfinance library for seamless data retrieval
        - Returns adjusted OHLCV data as a pandas.DataFrame
        - Supports intervals from 1 minute to 3 months

    --------------------------------------------------------------------
    ▸ Internal Normalization
    --------------------------------------------------------------------
    • _normalize_to_df(payload)
        Safely converts diverse JSON payloads (lists, dicts, nested dicts)
        into clean pandas DataFrames.

        - Supports complex hierarchical JSON structures
        - Normalizes scalar or nested key/value pairs
        - Used internally by make_safe_request and other adapters

    --------------------------------------------------------------------
    ▸ Integration
    --------------------------------------------------------------------
    - All network-bound modules (EODHD, FINRA, FRED) depend on utils for
      reliable request execution and consistent output structure.
    - The normalization layer ensures uniform column naming and type safety.
    - Enables reusable ETL components and data ingestion within AlpaxaQuant.

    --------------------------------------------------------------------
    ▸ Example Usage
    --------------------------------------------------------------------
    >>> from alpaxa_quant.utils import make_safe_request
    >>> df = make_safe_request("https://api.finra.org/data/group/otcMarket/name/weeklySummary",
    ...                        timeout=20, verbose=True)
    >>> print(df.head())

    --------------------------------------------------------------------
    ▸ Summary
    --------------------------------------------------------------------
    The utils module forms the backbone of AlpaxaQuant’s data architecture.
    It abstracts request logic, manages authentication, and provides reliable
    JSON-to-DataFrame transformation across all integrated financial datasets.
    """

    print(description)
