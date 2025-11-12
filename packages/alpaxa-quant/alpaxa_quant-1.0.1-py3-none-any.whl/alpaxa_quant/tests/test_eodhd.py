from alpaxa_quant.config import return_EODHD_base_api_endpoint, return_EODHD_test_api_key
from alpaxa_quant.eodhd import (
    get_historical_ticker_price, 
    get_insider_transactions,
    get_general_ticker_info, 
    get_outstanding_shares,
    get_ticker_highlights, 
    get_ticker_valuation,
    fetch_news_sentiment,
    get_analyst_ratings,
    get_split_dividends,
    get_shares_stats,
    get_technicals,
    get_financials,
    get_earnings,
    get_holders,
)
import pandas as pd
import pytest


def test_historical_ticker_price():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_historical_ticker_price(
        base_endpoint=e,
        api_token=k,
        ticker="TSLA",
        fmt="json",
        period="d",
        from_date="2017-05-01",
        to_date="2017-05-25",
        verbose=True,
    )

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    for col in ["date", "open", "high", "low", "close", "adjusted_close", "volume"]:
        assert col in df.columns


def test_general_ticker_info():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_general_ticker_info(base_endpoint=e, api_token=k, ticker="AAPL", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_ticker_highlights():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_ticker_highlights(base_endpoint=e, api_token=k, ticker="AAPL", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_ticker_valuation():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_ticker_valuation(base_endpoint=e, api_token=k, ticker="AAPL", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_shares_stats():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_shares_stats(base_endpoint=e, api_token=k, ticker="AAPL", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_technicals():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_technicals(base_endpoint=e, api_token=k, ticker="AAPL", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_split_dividends():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_split_dividends(base_endpoint=e, api_token=k, ticker="AAPL", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_analyst_ratings():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_analyst_ratings(base_endpoint=e, api_token=k, ticker="AAPL", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_holders_institutions():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_holders(base_endpoint=e, api_token=k, ticker="AAPL", holder_type="institutions", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_insider_transactions():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_insider_transactions(base_endpoint=e, api_token=k, ticker="AAPL", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_outstanding_shares():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_outstanding_shares(base_endpoint=e, api_token=k, ticker="AAPL", period="annual", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_earnings_trend():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_earnings(base_endpoint=e, api_token=k, ticker="AAPL", period="trend", verbose=True)
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_financials_balance_sheet_quarterly():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = get_financials(
        base_endpoint=e,
        api_token=k,
        ticker="AAPL",
        period="quarterly",
        financial_type="Balance_Sheet",
        verbose=True,
    )
    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

def test_fetch_news_sentiment():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    df = fetch_news_sentiment(
        base_endpoint=e,
        api_token=k,
        ticker="AAPL",
        start_date="2016-01-01",
        chunk="year",
        verbose=True
    )

    # Basic validations
    assert df is not None, "Returned DataFrame is None"
    assert isinstance(df, pd.DataFrame), "Returned object is not a DataFrame"
    assert not df.empty, "Returned DataFrame is empty"

    # Column structure checks
    expected_cols = ["date", "symbols", "tags", "polarity", "neg", "neu", "pos"]
    for col in expected_cols:
        assert col in df.columns, f"Missing expected column: {col}"

    # Value integrity
    assert df["date"].notnull().all(), "Date column contains null values"
    assert df["polarity"].between(-1, 1).all(), "Polarity values out of expected range"
    assert df["neg"].between(0, 1).all(), "Negative sentiment values out of range"
    assert df["pos"].between(0, 1).all(), "Positive sentiment values out of range"


if __name__ == "__main__":
    pytest.main([__file__])
