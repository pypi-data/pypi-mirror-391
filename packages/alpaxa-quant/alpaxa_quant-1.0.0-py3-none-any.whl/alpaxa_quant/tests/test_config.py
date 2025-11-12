from alpaxa_quant.config import return_EODHD_base_api_endpoint, return_EODHD_test_api_key, return_FRED_base_api_endpoint, return_FRED_test_api_key
from dotenv import load_dotenv
import pytest
import os

load_dotenv(".env")

def test_dotenv_variables():
    # Check that the API key and base endpoint matches what is saved in the env
    assert return_EODHD_base_api_endpoint() == os.getenv("TEST_EODHD_BASE_ENDPOINT")
    assert return_EODHD_test_api_key()      == os.getenv("TEST_EODHD_API_KEY")
    assert return_FRED_test_api_key()       == os.getenv("TEST_FRED_API_KEY")
    assert return_FRED_base_api_endpoint()  == os.getenv("TEST_FRED_BASE_ENDPOINT")

if __name__ == "__main__":
    pytest.main([__file__])
