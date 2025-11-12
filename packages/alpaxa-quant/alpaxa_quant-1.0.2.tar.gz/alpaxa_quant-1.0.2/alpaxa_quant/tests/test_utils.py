from alpaxa_quant.config import return_EODHD_base_api_endpoint, return_EODHD_test_api_key
from alpaxa_quant.utils import make_safe_request
import pandas as pd
import pytest

def test_make_safe_request():
    e = return_EODHD_base_api_endpoint()
    k = return_EODHD_test_api_key()

    # Construct query paramteres 
    params = {
        "api_token": k,
        "period": 'd',
        "order": 'a',
        "fmt": 'json',
    }
    # Set up endpoint 
    constructed_endpoint=f"{e}/TSLA.US"

    # Testing make request
    df = make_safe_request(endpoint=constructed_endpoint, timeout=10, params=params, verbose=True)
    
    assert df is not None, "Expected non-empty DataFrame"
    assert isinstance(df, pd.DataFrame), "Response should be a pandas DataFrame"
    assert not df.empty, "Expected data in DataFrame"

    # Validate key columns exist
    for col in ["date", "open", "high", "low", "close", "adjusted_close", "volume"]:
        assert col in df.columns, f"Missing column: {col}"

    # Check if the date returned follows the date range
    assert "2017-01-05" in df["date"].values, "Expected start date missing"
    assert "2017-01-10" in df["date"].values, "Expected end date missing"

if __name__ == "__main__":
    pytest.main([__file__])