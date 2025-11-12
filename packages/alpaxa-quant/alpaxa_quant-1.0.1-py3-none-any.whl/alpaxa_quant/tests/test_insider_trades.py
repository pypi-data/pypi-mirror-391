import pytest
import pandas as pd
from unittest.mock import patch
from alpaxa_quant.insider_trades import get_insider_trades, OpenInsiderScraper

@pytest.fixture
def sample_config():
    """Return a minimal configuration for testing."""
    return {
        "scraping": {
            "start_year": 2024,
            "start_month": 1,
            "max_workers": 2,
            "retry_attempts": 1,
            "timeout": 10,
        },
        "filters": {
            "min_transaction_value": 0,
            "transaction_types": ["P"],
            "exclude_companies": [],
            "include_companies": ["AAOI"],
            "min_shares_traded": 0,
        },
        "cache": {
            "enabled": False,
            "directory": ".cache",
            "max_age": 24,
        },
    }


@pytest.fixture
def sample_dataframe():
    """Example mock DataFrame that resembles real output."""
    data = {
        "filing_date": ["2025-08-15", "2016-05-27"],
        "trade_date": ["2025-08-14", "2016-05-25"],
        "ticker": ["AAOI", "AAOI"],
        "owner_name": ["Lin Che-Wei", "Chen Min-Chu (Mike)"],
        "Title": ["Dir", "Dir"],
        "transaction_type": ["P", "P"],
        "last_price": [21.64, 9.98],
        "Qty": [4609, 10000],
        "shares_held": [253506, 33262],
        "Owned": [2.0, 43.0],
        "Value": [99739, 99750],
    }
    return pd.DataFrame(data)


@patch.object(OpenInsiderScraper, "scrape")
def test_get_insider_trades_returns_dataframe(mock_scrape, sample_config, sample_dataframe):
    """Ensure get_insider_trades returns a DataFrame when scraping succeeds."""
    mock_scrape.return_value = sample_dataframe

    df = get_insider_trades(sample_config)

    # Assertions
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert set(df.columns) == {
        "filing_date",
        "trade_date",
        "ticker",
        "owner_name",
        "Title",
        "transaction_type",
        "last_price",
        "Qty",
        "shares_held",
        "Owned",
        "Value",
    }
    assert (df["ticker"] == "AAOI").all()


@patch.object(OpenInsiderScraper, "scrape", side_effect=Exception("Network error"))
def test_get_insider_trades_raises_exception(mock_scrape, sample_config):
    """Verify that exceptions are propagated if scraping fails."""
    with pytest.raises(Exception) as exc_info:
        get_insider_trades(sample_config)

    assert "Network error" in str(exc_info.value)


def test_scraper_config_loaded_correctly(sample_config):
    """Ensure Scraper configuration is loaded properly."""
    scraper = OpenInsiderScraper(sample_config)
    cfg = scraper.config

    assert cfg.start_year == 2024
    assert cfg.start_month == 1
    assert cfg.max_workers == 2
    assert cfg.retry_attempts == 1
    assert cfg.timeout == 10
    assert cfg.min_transaction_value == 0
    assert cfg.transaction_types == ["P"]
    assert cfg.include_companies == ["AAOI"]
    assert not cfg.cache_enabled

if __name__ == "__main__":
    pytest.main([__file__])