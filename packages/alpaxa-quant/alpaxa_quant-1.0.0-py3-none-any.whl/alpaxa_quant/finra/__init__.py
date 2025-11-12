from .finra import (
    get_agency_debt_market_breadth,
    get_agency_debt_market_sentiment,
    get_bearer_token,
    get_blocks_summary,
    get_consolidated_short_interest,
    get_corporate_and_agency_capped_volume,
    get_corporate_debt_market_breadth,
    get_corporate_debt_market_sentiment,
    get_daily_short_volume_sale,
    get_monthly_summary,
    get_otc_block_summary,
    get_securitized_product_capped_volume,
    get_treasury_daily_aggregates,
    get_treasury_monthly_aggregates,
    get_weekly_summary
)

__all__ = [
    # finra
    'get_agency_debt_market_breadth',
    'get_agency_debt_market_sentiment',
    'get_bearer_token',
    'get_blocks_summary',
    'get_consolidated_short_interest',
    'get_corporate_and_agency_capped_volume',
    'get_corporate_debt_market_breadth',
    'get_corporate_debt_market_sentiment',
    'get_daily_short_volume_sale',
    'get_monthly_summary',
    'get_otc_block_summary',
    'get_securitized_product_capped_volume',
    'get_treasury_daily_aggregates',
    'get_treasury_monthly_aggregates',
    'get_weekly_summary',
]

__version__ = "1.0"

def describe_finra():
    description = """
    AlpaxaQuant — FINRA Module Overview
    ===================================

    Provides authenticated access to the Financial Industry Regulatory Authority (FINRA)
    APIs through standardized, paginated, and schema-consistent request handlers.

    This module enables retrieval of both equity and fixed-income datasets including
    short interest, block trading summaries, OTC/ATS activity, and market sentiment.

    --------------------------------------------------------------------
    ▸ Authentication
    --------------------------------------------------------------------
    • get_bearer_token()
        Retrieves an OAuth2 bearer token using FINRA FIP client credentials
        for authenticated API access.

    --------------------------------------------------------------------
    ▸ Equity and OTC Market Data
    --------------------------------------------------------------------
    • get_blocks_summary()
        Aggregated ATS trade data for NMS stocks meeting share and dollar
        volume thresholds.

    • get_otc_block_summary()
        Aggregated OTC (non-ATS) block trade data across NMS securities.

    • get_consolidated_short_interest()
        Consolidated short interest by ticker, including position size,
        change rates, and settlement details.

    • get_daily_short_volume_sale()
        Daily short sale volume data from FINRA Reg SHO reports.

    • get_weekly_summary()
        Weekly OTC Market summary of share quantities, trade counts, and
        participant-level metrics (12-month rolling window).

    • get_monthly_summary()
        Monthly OTC Market summary with firm identifiers and product type
        metadata, supporting up to four years of history.

    --------------------------------------------------------------------
    ▸ Fixed Income Market Data
    --------------------------------------------------------------------
    • get_agency_debt_market_breadth()
        Breadth metrics for the U.S. agency debt market (fixed income).

    • get_agency_debt_market_sentiment()
        Sentiment indicators across agency debt instruments.

    • get_corporate_debt_market_breadth()
        Breadth and participation statistics for the corporate bond market.

    • get_corporate_debt_market_sentiment()
        Sentiment data reflecting trading tone and flow in corporate bonds.

    • get_corporate_and_agency_capped_volume()
        Combined capped trade volume data for corporate and agency securities.

    • get_securitized_product_capped_volume()
        Aggregate capped trading volumes across securitized products (MBS, ABS, CDOs).

    • get_treasury_daily_aggregates()
        Daily U.S. Treasury aggregate trading volume and participation data.

    • get_treasury_monthly_aggregates()
        Monthly Treasury market aggregates for broader temporal analysis.

    --------------------------------------------------------------------
    Usage Example
    --------------------------------------------------------------------
    >>> from alpaxa_quant import finra
    >>> token, _ = finra.get_bearer_token(client_id, client_secret)
    >>> df = finra.get_consolidated_short_interest(jwt_token=token, ticker="AAPL")

    Returns a pandas.DataFrame with standardized column naming.

    --------------------------------------------------------------------
    Internal Integration
    --------------------------------------------------------------------
    • All endpoints leverage make_safe_request() for consistent timeout,
      retry, and authentication handling.
    • Supports pagination (offset, limit) and automatic aggregation across
      requests for full historical coverage.

    Designed for scalable ingestion of FINRA-regulated trade data, the
    module provides a unified structure for both equity and fixed-income
    analysis pipelines within AlpaxaQuant.
    """

    print(description)
