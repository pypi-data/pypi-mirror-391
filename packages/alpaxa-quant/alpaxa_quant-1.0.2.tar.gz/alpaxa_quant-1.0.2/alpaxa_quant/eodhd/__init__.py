from .eodhd import (
    get_analyst_ratings, 
    get_ticker_valuation, 
    get_ticker_highlights, 
    get_earnings, get_financials, 
    get_general_ticker_info, 
    get_historical_ticker_price, 
    get_holders,
    get_insider_transactions,
    get_outstanding_shares,
    get_shares_stats,
    get_split_dividends,
    get_technicals,
    fetch_news_sentiment,
    )

__all__ = [
    # eodhd
    'get_analyst_ratings',
    'get_ticker_valuation',
    'get_ticker_highlights',
    'get_earnings',
    'get_financials',
    'get_general_ticker_info',
    'get_historical_ticker_price',
    'get_holders',
    'get_insider_transactions',
    'get_outstanding_shares',
    'get_shares_stats',
    'get_split_dividends',
    'get_technicals',
    'fetch_news_sentiment'
]

__version__ = "1.0"

def describe_eodhd():
    description = """
    AlpaxaQuant — EODHD Module Overview
    ===================================

    Provides complete integration with the EOD Historical Data API,
    enabling retrieval of equities, fundamentals, financials, and
    sentiment datasets in standardized, analysis-ready DataFrames.

    --------------------------------------------------------------------
    ▸ Price & Market Data
    --------------------------------------------------------------------
    • get_historical_ticker_price()
        Fetches OHLCV price data (daily, weekly, or monthly) for any ticker.

    --------------------------------------------------------------------
    ▸ Company Metadata & Fundamentals
    --------------------------------------------------------------------
    • get_general_ticker_info()
        Returns company profile data, identifiers (ISIN, CUSIP, LEI), 
        officers, listings, and sector classification.

    • get_ticker_highlights()
        Summarized financial highlights — profitability, growth, and 
        valuation metrics for quick equity screening.

    • get_ticker_valuation()
        Enterprise value and valuation ratios (P/E, P/B, EV/EBITDA, etc.)
        for cross-sectional or factor-based analysis.

    • get_financials()
        Retrieves complete Balance Sheet, Income Statement, or Cash Flow 
        data, either quarterly or annually.

    • get_earnings()
        Historical, forecasted, or annual EPS and revenue estimates with 
        analyst revisions and surprise data.

    • get_outstanding_shares()
        Annual or quarterly share count data for dilution and capital 
        structure analysis.

    --------------------------------------------------------------------
    ▸ Ownership & Insider Activity
    --------------------------------------------------------------------
    • get_holders()
        Institutional and fund ownership, share changes, and concentration
        metrics for institutional flow analysis.

    • get_insider_transactions()
        Insider trade records, including officer transactions, codes, 
        transaction values, and SEC filing links.

    • get_shares_stats()
        Share structure breakdown — float, insider/institutional 
        percentages, and short interest.

    --------------------------------------------------------------------
    ▸ Technical Indicators & Corporate Actions
    --------------------------------------------------------------------
    • get_technicals()
        Retrieves key trading statistics such as Beta, 52-week range,
        50/200-day moving averages, and short ratio metrics.

    • get_split_dividends()
        Dividend and stock split history, payout ratios, and forward 
        yield data.

    --------------------------------------------------------------------
    ▸ Sentiment & News Analytics
    --------------------------------------------------------------------
    • fetch_news_sentiment()
        Iteratively retrieves all historical news for a given ticker, 
        chunked by month, quarter, or year, including sentiment polarity 
        scores (positive, neutral, negative).

    --------------------------------------------------------------------
    Usage Example
    --------------------------------------------------------------------
    >>> from alpaxa_quant import eodhd
    >>> eodhd.get_historical_ticker_price(
    ...     base_endpoint="https://eodhd.com/api",
    ...     api_token="YOUR_API_KEY",
    ...     ticker="AAPL",
    ...     period="d"
    ... )

    Returns a pandas.DataFrame containing OHLCV records.

    --------------------------------------------------------------------
    All functions internally leverage:
    • make_safe_request() — standardized request handler with timeout,
      error handling, and verbose logging.

    Data returned is fully normalized into pandas DataFrames, ensuring
    smooth downstream compatibility with AlpaxaQuant pipelines, 
    modeling layers, and analytics workflows.
    """

    print(description)
