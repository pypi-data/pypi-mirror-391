from alpaxa_quant.utils import make_safe_request
from datetime import datetime, timedelta
from typing import Literal
import pandas as pd
import requests

def get_historical_ticker_price(
            base_endpoint: str,
            api_token: str,
            ticker: str,
            exchange_id: str = 'US',
            fmt: str = Literal['json', 'csv'],
            period: str = Literal['d', 'w', 'm'],
            order: str = Literal['a', 'd'],
            from_date: str = None,
            to_date: str = None,
            timeout: int = 10,
            verbose: bool = False
        ) -> pd.DataFrame | None:
        """
        Fetch historical EODHD price data for a given ticker symbol.

        Uses make_safe_request() internally for API calls.

        Args:
            base_endpoint: Base EODHD endpoint (e.g., https://eodhd.com/api/eod)
            api_token: EODHD API key
            ticker: Stock ticker symbol (e.g., 'AAPL')
            exchange_id: The id of the exchange of which the ticker is located (e.g., 'US)
            fmt: Response format (default: 'json')
            period: Data frequency ('d' daily, 'w' weekly, 'm' monthly)
            order: Sorting order ('a' ascending, 'd' descending)
            from_date: Start date (optional)
            to_date: End date (optional)
            timeout: Max request timeout (seconds)
            verbose: Print request configuration and logs if True

        Returns:
            A pandas DataFrame with historical price data or None on failure.
        """
    
        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "period": period,
            "order": order,
            "fmt": fmt,
        }

        # Add date params only if provided
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        
        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/eod/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Period: {period}
                    From: {from_date or 'Not Provided.'}
                    To: {to_date or 'Not Provided.'}

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_general_ticker_info(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None: 
        """
        Fetch comprehensive general company information for a given ticker symbol
        using the EODHD API.

        This endpoint returns metadata and profile-level information about the
        specified equity, including company identifiers, classification details,
        operational overview, address data, listings across exchanges, and key officers.

        ---
        Example Response Structure (EODHD "General" filter):

        {
            "Code": "AAL",
            "Type": "Common Stock",
            "Name": "American Airlines Group",
            "Exchange": "NASDAQ",
            "CurrencyCode": "USD",
            "CurrencyName": "US Dollar",
            "CurrencySymbol": "$",
            "CountryName": "USA",
            "CountryISO": "US",
            "OpenFigi": "BBG005P7Q881",
            "ISIN": "US02376R1023",
            "LEI": "IWUQB36BXD6OWD6X4T14",
            "PrimaryTicker": "AAL.US",
            "CUSIP": "001765106",
            "CIK": "0000006201",
            "EmployerIdNumber": "75-1825172",
            "FiscalYearEnd": "December",
            "IPODate": "2005-09-27",
            "InternationalDomestic": "International/Domestic",
            "Sector": "Industrials",
            "Industry": "Airlines",
            "GicSector": "Industrials",
            "GicGroup": "Transportation",
            "GicIndustry": "Passenger Airlines",
            "GicSubIndustry": "Passenger Airlines",
            "HomeCategory": "Domestic",
            "IsDelisted": false,
            "Description": "American Airlines Group Inc., through its subsidiaries, operates as a network air carrier...",
            "Address": "1 Skyview Drive, Fort Worth, TX, United States, 76155",
            "AddressData": {
                "Street": "1 Skyview Drive",
                "City": "Fort Worth",
                "State": "TX",
                "Country": "United States",
                "ZIP": "76155"
            },
            "Listings": {
                "0": {"Code": "A1G", "Exchange": "XETRA", "Name": "American Airlines Group Inc"},
                "1": {"Code": "A1G", "Exchange": "F", "Name": "American Airlines Group"},
                "2": {"Code": "AALL34", "Exchange": "SA", "Name": "American Airlines Group Inc"}
            },
            "Officers": {
                "0": {"Name": "Mr. Robert D. Isom Jr.", "Title": "CEO, President & Director", "YearBorn": "1964"},
                "1": {"Name": "Mr. Devon E. May", "Title": "Executive VP & CFO", "YearBorn": "1975"},
                ...
            },
            "Phone": "682 278 9000",
            "WebURL": "https://www.aa.com",
            "LogoURL": "/img/logos/US/aal.png",
            "FullTimeEmployees": 136900,
            "UpdatedAt": "2025-11-04"
        }

        ---
        Returned DataFrame Fields:
        - Identification: Code, ISIN, CIK, CUSIP, LEI, OpenFigi, PrimaryTicker
        - Classification: Sector, Industry, GICs hierarchy, HomeCategory, Type
        - Company Overview: Description, IPODate, FiscalYearEnd, InternationalDomestic
        - Financial Metadata: CurrencyCode, CurrencyName, Exchange, CountryName
        - Corporate Structure: Officers (nested), Listings (nested)
        - Contact Information: Address, Phone, WebURL
        - Operational Metadata: FullTimeEmployees, UpdatedAt, IsDelisted

        ---
        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            exchange_id (str): The exchange suffix (default: "US").
            fmt (str): Response format (default: "json").
            order (str): Sorting order ("a" ascending or "d" descending).
            timeout (int): Max timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints debug and request details.

        ---
        Returns:
            pd.DataFrame: A DataFrame containing the parsed general company information.
            Returns `None` if the request fails or no data is returned.
        """
        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": 'General'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_ticker_highlights(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch key financial highlights and valuation metrics for a given ticker symbol
        using the EODHD API with the 'Highlights' filter applied.

        This endpoint returns condensed fundamental indicators that describe a company's
        valuation, profitability, earnings estimates, and revenue performance. It is
        useful for quickly assessing market strength, growth trends, and relative
        financial stability.

        Example Response Structure (EODHD "Highlights" filter):

        {
            "MarketCapitalization": 8350093312,
            "MarketCapitalizationMln": 8350.0933,
            "EBITDA": 4613000192,
            "PERatio": 15.4268,
            "PEGRatio": 0.2246,
            "WallStreetTargetPrice": 15.0175,
            "BookValue": -6.002,
            "DividendShare": null,
            "DividendYield": null,
            "EarningsShare": 0.82,
            "EPSEstimateCurrentYear": 0.7402,
            "EPSEstimateNextYear": 1.8286,
            "EPSEstimateNextQuarter": 0.3206,
            "EPSEstimateCurrentQuarter": -0.2751,
            "MostRecentQuarter": "2025-09-30",
            "ProfitMargin": 0.0111,
            "OperatingMarginTTM": 0.0128,
            "ReturnOnAssetsTTM": 0.0236,
            "ReturnOnEquityTTM": 0,
            "RevenueTTM": 54293999616,
            "RevenuePerShareTTM": 82.354,
            "QuarterlyRevenueGrowthYOY": 0.003,
            "GrossProfitTTM": 12883000320,
            "DilutedEpsTTM": 0.82,
            "QuarterlyEarningsGrowthYOY": -0.1
        }

        Returned DataFrame Fields:
        - Valuation metrics: MarketCapitalization, PERatio, PEGRatio, BookValue
        - Profitability: EBITDA, ProfitMargin, OperatingMarginTTM
        - Earnings and estimates: EarningsShare, DilutedEpsTTM, EPSEstimateCurrentYear,
            EPSEstimateNextYear, EPSEstimateCurrentQuarter, EPSEstimateNextQuarter
        - Growth and revenue: RevenueTTM, RevenuePerShareTTM, QuarterlyRevenueGrowthYOY,
            QuarterlyEarningsGrowthYOY, GrossProfitTTM
        - Other indicators: WallStreetTargetPrice, ReturnOnAssetsTTM, ReturnOnEquityTTM

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            exchange_id (str): Exchange suffix (default: "US").
            fmt (str): Response format (default: "json").
            order (str): Sorting order ("a" ascending or "d" descending).
            timeout (int): Max timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing the parsed fundamental highlights for the ticker.
            Returns None if the request fails or no data is available.
        """
        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": 'Highlights'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_ticker_valuation(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch valuation ratios and enterprise value metrics for a given ticker symbol
        using the EODHD API with the 'Valuation' filter applied.

        This endpoint provides key indicators used to assess a company's market value
        relative to its earnings, revenue, and book value. It is typically used in
        fundamental analysis to determine whether a stock is overvalued or undervalued
        compared to its financial performance.

        Example Response Structure (EODHD "Valuation" filter):

        {
            "TrailingPE": 15.4268,
            "ForwardPE": 6.2112,
            "PriceSalesTTM": 0.1538,
            "PriceBookMRQ": 0,
            "EnterpriseValue": 36169843424,
            "EnterpriseValueRevenue": 0.6667,
            "EnterpriseValueEbitda": 14.2457
        }

        Returned DataFrame Fields:
        - Price-to-earnings ratios: TrailingPE, ForwardPE
        - Price-based valuation: PriceSalesTTM, PriceBookMRQ
        - Enterprise value metrics: EnterpriseValue, EnterpriseValueRevenue, EnterpriseValueEbitda

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            exchange_id (str): Exchange suffix (default: "US").
            fmt (str): Response format (default: "json").
            order (str): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing valuation and enterprise value ratios.
            Returns None if the request fails or no data is available.
        """
        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": 'Valuation'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_shares_stats(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch share statistics for a given ticker symbol using the EODHD API with the
        'SharesStats' filter applied.

        This endpoint provides information on a company's share structure, including
        the number of outstanding and floating shares, insider and institutional
        ownership percentages, and short interest data when available. It is useful for
        evaluating liquidity, investor composition, and potential volatility based on
        short positioning.

        Example Response Structure (EODHD "SharesStats" filter):

        {
            "SharesOutstanding": 660086495,
            "SharesFloat": 650482236,
            "PercentInsiders": 1.5190000000000001,
            "PercentInstitutions": 65.39,
            "SharesShort": null,
            "SharesShortPriorMonth": null,
            "ShortRatio": null,
            "ShortPercentOutstanding": null,
            "ShortPercentFloat": 0.1077
        }

        Returned DataFrame Fields:
        - Share volume: SharesOutstanding, SharesFloat
        - Ownership distribution: PercentInsiders, PercentInstitutions
        - Short interest data: SharesShort, SharesShortPriorMonth,
            ShortRatio, ShortPercentOutstanding, ShortPercentFloat

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            exchange_id (str): Exchange suffix (default: "US").
            fmt (str): Response format (default: "json").
            order (str): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing share statistics and ownership data.
            Returns None if the request fails or no data is available.
        """
        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": 'SharesStats'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_technicals(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch technical and trading statistics for a given ticker symbol using the
        EODHD API with the 'Technicals' filter applied.

        This endpoint provides recent trading-related metrics including beta, moving
        averages, 52-week price range, and short interest data. It is used to analyze
        a stock’s volatility, trend direction, and overall technical strength relative
        to the market.

        Example Response Structure (EODHD "Technicals" filter):

        {
            "Beta": 1.269,
            "52WeekHigh": 19.1,
            "52WeekLow": 8.5,
            "50DayMA": 12.4338,
            "200DayMA": 12.3631,
            "SharesShort": 70591644,
            "SharesShortPriorMonth": 78784800,
            "ShortRatio": 0.85,
            "ShortPercent": 0.1077
        }

        Returned DataFrame Fields:
        - Volatility and beta: Beta
        - Price range: 52WeekHigh, 52WeekLow
        - Moving averages: 50DayMA, 200DayMA
        - Short interest: SharesShort, SharesShortPriorMonth, ShortRatio, ShortPercent

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            exchange_id (str): Exchange suffix (default: "US").
            fmt (str): Response format (default: "json").
            order (str): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing technical and short interest statistics.
            Returns None if the request fails or no data is available.
        """
        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": 'Technicals'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_split_dividends(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch dividend and split history information for a given ticker symbol using the
        EODHD API with the 'SplitsDividends' filter applied.

        This endpoint provides details about a company's historical and forward dividend
        data, payout ratios, and stock split history. It includes information on dividend
        dates, ex-dividend dates, forward yields, and the number of dividends issued per
        year. This data is typically used for income analysis, dividend tracking, and
        understanding corporate actions affecting shareholders.

        Example Response Structure (EODHD "SplitsDividends" filter):

        {
            "ForwardAnnualDividendRate": 0,
            "ForwardAnnualDividendYield": 0,
            "PayoutRatio": 0,
            "DividendDate": "2020-02-19",
            "ExDividendDate": "2020-02-04",
            "LastSplitFactor": "0:1",
            "LastSplitDate": "2013-12-09",
            "NumberDividendsByYear": {
                "0": {"Year": 2014, "Count": 2},
                "1": {"Year": 2015, "Count": 4},
                "2": {"Year": 2016, "Count": 4},
                "3": {"Year": 2017, "Count": 4},
                "4": {"Year": 2018, "Count": 4},
                "5": {"Year": 2019, "Count": 4},
                "6": {"Year": 2020, "Count": 1}
            }
        }

        Returned DataFrame Fields:
        - Dividend metrics: ForwardAnnualDividendRate, ForwardAnnualDividendYield, PayoutRatio
        - Key dates: DividendDate, ExDividendDate
        - Split information: LastSplitFactor, LastSplitDate
        - Dividend frequency: NumberDividendsByYear (yearly breakdown of dividend count)

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            exchange_id (str): Exchange suffix (default: "US").
            fmt (str): Response format (default: "json").
            order (str): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing dividend, payout, and split history data.
            Returns None if the request fails or no data is available.
        """

        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": 'SplitsDividends'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_analyst_ratings(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch analyst consensus ratings and target price data for a given ticker symbol
        using the EODHD API with the 'AnalystRatings' filter applied.

        This endpoint provides aggregated analyst sentiment, including the number of
        buy, hold, and sell recommendations, along with an overall rating score and
        average target price. It is used to gauge market sentiment and analyst outlook
        for a specific company or security.

        Example Response Structure (EODHD "AnalystRatings" filter):

        {
            "Rating": 3.9167,
            "TargetPrice": 15.0175,
            "StrongBuy": 10,
            "Buy": 3,
            "Hold": 10,
            "Sell": 1,
            "StrongSell": 0
        }

        Returned DataFrame Fields:
        - Aggregate analyst sentiment: Rating, TargetPrice
        - Recommendation counts: StrongBuy, Buy, Hold, Sell, StrongSell

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            exchange_id (str): Exchange suffix (default: "US").
            fmt (str): Response format (default: "json").
            order (str): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing analyst rating and recommendation data.
            Returns None if the request fails or no data is available.
        """


        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": 'AnalystRatings'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_holders(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        holder_type: Literal['institutions', 'funds'] = 'institutions',
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch institutional or fund holder data for a given ticker symbol using the
        EODHD API with the 'Holders' filter applied.

        This endpoint retrieves detailed ownership information for the selected holder
        type ('Institutions' or 'Funds'), showing major shareholders, their share
        holdings, changes over time, and ownership percentages. It is typically used to
        analyze institutional ownership concentration, fund exposure, and investor
        trends for a company.

        Example Response Structure (EODHD "Holders" filter):

        {
            "Institutions": {
                "0": {
                    "name": "Vanguard Group Inc",
                    "date": "2025-06-30",
                    "totalShares": 9.4298,
                    "totalAssets": 0.0113,
                    "currentShares": 62220777,
                    "change": -1404507,
                    "change_p": -2.2075
                },
                "1": {
                    "name": "BlackRock Inc",
                    "date": "2025-06-30",
                    "totalShares": 8.7564,
                    "totalAssets": 0.0123,
                    "currentShares": 57777150,
                    "change": -191392,
                    "change_p": -0.3302
                },
                ...
            },
            "Funds": {
                "0": {
                    "name": "Vanguard PRIMECAP Inv",
                    "date": "2025-06-30",
                    "totalShares": 3.6733,
                    "totalAssets": 0.3628,
                    "currentShares": 24237513,
                    "change": -4689200,
                    "change_p": -16.2106
                },
                "1": {
                    "name": "iShares Core S&P Mid-Cap ETF",
                    "date": "2025-08-31",
                    "totalShares": 3.2535,
                    "totalAssets": 0.287,
                    "currentShares": 21467218,
                    "change": 0,
                    "change_p": 0
                },
                ...
            }
        }

        Returned DataFrame Fields:
        - Holder identification: name, date
        - Ownership metrics: totalShares (percentage), currentShares (absolute number)
        - Asset exposure: totalAssets (percentage of fund/institution assets)
        - Position change: change (absolute shares), change_p (percentage change)

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            holder_type (Literal['Institutions', 'Funds']): Type of holder data to retrieve.
            exchange_id (str): Exchange suffix (default: "US").
            fmt (Literal['json', 'csv']): Response format (default: "json").
            order (Literal['a', 'd']): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing ownership information for the selected
            holder type (Institutions or Funds). Returns None if the request fails or
            no data is available.
        """
        holder_type = holder_type.capitalize()
        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": f'Holders::{holder_type}'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_insider_transactions(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch insider trading transactions for a given ticker symbol using the EODHD API
        with the 'InsiderTransactions' filter applied.

        This endpoint returns recent insider trading activity, including the names of
        executives, officers, and key shareholders, along with their transaction types,
        dates, prices, and SEC filing links when available. It is useful for analyzing
        insider sentiment, identifying buying or selling trends, and monitoring changes
        in insider ownership.

        Example Response Structure (EODHD "InsiderTransactions" filter):

        {
            "0": {
                "date": "2025-06-17",
                "ownerCik": null,
                "ownerName": "Tim Moore",
                "transactionDate": "2025-06-17",
                "transactionCode": "S",
                "transactionAmount": null,
                "transactionPrice": 10.56,
                "transactionAcquiredDisposed": "D",
                "postTransactionAmount": null,
                "secLink": null
            },
            "1": {
                "date": "2025-06-16",
                "ownerCik": null,
                "ownerName": "Tim Moore",
                "transactionDate": "2025-06-16",
                "transactionCode": "P",
                "transactionAmount": null,
                "transactionPrice": 10.9,
                "transactionAcquiredDisposed": "A",
                "postTransactionAmount": null,
                "secLink": null
            },
            ...
            "14": {
                "date": "2024-12-27",
                "ownerCik": null,
                "ownerName": "Robert D Isom Jr",
                "transactionDate": "2024-12-27",
                "transactionCode": "S",
                "transactionAmount": 102441,
                "transactionPrice": 17.21,
                "transactionAcquiredDisposed": "D",
                "postTransactionAmount": null,
                "secLink": "http://www.sec.gov/Archives/edgar/data/6201/000166427224000431/xslF345X05/f4_a1eus000003he7omas-live.xml"
            }
        }

        Returned DataFrame Fields:
        - Insider identification: ownerName, ownerCik
        - Transaction details: transactionDate, transactionCode, transactionPrice, transactionAmount
        - Transaction type: transactionAcquiredDisposed ('A' for acquired, 'D' for disposed)
        - Ownership impact: postTransactionAmount
        - SEC filing link: secLink (if available)

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            exchange_id (str): Exchange suffix (default: "US").
            fmt (Literal['json', 'csv']): Response format (default: "json").
            order (Literal['a', 'd']): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing insider transaction records for the given ticker.
            Returns None if the request fails or no data is available.
        """

        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": f'InsiderTransactions'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_outstanding_shares(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        period: Literal['annual', 'quarterly'] = 'quarterly',
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch outstanding share count data for a given ticker symbol using the EODHD API
        with the 'outstandingShares' filter applied.

        This endpoint provides information on the company’s total shares outstanding,
        either on an annual or quarterly basis. It can be used to analyze dilution trends,
        changes in equity structure, and share count fluctuations over time.

        Example Response Structure (EODHD "outstandingShares" filter):

        {
            "0": {
                "date": "2025",
                "dateFormatted": "2025-12-31",
                "sharesMln": "660.3580",
                "shares": 660358000
            },
            "1": {
                "date": "2024",
                "dateFormatted": "2024-12-31",
                "sharesMln": "721.3000",
                "shares": 721300000
            }
        }

        Returned DataFrame Fields:
        - Period reference: date (fiscal year or quarter), dateFormatted (formatted date)
        - Share data: sharesMln (shares in millions), shares (exact count)

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            period (Literal['Annual', 'Quarterly']): Reporting period for outstanding shares.
            exchange_id (str): Exchange suffix (default: "US").
            fmt (Literal['json', 'csv']): Response format (default: "json").
            order (Literal['a', 'd']): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing outstanding share data for the specified
            reporting period (annual or quarterly). Returns None if the request fails or
            no data is available.
        """

        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": f'outstandingShares::{period.lower()}'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_earnings(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        period: Literal['history', 'trend', 'annual'] = 'annual',
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch earnings data for a given ticker symbol using the EODHD API with the
        'Earnings' filter applied.

        This endpoint provides earnings-related information in three formats depending
        on the selected period: 'history', 'trend', or 'annual'. It allows retrieval of
        historical earnings surprises, analyst estimates and forecast trends, or annual
        EPS performance data. This information is essential for analyzing company
        profitability, estimate accuracy, and growth expectations.

        Example Response Structures (EODHD "Earnings" filter):

        1. History
        {
            "2025-12-31": {
                "reportDate": "2026-01-22",
                "date": "2025-12-31",
                "beforeAfterMarket": "BeforeMarket",
                "currency": null,
                "epsActual": 0,
                "epsEstimate": 0.58,
                "epsDifference": -0.58,
                "surprisePercent": -100
            }
        }

        2. Trend
        {
            "2026-12-31": {
                "date": "2026-12-31",
                "period": "+1y",
                "growth": "1.4705",
                "earningsEstimateAvg": "1.8286",
                "earningsEstimateLow": "1.3800",
                "earningsEstimateHigh": "2.2500",
                "earningsEstimateYearAgoEps": "0.7402",
                "earningsEstimateNumberOfAnalysts": "20.0000",
                "earningsEstimateGrowth": "1.4705",
                "revenueEstimateAvg": "58250369610.00",
                "revenueEstimateLow": "56597000000.00",
                "revenueEstimateHigh": "59769200000.00",
                "revenueEstimateYearAgoEps": null,
                "revenueEstimateNumberOfAnalysts": "19.00",
                "revenueEstimateGrowth": "0.0616",
                "epsTrendCurrent": "1.8286",
                "epsTrend7daysAgo": "1.7421",
                "epsTrend30daysAgo": "1.6441",
                "epsTrend60daysAgo": "1.6690",
                "epsTrend90daysAgo": "1.6333",
                "epsRevisionsUpLast7days": "8.0000",
                "epsRevisionsUpLast30days": "10.0000",
                "epsRevisionsDownLast7days": null,
                "epsRevisionsDownLast30days": "6.0000"
            }
        }

        3. Annual
        {
            "2025-09-30": {
                "date": "2025-09-30",
                "epsActual": 0.15
            },
            "2024-12-31": {
                "date": "2024-12-31",
                "epsActual": 1.28
            }
        }

        Returned DataFrame Fields:
        - History:
            reportDate, date, beforeAfterMarket, currency,
            epsActual, epsEstimate, epsDifference, surprisePercent
        - Trend:
            earningsEstimateAvg, earningsEstimateLow, earningsEstimateHigh,
            earningsEstimateGrowth, earningsEstimateNumberOfAnalysts,
            revenueEstimateAvg, revenueEstimateGrowth,
            epsTrendCurrent, epsTrend7daysAgo, epsRevisionsUpLast30days, etc.
        - Annual:
            date, epsActual

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            period (Literal['history', 'trend', 'annual']): Type of earnings data to fetch.
            exchange_id (str): Exchange suffix (default: "US").
            fmt (Literal['json', 'csv']): Response format (default: "json").
            order (Literal['a', 'd']): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing the requested earnings data (history, trend, or annual).
            Returns None if the request fails or no data is available.
        """
        period = period.capitalize()
        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": f'Earnings::{period}'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def get_financials(
        base_endpoint: str,
        api_token: str,
        ticker: str,
        period: Literal['quarterly', 'yearly'],
        financial_type: Literal['Balance_Sheet', 'Income_Statement', 'Cash_Flow'],
        exchange_id: str = 'US',
        fmt: str = Literal['json', 'csv'],
        order: str = Literal['a', 'd'],
        timeout: int = 10,
        verbose: bool = True) -> pd.DataFrame | None:
        """
        Fetch company financial statements for a given ticker symbol using the EODHD API
        with the 'Financials' filter applied.

        This endpoint retrieves detailed financial statement data — balance sheet,
        income statement, or cash flow — for the selected reporting period (quarterly
        or yearly). It is commonly used for fundamental financial analysis, valuation
        models, and company performance tracking over time.

        Example Filter Usage:
        Financials::Balance_Sheet::Quarterly
        Financials::Income_Statement::Yearly
        Financials::Cash_Flow::Quarterly

        Returned DataFrame Content:
        - Balance_Sheet: Assets, Liabilities, Shareholders’ Equity, Cash, Debt,
            Inventory, Accounts Receivable, and Total Equity.
        - Income_Statement: Revenue, Operating Income, Net Income, EPS, Cost of Goods
            Sold (COGS), Operating Expenses, and EBITDA.
        - Cash_Flow: Net Cash from Operating, Investing, and Financing activities,
            Free Cash Flow, and Net Change in Cash.

        Args:
            base_endpoint (str): Base EODHD endpoint (e.g. "https://eodhd.com/api/fundamentals")
            api_token (str): EODHD API key.
            ticker (str): The company ticker symbol (e.g. "AAPL", "TSLA").
            period (Literal['quarterly', 'yearly']): Reporting period for the financial data.
            financial_type (Literal['Balance_Sheet', 'Income_Statement', 'Cash_Flow']):
                The type of financial statement to retrieve.
            exchange_id (str): Exchange suffix (default: "US").
            fmt (Literal['json', 'csv']): Response format (default: "json").
            order (Literal['a', 'd']): Sorting order ("a" ascending or "d" descending).
            timeout (int): Maximum timeout duration for the request in seconds (default: 10).
            verbose (bool): If True, prints request and response details.

        Returns:
            pd.DataFrame: A DataFrame containing the requested financial statement
            (Balance Sheet, Income Statement, or Cash Flow) for the specified period.
            Returns None if the request fails or no data is available.
        """
        # Construct query paramteres 
        params = {
            "api_token": api_token,
            "order": order,
            "fmt": fmt,
            "filter": f'Financials::{financial_type}::{period.lower()}'
        }

        # Set up endpoint 
        constructed_endpoint=f"{base_endpoint}/fundamentals/{ticker.upper()}.{exchange_id}"

        # Verbose print statement
        if verbose:
            print(f"""
                    Processing ticker: {ticker}

                    Request configuration:
                    Filter Applied: General

                    Return configuration:
                    Order: {order}
                    Format: {fmt}
                    URL: {constructed_endpoint}
                """)
        
        # Make request
        df = make_safe_request(endpoint=constructed_endpoint, timeout=timeout, params=params, verbose=verbose)

        # Check if df is not empty
        if df is None or df.empty:
            print(f"No data returned for {ticker}")
            return None

        return df

def fetch_news_sentiment(
    base_endpoint: str,
    api_token: str,
    ticker: str,
    start_date: str = "2000-01-01",
    end_date: datetime = None,
    chunk: str = Literal['year', 'month', 'quarter'],
    verbose: bool = True
) -> pd.DataFrame:
    """
    Fetches all news for a given ticker from EODHD API in date chunks.
    Automatically iterates from start_date to today.

    Args:
        base_endpoint (str): Base API endpoint (e.g. 'https://eodhd.com/api').
        api_token (str): EODHD API key.
        ticker (str): Stock ticker (e.g. 'MSFT.US').
        start_date (str): Starting date (YYYY-MM-DD).
        end_date (datetime): End date (defaults to today).
        chunk (str): Chunk type ('year', 'month', 'quarter').
        verbose (bool): Print progress.

    Returns:
        pd.DataFrame: Combined news articles across all chunks.
    """
    base_url = f"{base_endpoint}/news"
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    if end_date is None:
        end_dt = datetime.today()
    elif isinstance(end_date, str):
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    else:
        end_dt = end_date

    # define chunk step
    if chunk == "year":
        step = timedelta(days=365)
    elif chunk == "quarter":
        step = timedelta(days=90)
    elif chunk == "month":
        step = timedelta(days=30)
    else:
        raise ValueError("Invalid chunk type. Use 'year', 'quarter', or 'month'.")

    all_data = []

    current = start_dt
    while current < end_dt:
        next_chunk = min(current + step, end_dt)
        params = {
            "s": ticker,
            "from": current.strftime("%Y-%m-%d"),
            "to": next_chunk.strftime("%Y-%m-%d"),
            "api_token": api_token,
            "fmt": "json"
        }

        if verbose:
            print(f"Fetching {params['from']} → {params['to']}")

        try:
            response = requests.get(base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            for item in data:
                if isinstance(item, dict):
                    sentiment = item.get("sentiment", {})
                    filtered_item = {
                        "date": item.get("date"),
                        "symbols": ",".join(item.get("symbols", [])),
                        "tags": ",".join(item.get("tags", [])),
                        "polarity": sentiment.get("polarity"),
                        "neg": sentiment.get("neg"),
                        "neu": sentiment.get("neu"),
                        "pos": sentiment.get("pos"),
                    }
                    all_data.append(filtered_item)

        except Exception as e:
            print(f"Error fetching {params['from']} → {params['to']}: {e}")

        current = next_chunk + timedelta(days=1)

    if not all_data:
        print("No data retrieved.")
        return pd.DataFrame()

    df = pd.DataFrame(all_data)
    df.drop_duplicates(subset=["date", "symbols", "tags"], inplace=True)
    df.sort_values(by="date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df


