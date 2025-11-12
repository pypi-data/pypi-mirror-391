import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from retry import retry
from pathlib import Path
import json
from typing import Dict, List, Set
from dataclasses import dataclass
import re

@dataclass
class ScraperConfig:
    start_year: int
    start_month: int
    max_workers: int
    retry_attempts: int
    timeout: int
    min_transaction_value: float
    transaction_types: List[str]
    exclude_companies: List[str]
    include_companies: List[str]
    min_shares_traded: int
    cache_enabled: bool
    cache_dir: str
    cache_max_age: int

class OpenInsiderScraper:
    def __init__(self, config_path: Dict):
        self.config = self._load_config(config_path)
        self._setup_directories()
        
    def _load_config(self, config: Dict) -> ScraperConfig:
        return ScraperConfig(
            start_year=config['scraping']['start_year'],
            start_month=config['scraping']['start_month'],
            max_workers=config['scraping']['max_workers'],
            retry_attempts=config['scraping']['retry_attempts'],
            timeout=config['scraping']['timeout'],
            min_transaction_value=config['filters']['min_transaction_value'],
            transaction_types=config['filters']['transaction_types'],
            exclude_companies=config['filters']['exclude_companies'],
            include_companies=config['filters']['include_companies'],
            min_shares_traded=config['filters']['min_shares_traded'],
            cache_enabled=config['cache']['enabled'],
            cache_dir=config['cache']['directory'],
            cache_max_age=config['cache']['max_age']
        )
    
    def _setup_directories(self) -> None:
        if self.config.cache_enabled:
            Path(self.config.cache_dir).mkdir(parents=True, exist_ok=True)
    
    @retry(tries=3, delay=2, backoff=2)
    def _fetch_data(self, url: str) -> requests.Response:
        return requests.get(url, timeout=self.config.timeout)
    
    def _get_cache_path(self, year: int, month: int) -> Path:
        return Path(self.config.cache_dir) / f"data_{year}_{month}.json"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        if not cache_path.exists():
            return False
        cache_age = datetime.now().timestamp() - cache_path.stat().st_mtime
        return cache_age < self.config.cache_max_age * 3600
    
    def _get_data_for_month(self, year: int, month: int) -> Set[tuple]:
        cache_path = self._get_cache_path(year, month)

        if self.config.cache_enabled and self._is_cache_valid(cache_path):
            with open(cache_path, 'r') as f:
                return set(tuple(x) for x in json.load(f))

        start_date = datetime(year, month, 1).strftime('%m/%d/%Y')
        end_date = (datetime(year, month, 1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        end_date = end_date.strftime('%m/%d/%Y')

        url = f'http://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=-1&fdr={start_date}+-+{end_date}&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=5000&page=1'

        try:
            response = self._fetch_data(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'tinytable'})
            if not table:
                print(f"No table found for {month}-{year}")
                return set()

            rows = table.find('tbody').find_all('tr')
            data = set()

            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 13: 
                    continue

                try:
                    filing_date = cols[1].get_text(strip=True)  
                    trade_date = cols[2].get_text(strip=True)
                    ticker = cols[3].get_text(strip=True)
                    company_name = cols[4].get_text(strip=True)
                    insider_name = cols[5].get_text(strip=True)
                    title = cols[6].get_text(strip=True)
                    transaction_type = cols[7].get_text(strip=True)
                    last_price = cols[8].get_text(strip=True)
                    qty = cols[9].get_text(strip=True)
                    shares_held = cols[10].get_text(strip=True)
                    owned = cols[11].get_text(strip=True)
                    value = cols[12].get_text(strip=True)

                    # Clean transaction type ("S - Sale" → "S")
                    transaction_type = re.sub(r"\s*-\s*.*", "", transaction_type).strip()

                    insider_data = (
                        filing_date,
                        trade_date,
                        ticker,
                        company_name,
                        insider_name,
                        title,
                        transaction_type,
                        last_price,
                        qty,
                        shares_held,
                        owned,
                        value
                    )

                    # Apply filters
                    if self._apply_filters({
                        "ticker": ticker,
                        "transaction_type": transaction_type,
                        "Value": value,
                        "Qty": qty
                    }):
                        data.add(insider_data)

                except Exception as e:
                    print(f"Error parsing row: {str(e)}")
                    continue


            # Save cache if enabled
            if self.config.cache_enabled:
                with open(cache_path, 'w') as f:
                    json.dump([list(x) for x in data], f)

            return data

        except Exception as e:
            print(f"Error fetching data for {month}-{year}: {str(e)}")
            return set()


    
    def _clean_numeric(self, value: str) -> float:
        """Clean numeric values from strings, handling currency, percentages, and text."""
        if not value or value.lower() in ['n/a', 'new']:
            return 0.0
        # Remove currency symbols and commas
        clean = value.replace('$', '').replace(',', '')
        # Handle percentages by removing % and converting to decimal
        if '%' in clean:
            clean = clean.replace('+', '').replace('%', '')
            return 0.0  # We don't need the actual percentage value
        try:
            return float(clean)
        except ValueError:
            return 0.0  # Return 0 for any non-numeric values

    def _apply_filters(self, data: Dict[str, str]) -> bool:
        try:
            # Check transaction type filter
            if self.config.transaction_types and data['transaction_type'] not in self.config.transaction_types:
                return False
                
            # Check excluded companies
            if data['ticker'] in self.config.exclude_companies:
                return False

            # Check included companies
            if self.config.include_companies and data['ticker'] not in self.config.include_companies:
                return False

            # Convert and check value
            value = self._clean_numeric(data['Value'])
            if value < self.config.min_transaction_value:
                return False
                
            # Convert and check quantity
            shares = self._clean_numeric(data['Qty'])
            if shares < self.config.min_shares_traded:
                return False
            
            return True
        except (ValueError, KeyError) as e:
            print(f"Error filtering data: {str(e)}")
            return False
    
    def scrape(self) -> None:
        print("Starting scraping process...")
        
        all_data = []
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = []
            total_months = sum(
                12 if year != current_year else current_month
                for year in range(self.config.start_year, current_year + 1)
            )
            
            for year in range(self.config.start_year, current_year + 1):
                start_month = 1 if year != self.config.start_year else self.config.start_month
                end_month = current_month if year == current_year else 12
                
                for month in range(start_month, end_month + 1):
                    futures.append(executor.submit(self._get_data_for_month, year, month))
            
            with tqdm(total=len(futures), desc="Processing months") as pbar:
                for future in as_completed(futures):
                    try:
                        data = future.result()
                        all_data.extend(data)
                        pbar.update(1)
                    except Exception as e:
                        print(f"Error processing month: {str(e)}")
        
        print(f"Scraping completed. Found {len(all_data)} transactions.")
        return self._save_data(all_data)
    
    def _save_data(self, data: List[tuple]) -> pd.DataFrame:

        field_names = [
            "filing_date", "trade_date", "ticker", "company_name",
            "owner_name", "Title", "transaction_type", "last_price",
            "Qty", "shares_held", "Owned", "Value"
        ]

        df = pd.DataFrame(data, columns=field_names)

        if "company_name" in df.columns:
            df = df.drop(columns=["company_name"])

        for col in ["owner_name", "Title"]:
            df[col] = (
                df[col]
                .astype(str)
                .replace({"": None, "nan": None, "None": None})
                .str.strip()
            )

        df["transaction_type"] = (
            df["transaction_type"]
            .astype(str)
            .str.strip()
            .str.replace(r"\s*-\s*.*", "", regex=True)
            .str.replace(r"[^A-Z]", "", regex=True)
            .replace("", None)
        )

        numeric_cols = ["last_price", "Qty", "shares_held", "Owned", "Value"]

        for col in numeric_cols:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("%", "", regex=False)
                    .str.replace(r"[^\d\.\-\+]", "", regex=True)
                    .replace("", None)
                )
                df[col] = pd.to_numeric(df[col], errors="coerce")

        for date_col in ["filing_date", "trade_date"]:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors="coerce").dt.date

        df = df.dropna(subset=["ticker", "transaction_type"], how="any")

        df = df.sort_values(by=["ticker", "filing_date"], ascending=[True, False]).reset_index(drop=True)

        total = len(df)
        tickers = df["ticker"].nunique()
        print(f"Cleaned {total} transactions from {tickers} unique tickers.")
        print(df.head(5))

        return df

def get_insider_trades(config: Dict) -> pd.DataFrame:
    """
    OpenInsider Data Scraper (Extended)

    A robust and parallelized insider trading data scraper built for integration within
    the AlpaxaQuant ecosystem, inspired by and adapted from the original 
    openinsiderData project (https://github.com/sd3v/openinsiderData).

    This function retrieves insider trading records directly from openinsider.com,
    supporting intelligent caching, multi-threaded scraping, and user-defined filters.
    It returns a pandas DataFrame containing all transactions that meet your criteria.

    -------------------------------------------------------------------------------
    Configuration Schema
    -------------------------------------------------------------------------------
    The scraper behavior is fully configurable through a nested dictionary
    matching the following structure:

    config = {
        "scraping": {
            "start_year": 2000,      # Starting year for data collection
            "start_month": 1,        # Starting month within start_year
            "max_workers": 10,       # Number of concurrent threads
            "retry_attempts": 3,     # Number of automatic retry attempts
            "timeout": 30            # Timeout in seconds for each HTTP request
        },
        "filters": {
            "min_transaction_value": 0,       # Minimum transaction value in USD
            "transaction_types": [],          # Empty = all, or specify e.g. ["P", "S", "A"]
            "exclude_companies": [],          # List of tickers to exclude
            "include_companies": [],          # List of tickers to include
            "min_shares_traded": 0            # Minimum number of traded shares
        },
        "cache": {
            "enabled": False,                 # Enable/disable caching
            "directory": ".cache",            # Directory for cache files
            "max_age": 24                     # Max cache age in hours
        }
    }

    ------------------------------------------------------------
    Code    Description
    ------------------------------------------------------------
    P       Purchase,
    S       Sale,
    F       Tax,
    D       Disposition,
    G       Gift,
    X       Exercise,
    M       Options Exercise,
    C       Conversion,
    W       Will / Inheritance,
    H       Holdings,
    O       Other

    -------------------------------------------------------------------------------
    Key Features
    -------------------------------------------------------------------------------
    - Multi-threaded Collection:
      Fetches data across multiple months and years in parallel using Python's 
      ThreadPoolExecutor for optimal speed.

    - Smart Caching System:
      Optionally stores and reuses previously fetched results to minimize server load 
      and reduce redundant network requests.

    - Customizable Filters:
      Supports filtering transactions by:
        * Minimum trade value (min_transaction_value)
        * Trade type (purchase, sale, award, etc.)
        * Specific tickers to include or exclude
        * Minimum number of shares traded

    - Resilient Networking:
      Built-in retry logic via the retry decorator automatically retries failed 
      HTTP requests with exponential backoff.

    - Real-Time Progress Tracking:
      Displays a progress bar with tqdm to monitor month-by-month scraping.

    - Flexible Output Integration:
      Returns a pandas DataFrame ready for downstream processing or saving to
      CSV or Parquet within your pipeline.

    -------------------------------------------------------------------------------
    Data Structure
    -------------------------------------------------------------------------------
    Each returned record includes the following fields:

    filing_date        - Date the transaction was filed with SEC
    trade_date         - Date the trade occurred
    ticker             - Stock ticker symbol
    owner_name         - Name of the insider
    Title              - Insider's role or title
    transaction_type   - Type of transaction (P, S, A, etc.)
    last_price         - Last price of the traded stock
    Qty                - Quantity of shares traded
    shares_held        - Number of shares held after transaction
    Owned              - Ownership percentage (if available)
    Value              - Total value of the transaction in USD

    -------------------------------------------------------------------------------
    Return Value
    -------------------------------------------------------------------------------
    pandas.DataFrame

    A pandas DataFrame containing all transactions matching the configured filters.

    -------------------------------------------------------------------------------
    Notes
    -------------------------------------------------------------------------------
    - The tool respects the source website's structure but may need updates if the
      HTML layout of openinsider.com changes.
    - Use responsibly in accordance with the website's terms of service.
    - Large time ranges can result in long execution times or large memory usage.

    -------------------------------------------------------------------------------
    Example Usage
    -------------------------------------------------------------------------------

    from alpaxa_quant.insider_trades import get_insider_trades

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

    df = get_insider_trades(config)
    print(df.head())

    -------------------------------------------------------------------------------
    Citation
    -------------------------------------------------------------------------------
    This module was inspired by and extends functionality from the openinsiderData
    project (https://github.com/sd3v/openinsiderData), modernized for structured 
    configuration, improved modularity, and integration into the AlpaxaQuant package.
    """
    try:
        scraper = OpenInsiderScraper(config)
        df = scraper.scrape()
        return df
    except Exception as e:
        print(f"The following error occured: {str(e)}")
        raise

