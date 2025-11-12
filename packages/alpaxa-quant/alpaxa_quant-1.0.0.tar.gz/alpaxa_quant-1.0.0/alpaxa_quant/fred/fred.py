from alpaxa_quant.config import return_FRED_base_api_endpoint, return_FRED_test_api_key
from alpaxa_quant.utils import request_util, make_yf_request
import pandas as pd 

# ----------------
# COMMODITIES
# ----------------
def get_daily_gold_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="GC=F"
    interval='1d'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_monthly_gold_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="GC=F"
    interval='1mo'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_daily_silver_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="SI=F"
    interval='1d'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_monthly_silver_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="SI=F"
    interval='1mo'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_daily_copper_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="HG=F"
    interval='1d'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_monthly_copper_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="HG=F"
    interval='1mo'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_daily_aluminum_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="ALI=F"
    interval='1d'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_monthly_aluminum_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="ALI=F"
    interval='1mo'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_daily_platinum_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="PL=F"
    interval='1d'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_monthly_platinum_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="PL=F"
    interval='1mo'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_daily_pallaidium_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="PA=F"
    interval='1d'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_monthly_palladium_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="PA=F"
    interval='1mo'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_daily_corn_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="ZC=F"
    interval='1d'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_monthly_corn_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="ZC=F"
    interval='1mo'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_daily_soybean_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="ZS=F"
    interval='1d'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_monthly_soybean_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="ZS=F"
    interval='1mo'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_daily_wheat_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="KE=F"
    interval='1d'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df

def get_monthly_wheat_prices(start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame():
    ticker="KE=F"
    interval='1mo'
    timeout=30

    df = make_yf_request(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval, timeout=timeout, verbose=verbose)

    return df
# ----------------

# ----------------
# HOUSING
# ----------------
def get_nonfarm_business_sector_hours_worked(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "HOANBS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "q",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df


def get_homeownership_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "RSAHORUSQ156S",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "q",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_new_private_housing_permits(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "PERMIT",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_fifteen_year_fixed_morgage_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "MORTGAGE15US",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_total_units_new_private_homes(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "HOUST",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_median_house_sale_price(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "MSPUS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "q",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_thirty_year_mortgage_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "MORTGAGE30US",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

# ----------------

# ----------------
# COMMODITIES
# ----------------
def get_egg_avg_prices(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "APU0000708111",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_avg_beef_prices(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "APU0000703112",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_avg_electricity_prices(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "APU000072610",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_avg_dairy_prices(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "APU0000709112",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_crude_oil_prices(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "DCOILWTICO",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_crude_oil_prices(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "MCOILWTICO",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_weekly_crude_oil_prices(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "WCOILWTICO",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_crude_oil_prices(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "MCOILWTICO",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df


# ----------------

# ----------------
# VOLATILITY
# ----------------
def get_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "VIXCLS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_gold_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "GVZCLS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_oil_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "OVXCLS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_equity_market_VIX_sentiment(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMVMACROBUS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_NASDAQ_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "VXNCLS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_RUSSELL_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "RVXCLS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_DJIA_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "VXDCLS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_emerging_markets_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "VXEEMCLS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_interest_rate_VIX_sentiment(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMVMACROINTEREST",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_inflation_VIX_sentiment(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMVMACROINFLATION",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_political_governance_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMVELECTGOVRN",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_consumer_sentiment_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMVMACROCONSUME",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_trade_policy_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMVTRADEPOLEMV",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monetary_policy_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMVMONETARYPOL",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_fiscal_policy_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMVFISCALPOL",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_real_estate_VIX(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMVMACRORE",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df
# ----------------

# ----------------
# INFLATION/RECESSION
# ----------------
def get_core_CPI(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "CPILFESL",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_real_gdp_growth(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "GDPC1",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "q",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_sahm_rule_recession_indicator(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "SAHMCURRENT",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_NBER_rule_recession_indicator(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    """
    Provides day ranges when recessions occured.
    """
    # Construct params
    params = {
        "series_id":       "USRECD",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_inflation_expectation(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "MICH",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_fed_financial_conditions(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "NFCI",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_economic_policy_uncertainty(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "USEPUINDXD",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_economic_policy_uncertainty(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "USEPUINDXM",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_financial_stress(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "STLFSI4",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_consumer_loans(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "H8B1247NCBCMG",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_delinquincy_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DRSFRMACBS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "q",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_five_yearly_forward_inflation_expectation_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "T5YIFRM",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_five_yearly_forward_inflation_expectation_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "T5YIFR",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_smoothed_US_recession_probabilities(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "RECPROUSM156N",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_consumer_sentiment(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "UMCSENT",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_delinquincy_rate_credit_card_loans(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DRCCLACBS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "q",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_real_time_sahm_recession_indicator(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "SAHMREALTIME",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_producer_price_index(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "PPIACO",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_personal_savings_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "PSAVERT",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_cpi(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "CPIAUCNS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_semiannual_cpi(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "CUUS0000SA0",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "sa",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

# ----------------

# ----------------
# Labour Market
# ----------------
def get_unemployement_population_ratio(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "EMRATIO",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_young_unemployment_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "LNS14000024",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_total_unemployed(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "U6RATE",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_job_openings(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "JTSJOL",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_labour_participation_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "CIVPART",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_initial_claims(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "ICSA",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_unemployed_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "UNRATE",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df
# ----------------

# ----------------
# FEDERAL
# ----------------
def get_federal_surplus_deficit(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "FYFSD",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "a",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_total_assets(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "WALCL",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_reverse_repurchase_agreements(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "RRPONTSYD",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_all_federal_employees(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "CES9091000001",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_federal_expenditures_interest_payements(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "A091RC1Q027SBEA",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "q",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_liabilities_capital(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "WTREGEN",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df


def get_federal_liabilities_capital(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "WRBWFRBL",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_federal_liabilities_capital_weekly_average(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "WRESBAL",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_quarterly_federal_debt(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "GFDEGDQ188S",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "q",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_annual_federal_funds_effective(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "RIFSPFFNA",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "a",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_weekly_federal_funds_effective(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "FF",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_federal_funds_effective(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "DFF",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_federal_funds_effective(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
# Construct params
    params = {
        "series_id":       "FEDFUNDS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df
# ----------------

# ----------------
# MONETARY
# ----------------
def get_JPY_vs_US(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DEXJPUS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_yuan_vs_US(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DEXCHUS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_pounds_vs_US(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DEXUSUK",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_francs_vs_US(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DEXSZUS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_m1_supply(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "M1SL",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_m2_supply(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "M2SL",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_m2_velocity(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "M2V",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "q",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monetary_base(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "BOGMBASE",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_nominal_broad_US_dollar(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DTWEXBGS",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_nominal_broad_US_dollar(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "TWEXBGSMTH",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_annual_US_vs_EURO_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "AEXUSEU",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "a",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_US_vs_EURO_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "EXUSEU",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_US_vs_EURO_rate(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DEXUSEU",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df
# ----------------

# ----------------
# YIELDS
# ----------------
def get_ICE_BofA_H_Y_option_adjusted_spread(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "BAMLH0A0HYM2",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_ICE_BofA_H_Y_effective_yield(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "BAMLH0A0HYM2EY",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_ICE_BofA_CCC_L_H_Y_option_adjusted_spread(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "BAMLH0A3HYC",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_moodys_seasoned_BAA_corp_yield(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "BAA",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_moodys_seasoned_BAA_corp_yield(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DBAA",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_weekly_moodys_seasoned_BAA_corp_yield(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "WBAA",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_ICE_BofA_corp(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "BAMLC0A0CM",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_ICE_BofA_BBB_corp(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "BAMLC0A4CBBB",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df
# ----------------

# ----------------
# TREASURY YIELDS
# ----------------
# Get US30Y Treasury Yields 
def get_thirty_yield_us(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    # Construct params
    params = {
        "series_id":       "DGS30",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

# Get US20Y Treasury Yields 
def get_twenty_yield_us(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "DGS20",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

# Get US10Y Treasury Yields 
def get_ten_yield_us(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "DGS10",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

# Get US05Y Treasury Yields 
def get_five_yield_us(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "DGS5",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

# Get US02Y Treasury Yields 
def get_two_yield_us(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "DGS2",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df
    
def get_daily_ten_year_treasury_constant_maturity(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "T10Y2Y",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_ten_year_treasury_constant_maturity(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "T10Y2Y",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_daily_market_yield_US_treasury_ten_year_constant(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "DGS10",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_weekly_market_yield_US_treasury_ten_year_constant(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "WGS10YR",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "w",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_monthly_market_yield_US_treasury_ten_year_constant(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "GS10",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "m",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df

def get_ten_year_constant_maturity_minus_three_month_treasury_constant(api_key: str, base_url: str, start_date: str, end_date: str, verbose: bool = False) -> pd.DataFrame:
    params = {
        "series_id":       "T10Y3M",
        "api_key":         api_key,
        "file_type":       "json",
        "observation_start": start_date,
        "observation_end":   end_date,
        "frequency":       "d",
    }
    df = request_util(params=params, base_url=base_url, verbose=verbose)
    return df
# -------------------

if __name__ == "__main__":
    K= return_FRED_test_api_key()
    u= return_FRED_base_api_endpoint()
    get_annual_federal_funds_effective(api_key=K, base_url=u, start_date="2020-01-01", end_date="2021-01-01", verbose=True)