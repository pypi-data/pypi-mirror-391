from dotenv import load_dotenv
import os

load_dotenv(".env")

def return_EODHD_test_api_key() -> str:
    """Returns EODHD test api key as a string."""
    return os.getenv("TEST_EODHD_API_KEY")

def return_EODHD_base_api_endpoint() -> str:
    """Returns EODHD test base api endpoint."""
    return os.getenv("TEST_EODHD_BASE_ENDPOINT")

def return_FRED_test_api_key() -> str:
    """Returns FRED test api key as a string."""
    return os.getenv("TEST_FRED_API_KEY")

def return_FRED_base_api_endpoint() -> str:
    """Returns FRED base api endpoint."""
    return os.getenv("TEST_FRED_BASE_ENDPOINT")

def return_FINRA_client_id() -> str:
    """Returns Finra client id."""
    return os.getenv("TEST_FINRA_CLIENT_ID")

def return_FINRA_client_secret() -> str:
    """Returns Finra client secret."""
    return os.getenv("TEST_FINRA_SECRET")