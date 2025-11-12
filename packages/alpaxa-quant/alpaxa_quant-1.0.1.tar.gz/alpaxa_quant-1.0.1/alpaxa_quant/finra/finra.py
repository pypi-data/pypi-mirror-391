from alpaxa_quant.utils import make_safe_request
from typing import Any, Dict, Optional
from ast import Tuple
import pandas as pd
import requests
import base64

def get_bearer_token(client_id: str, client_secret: str) -> Tuple:
    """
    Obtain FINRA FIP bearer access token using client credentials.
    """
    token_bytes = f"{client_id}:{client_secret}".encode("utf-8")
    b64_token = base64.b64encode(token_bytes).decode("utf-8")

    url = "https://ews.fip.finra.org/fip/rest/ews/oauth2/access_token?grant_type=client_credentials"

    headers = {
        "Authorization": f"Basic {b64_token}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    # POST request
    response = requests.post(url, headers=headers)

    # Raise if something went wrong
    response.raise_for_status()

    # Parse JSON
    data = response.json()

    jwt_token = data['access_token']
    expires_in = data['expires_in']

    return jwt_token, expires_in

def get_blocks_summary(    
    jwt_token: str,
    fields: Optional[Dict[str, Any]] = None,
    limit: int = 100,
    verbose: bool = False
    ) -> pd.DataFrame():
    """
    Aggregated ATS trade data in NMS stocks that meets certain share based and dollar based thresholds.

    For more information on fields that can be filtered by, visit the following website
    [FINRA OTC Market Metadata](https://api.finra.org/metadata/group/otcMarket/name/blocksSummary).

    Args:
        jws_token (str): Jwt token retrieved by get_bearer_token function.
        fields (Dict): A comma delimmeted list of fields to filter by
        limit (int): A int value of the amount of records to be retrieved from a given request.
        verbose (bool): Print progress.

    Returns:
        pd.DataFrame: Aggregated ATS trade data in NMS stocks
    """

    if verbose:
        print("Retreving Block Summary...\n")

    if limit > 1000:
        raise ValueError("Limit value has to be less than 1000")

    url = "https://api.finra.org/data/group/otcMarket/name/blocksSummary"

    params = {
        "limit": limit,
    }
    if fields:
        params["fields"] = ",".join(fields)

    if verbose:
        print(f"Params:\n Limit: {limit}\nFields:{fields}")

    response = make_safe_request(endpoint=url, timeout=30, params=params, auth=True, jwt_key=jwt_token, verbose=verbose)

    df = pd.DataFrame(response)

    return df


def get_consolidated_short_interest(
    jwt_token: str,
    ticker: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL Consolidated Short Interest data for a specific ticker symbol
    using FINRA's pagination system (limit + offset), via make_safe_request.

    Args:
        jwt_token (str): Bearer token retrieved by get_bearer_token.
        ticker (str): The ticker symbol to filter for (e.g. 'TSLA').
        limit (int): The maximum number of records per request (<=1000).
        verbose (bool): Print debug and progress logs.

    Returns:
        pd.DataFrame: Combined DataFrame of all available consolidated short interest records.
    """

    if verbose:
        print(f"Retrieving Consolidated Short Interest for {ticker}...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/otcMarket/name/consolidatedShortInterest"
    offset = 0
    all_batches = []

    while True:
        body = {
            "limit": limit,
            "offset": offset,
            "compareFilters": [
                {
                    "compareType": "equal",
                    "fieldName": "symbolCode",
                    "fieldValue": ticker.upper()
                }
            ],
            "fields": [
                "stockSplitFlag",
                "previousShortPositionQuantity",
                "averageDailyVolumeQuantity",
                "issueName",
                "currentShortPositionQuantity",
                "changePreviousNumber",
                "accountingYearMonthNumber",
                "settlementDate",
                "marketClassCode",
                "symbolCode",
                "daysToCoverQuantity",
                "issuerServicesGroupExchangeCode",
                "revisionFlag",
                "changePercent"
            ]
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit} for {ticker}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=None,
            json=body,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found, stopping pagination.")
            break

        all_batches.append(df)
        if len(df) < limit:
            if verbose:
                print(f"Last batch retrieved ({len(df)} rows).")
            break

        offset += limit 

    if not all_batches:
        if verbose:
            print(f"No data returned for ticker {ticker}.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved for {ticker}: {len(final_df)}")

    return final_df

def get_monthly_summary(
    jwt_token: str,
    ticker: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
        Retrieve ALL monthly summary data for a specific ticker symbol
        using FINRA's pagination system (limit + offset), via make_safe_request.

        Args:
            jwt_token (str): Bearer token retrieved by get_bearer_token.
            ticker (str): The ticker symbol to filter for (e.g. 'TSLA').
            limit (int): The maximum number of records per request (<=1000).
            verbose (bool): Print debug and progress logs.

        Returns:
            pd.DataFrame: Combined DataFrame of all available monthly summary records.
    """

    if verbose:
        print(f"Retrieving montly summary for {ticker}...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/otcMarket/name/monthlySummary"
    offset = 0
    all_batches = []

    while True:
        body = {
            "limit": limit,
            "offset": offset,
            "compareFilters": [
                {
                    "compareType": "equal",
                    "fieldName": "issueSymbolIdentifier",
                    "fieldValue": ticker.upper()
                }
            ],
            "fields": [
                "issueSymbolIdentifier",
                "issueName",
                "lastUpdateDate",
                "lastReportedDate",
                "initialPublishedDate",
                "tierIdentifier",
                "summaryStartDate",
                "monthStartDate",
                "totalMonthlyTradeCount",
                "firmCRDNumber",
                "productTypeCode",
                "marketParticipantName",
                "totalMonthlyShareQuantity",
                "summaryTypeCode"
            ]
        }
        

        if verbose:
            print(f"Fetching offset={offset}, limit={limit} for {ticker}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=None,
            json=body,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found, stopping pagination.")
            break

        all_batches.append(df)
        if len(df) < limit:
            if verbose:
                print(f"Last batch retrieved ({len(df)} rows).")
            break

        offset += limit 

    if not all_batches:
        if verbose:
            print(f"No data returned for ticker {ticker}.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved for {ticker}: {len(final_df)}")

    return final_df

def get_otc_block_summary(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
        Aggregated OTC (Non-ATS) trade data in NMS stocks that meets certain share based and dollar based thresholds.

        Args:
            jwt_token (str): Bearer token retrieved by get_bearer_token.
            limit (int): The maximum number of records per request (<=1000).
            verbose (bool): Print debug and progress logs.

        Returns:
            pd.DataFrame: Combined DataFrame of all available OTC block summary data...
    """

    if verbose:
        print(f"Retrieving OTC block summary data...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/otcMarket/name/otcBlocksSummary"
    offset = 0
    all_batches = []

    while True:
        body = {
            "limit": limit,
            "offset": offset,
            "fields":[
                "OTCBlockBusinessSharePercent",
                "OTCBlockBusinessShareRank",
                "OTCBlockBusinessTradePercent",
                "OTCBlockBusinessTradeRank",
                "OTCBlockCount",
                "OTCBlockQuantity",
                "OTCBlockSharePercent",
                "OTCBlockShareRank",
                "OTCBlockTradePercent",
                "OTCBlockTradeRank",
                "OTCSharePercent",
                "OTCShareRank",
                "OTCTradePercent",
                "OTCTradeRank",
                "atsOtc",
                "averageBlockSize",
                "averageBlockSizeRank",
                "averageTradeSize",
                "averageTradeSizeRank",
                "crdFirmName",
                "initialPublishedDate",
                "lastReportedDate",
                "lastUpdateDate",
                "monthStartDate",
                "summaryStartDate",
                "summaryTypeCode",
                "summaryTypeDescription",
                "totalShareQuantity",
                "totalTradeCount"
            ]
        }
        

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=None,
            json=body,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found, stopping pagination.")
            break

        all_batches.append(df)
        if len(df) < limit:
            if verbose:
                print(f"Last batch retrieved ({len(df)} rows).")
            break

        offset += limit 

    if not all_batches:
        if verbose:
            print(f"No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df


def get_daily_short_volume_sale(
    jwt_token: str,
    ticker: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
        Retrieve ALL daily agreggated short volume sale data for a specific ticker symbol
        using FINRA's pagination system (limit + offset), via make_safe_request.

        Args:
            jwt_token (str): Bearer token retrieved by get_bearer_token.
            ticker (str): The ticker symbol to filter for (e.g. 'TSLA').
            limit (int): The maximum number of records per request (<=1000).
            verbose (bool): Print debug and progress logs.

        Returns:
            pd.DataFrame: Combined DataFrame of all available agreggated short volume data records.
    """

    if verbose:
        print(f"Retrieving daily short volume sale data for {ticker}...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/otcMarket/name/regShoDaily"
    offset = 0
    all_batches = []

    while True:
        body = {
            "limit": limit,
            "offset": offset,
            "compareFilters": [
                {
                    "compareType": "equal",
                    "fieldName": "securitiesInformationProcessorSymbolIdentifier",
                    "fieldValue": ticker.upper()
                }
            ],
            "fields": [
                "tradeReportDate",
                "securitiesInformationProcessorSymbolIdentifier",
                "shortParQuantity",
                "shortExemptParQuantity",
                "totalParQuantity",
                "marketCode",
                "reportingFacilityCode"
            ]
        }
        

        if verbose:
            print(f"Fetching offset={offset}, limit={limit} for {ticker}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=None,
            json=body,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found, stopping pagination.")
            break

        all_batches.append(df)
        if len(df) < limit:
            if verbose:
                print(f"Last batch retrieved ({len(df)} rows).")
            break

        offset += limit 

    if not all_batches:
        if verbose:
            print(f"No data returned for ticker {ticker}.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved for {ticker}: {len(final_df)}")

    return final_df

def get_weekly_summary(
    jwt_token: str,
    ticker: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve FINRA OTC Market Weekly Summary (rolling 12 months)
    for a specific ticker (issueSymbolIdentifier).

    Args:
        jwt_token (str): FINRA bearer token.
        ticker (str): Symbol (e.g., 'AAPL').
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: Weekly OTC/ATS aggregate trade data.
    """

    if verbose:
        print(f"Retrieving Weekly Summary for {ticker} (12-month rolling window)...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/otcMarket/name/weeklySummary"
    offset = 0
    all_batches = []

    # Build compare filters
    filters = [
        {
            "compareType": "equal",
            "fieldName": "issueSymbolIdentifier",
            "fieldValue": ticker.upper()
        }
    ]

    fields = [
        "totalWeeklyShareQuantity",
        "issueSymbolIdentifier",
        "issueName",
        "lastUpdateDate",
        "lastReportedDate",
        "tierDescription",
        "initialPublishedDate",
        "tierIdentifier",
        "summaryStartDate",
        "totalWeeklyTradeCount",
        "weekStartDate",
        "MPID",
        "firmCRDNumber",
        "productTypeCode",
        "marketParticipantName",
        "summaryTypeCode"
    ]

    while True:
        body = {
            "limit": limit,
            "offset": offset,
            "fields": fields,
            "compareFilters": filters
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=None,
            json=body,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved for {ticker}: {len(final_df)}")

    return final_df


def get_agency_debt_market_breadth(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL available agency debt market breadth.

    Args:
        jwt_token (str): FINRA bearer token.
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: All available agency debt market breadth.
    """

    if verbose:
        print(f"Retrieving agency debt market debth ...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/fixedIncomeMarket/name/agencyMarketBreadth"
    offset = 0
    all_batches = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=params,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df

def get_agency_debt_market_sentiment(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL available agency debt market sentiment.

    Args:
        jwt_token (str): FINRA bearer token.
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: All available agency debt market sentiment.
    """

    if verbose:
        print(f"Retrieving agency debt market sentiment ...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/fixedIncomeMarket/name/agencyMarketSentiment"
    offset = 0
    all_batches = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=params,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df

def get_corporate_debt_market_breadth(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL available corporate debt market breadth.

    Args:
        jwt_token (str): FINRA bearer token.
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: All available corporate debt market breadth.
    """

    if verbose:
        print(f"Retrieving corporate debt market breadth ...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/fixedIncomeMarket/name/corporate144AMarketBreadth"
    offset = 0
    all_batches = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=params,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df

def get_corporate_debt_market_sentiment(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL available corporate debt market sentiment.

    Args:
        jwt_token (str): FINRA bearer token.
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: All available corporate debt market sentiment.
    """

    if verbose:
        print(f"Retrieving corporate debt market sentiment ...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/fixedIncomeMarket/name/corporate144AMarketSentiment"
    offset = 0
    all_batches = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=params,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df


def get_corporate_and_agency_capped_volume(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL available corporate and agency capped volume.

    Args:
        jwt_token (str): FINRA bearer token.
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: All available corporate and agency capped volume.
    """

    if verbose:
        print(f"Retrieving corporate and agency capped volume ...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/fixedIncomeMarket/name/corporatesAndAgenciesCappedVolume"
    offset = 0
    all_batches = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=params,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df

def get_corporate_debt_market_sentiment(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL available corporate debt market sentiment.

    Args:
        jwt_token (str): FINRA bearer token.
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: All available corporate debt market sentiment.
    """

    if verbose:
        print(f"Retrieving corporate debt market sentiment ...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/fixedIncomeMarket/name/corporateMarketSentiment"
    offset = 0
    all_batches = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=params,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df

def get_securitized_product_capped_volume(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL available securitized product capped volume.

    Args:
        jwt_token (str): FINRA bearer token.
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: All available securitized product capped volume.
    """

    if verbose:
        print(f"Retrieving securitized product capped volume ...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/fixedIncomeMarket/name/securitizedProductsCappedVolume"
    offset = 0
    all_batches = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=params,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df

def get_treasury_daily_aggregates(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL available treasury daily aggregates.

    Args:
        jwt_token (str): FINRA bearer token.
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: All available treasury daily aggregates.
    """

    if verbose:
        print(f"Retrieving treasury daily aggregates ...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/fixedIncomeMarket/name/treasuryDailyAggregates"
    offset = 0
    all_batches = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=params,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df

def get_treasury_monthly_aggregates(
    jwt_token: str,
    limit: int = 1000,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Retrieve ALL available treasury monthly aggregates.

    Args:
        jwt_token (str): FINRA bearer token.
        limit (int): Max records per request.
        verbose (bool): Print debug output.

    Returns:
        pd.DataFrame: All available treasury monthly aggregates.
    """

    if verbose:
        print(f"Retrieving treasury monthly aggregates ...\n")

    if limit > 1000:
        raise ValueError("Limit must be <= 1000 (FINRA API constraint).")

    url = "https://api.finra.org/data/group/fixedIncomeMarket/name/treasuryMonthlyAggregates"
    offset = 0
    all_batches = []

    while True:
        params = {
            "limit": limit,
            "offset": offset,
        }

        if verbose:
            print(f"Fetching offset={offset}, limit={limit}")

        df = make_safe_request(
            endpoint=url,
            timeout=30,
            params=params,
            auth=True,
            jwt_key=jwt_token,
            verbose=verbose
        )

        if df is None or df.empty:
            if verbose:
                print("No more records found.")
            break

        all_batches.append(df)
        if len(df) < limit:
            break

        offset += limit

    if not all_batches:
        if verbose:
            print("No data returned.")
        return pd.DataFrame()

    final_df = pd.concat(all_batches, ignore_index=True)

    if verbose:
        print(f"Total records retrieved: {len(final_df)}")

    return final_df