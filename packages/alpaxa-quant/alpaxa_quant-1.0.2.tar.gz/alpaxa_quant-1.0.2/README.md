
# AlpaxaQuant

![Alt](https://repobeats.axiom.co/api/embed/dc5a7b6cda9f5c25931d25c94d4ccee56c2ff69c.svg "Repobeats analytics image")

[![PyPI version](https://img.shields.io/pypi/v/alpaxa-quant.svg?style=flat-square&color=0078D7)](https://pypi.org/project/alpaxa-quant/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square)](https://www.apache.org/licenses/LICENSE-2.0)
![Views](https://visitor-badge.laobi.icu/badge?page_id=JMasSolutions.AlpaxaQuant&color=0078D7)
[![Hits](https://hits.sh/github.com/JMasSolutions/AlpaxaQuant.svg?label=views&color=0078D7&style=flat)](https://hits.sh/github.com/JMasSolutions/AlpaxaQuant/)


**AlpaxaQuant** is a comprehensive quantitative finance and data acquisition library that unifies financial, macroeconomic, insider, and market-structure data from multiple APIs — including EODHD, FINRA, and FRED — into one modular Python package.

It is designed for quantitative analysts, researchers, and developers who want clean access to financial datasets for model training, signal generation, and econometric analysis.

---

## Table of Contents
- [AlpaxaQuant](#alpaxaquant)
  - [Table of Contents](#table-of-contents)
  - [Installation](#installation)
  - [Package Overview](#package-overview)
    - [utils](#utils)
    - [eodhd](#eodhd)
    - [insider\_trades](#insider_trades)
    - [finra](#finra)
    - [fred](#fred)
  - [Example Usage](#example-usage)
  - [License](#license)
  - [Contributing](#contributing)
  - [Connect](#connect)

---

## Installation

```bash
pip install alpaxa_quant
````

or install directly from source:

```bash
git clone https://github.com/Joanmascastella/AlpaxaQuant.git
cd AlpaxaQuant
pip install .
```

---

## Package Overview

### utils

Utility functions and request handlers used internally across the package.

* **`make_safe_request()`** — robust, retry-aware HTTP request wrapper with timeout and structured DataFrame return.
* **`request_util()`** — generic API request helper for GET/POST calls.
* **`make_yf_request()`** — lightweight Yahoo Finance helper for quick ticker data retrieval.

---

### eodhd

Wrapper around the EODHD API, offering market-wide coverage of financial and sentiment data for all global tickers.

**Key functions include:**

* `get_historical_ticker_price()` – OHLCV data retrieval for any ticker
* `get_financials()`, `get_balance_sheet()`, `get_cash_flow()` – full fundamental statements
* `get_earnings()` – historical and forward EPS data
* `get_technicals()` – moving averages, oscillators, and technical indicators
* `fetch_news_sentiment()` – sentiment analysis scores and metadata from recent news
* `get_analyst_ratings()` – aggregated analyst buy/hold/sell recommendations

---

### insider_trades

High-performance scraper and API interface for U.S. insider trading data.

* `get_insider_trades()` – retrieves Form 4 insider transactions for all U.S.-listed tickers.
* Supports filtering by:

  * Transaction type (Buy, Sell, Option Exercise)
  * Date range
  * Position (Officer, Director, Major Shareholder)
  * Minimum transaction value or share size

---

### finra

Comprehensive interface for FINRA’s fixed-income and equity market datasets — covering everything from short interest to block trading and debt market breadth.

**Highlights:**

* **Market Structure Data**

  * `get_blocks_summary()` – aggregated ATS trades
  * `get_otc_block_summary()` – OTC-block transaction data
  * `get_weekly_summary()` / `get_monthly_summary()` – market-wide summary data

* **Short Interest**

  * `get_consolidated_short_interest()` – historical short positions per ticker

* **Debt Markets**

  * `get_corporate_debt_market_sentiment()`
  * `get_agency_debt_market_breadth()`
  * `get_corporate_and_agency_capped_volume()`

* **Treasury & Fixed Income**

  * `get_treasury_daily_aggregates()`
  * `get_treasury_monthly_aggregates()`

---

### fred

Extensive collection of macroeconomic, monetary, and commodity data via the Federal Reserve (FRED) API.

Organized by category for clarity:

* Housing: `get_homeownership_rate()`, `get_median_house_sale_price()`, etc.
* Commodities: `get_daily_crude_oil_prices()`, `get_daily_gold_prices()`, `get_avg_beef_prices()`, etc.
* Inflation & Recession: `get_monthly_cpi()`, `get_financial_stress()`, `get_sahm_rule_recession_indicator()`
* Labour Market: `get_job_openings()`, `get_unemployed_rate()`, `get_labour_participation_rate()`
* Fiscal & Monetary Policy: `get_federal_surplus_deficit()`, `get_m1_supply()`, `get_m2_velocity()`
* Foreign Exchange: `get_daily_US_vs_EURO_rate()`, `get_JPY_vs_US()`, `get_yuan_vs_US()`
* Yields & Credit Spreads: `get_ICE_BofA_H_Y_effective_yield()`, `get_daily_moodys_seasoned_BAA_corp_yield()`
* Treasury Yields: `get_ten_yield_us()`, `get_twenty_yield_us()`, `get_thirty_yield_us()`
* GDP & Growth: `get_real_gdp_growth()`
* Volatility & Sentiment (VIX): `get_VIX()`, `get_equity_market_VIX_sentiment()`, `get_oil_VIX()`

---

## Example Usage

```python
import alpaxa_quant as aq
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv(".env")

# --- EODHD Example ---
base_endpoint = os.getenv('EXAMPLE_BASE_ENDPOINT')
api_key = os.getenv('EXAMPLE_API_KEY')

df_prices = aq.eodhd.get_historical_ticker_price(
    base_endpoint=base_endpoint,
    api_token=api_key,
    ticker='AAPL',
    fmt='json',
    period='d',
    order='a',
    from_date='2020-01-01',
    to_date='2025-01-01',
    verbose=False
)
print(df_prices.head())

# --- Insider Trades Example ---
config = {
    "scraping": {
        "start_year": 2024,
        "start_month": 6,
        "max_workers": 5,
        "retry_attempts": 3,
        "timeout": 30
    },
    "filters": {
        "min_transaction_value": 10000,
        "transaction_types": ["P", "S"],
        "exclude_companies": [],
        "include_companies": ["TSLA", "NVDA"],
        "min_shares_traded": 500
    },
    "cache": {
        "enabled": True,
        "directory": ".cache",
        "max_age": 12
    }
}
insiders = aq.insider_trades.get_insider_trades(config)
print(insiders.head())

# --- FINRA Example ---
finra_client_id = os.getenv('FINRA_CLIENT_ID')
finra_secret = os.getenv('FINRA_CLIENT_SECRET')

jwt, _ = aq.finra.get_bearer_token(client_id=finra_client_id, client_secret=finra_secret)
short_interest = aq.finra.get_consolidated_short_interest(jwt_token=jwt, ticker="TSLA")
print(short_interest.head())

# --- FRED Example ---
fred_endpoint = os.getenv('FRED_ENDPOINT')
fred_api = os.getenv('FRED_API_KEY')

cpi = aq.fred.get_monthly_cpi(api_key=fred_api, base_url=fred_endpoint, start_date='2020-01-01', end_date='2021-01-01', verbose=False)
print(cpi.tail())
```

---

## License

**Apache License 2.0**
© 2025 Joan Mas Castella

You may freely use, modify, and distribute AlpaxaQuant under the terms of the Apache 2.0 license.

---

## Contributing

Contributions are welcome.
If you’d like to add new endpoints, fix bugs, or improve documentation:

```bash
git clone https://github.com/Joanmascastella/AlpaxaQuant.git
git checkout -b feature/new-endpoint
```

Then submit a Pull Request describing your change.

---

## Connect

* **Author:** [Joan Mas Castella](https://github.com/JMasSolutions)
* **Organization:** [JMasSolutions](https://github.com/JMasSolutions)
* **Email:** [jmascastella@gmail.com](mailto:jmascastella@gmail.com)

---

> AlpaxaQuant — bridging financial data, macroeconomic insight, and quantitative modeling into one unified Python toolkit.

