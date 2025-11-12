import pytest
import pandas as pd
from alpaxa_quant.config import return_FINRA_client_id, return_FINRA_client_secret
from alpaxa_quant.finra import (
    get_bearer_token,
    get_blocks_summary,
    get_consolidated_short_interest,
    get_monthly_summary,
    get_otc_block_summary,
    get_daily_short_volume_sale,
    get_weekly_summary,
    get_agency_debt_market_breadth,
    get_agency_debt_market_sentiment,
    get_corporate_debt_market_breadth,
    get_corporate_debt_market_sentiment,
    get_corporate_and_agency_capped_volume,
    get_securitized_product_capped_volume,
    get_treasury_daily_aggregates,
    get_treasury_monthly_aggregates,
)


@pytest.fixture(scope="session")
def jwt_token():
    """Obtain a live FINRA bearer token for all tests."""
    cid = return_FINRA_client_id()
    secret = return_FINRA_client_secret()
    token, exp = get_bearer_token(cid, secret)
    assert isinstance(token, str) and len(token) > 10, "Token retrieval failed"
    return token


def _check_dataframe(df: pd.DataFrame):
    assert df is not None, "Expected a DataFrame"
    assert isinstance(df, pd.DataFrame)
    assert not df.empty, "DataFrame should not be empty"
    assert len(df.columns) > 0, "Expected columns present"


def test_blocks_summary(jwt_token):
    df = get_blocks_summary(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


def test_consolidated_short_interest(jwt_token):
    df = get_consolidated_short_interest(jwt_token, ticker="AAPL", limit=10, verbose=True)
    _check_dataframe(df)
    assert "symbolCode" in df.columns


def test_monthly_summary(jwt_token):
    df = get_monthly_summary(jwt_token, ticker="AAPL", limit=10, verbose=True)
    _check_dataframe(df)
    assert "issueSymbolIdentifier" in df.columns


def test_otc_block_summary(jwt_token):
    df = get_otc_block_summary(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


def test_daily_short_volume_sale(jwt_token):
    df = get_daily_short_volume_sale(jwt_token, ticker="AAPL", limit=10, verbose=True)
    _check_dataframe(df)
    assert "securitiesInformationProcessorSymbolIdentifier" in df.columns


def test_weekly_summary(jwt_token):
    df = get_weekly_summary(jwt_token, ticker="AAPL", limit=10, verbose=True)
    _check_dataframe(df)


def test_agency_debt_market_breadth(jwt_token):
    df = get_agency_debt_market_breadth(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


def test_agency_debt_market_sentiment(jwt_token):
    df = get_agency_debt_market_sentiment(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


def test_corporate_debt_market_breadth(jwt_token):
    df = get_corporate_debt_market_breadth(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


def test_corporate_debt_market_sentiment(jwt_token):
    df = get_corporate_debt_market_sentiment(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


def test_corporate_and_agency_capped_volume(jwt_token):
    df = get_corporate_and_agency_capped_volume(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


def test_securitized_product_capped_volume(jwt_token):
    df = get_securitized_product_capped_volume(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


def test_treasury_daily_aggregates(jwt_token):
    df = get_treasury_daily_aggregates(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


def test_treasury_monthly_aggregates(jwt_token):
    df = get_treasury_monthly_aggregates(jwt_token, limit=10, verbose=True)
    _check_dataframe(df)


if __name__ == "__main__":
    pytest.main([__file__])
