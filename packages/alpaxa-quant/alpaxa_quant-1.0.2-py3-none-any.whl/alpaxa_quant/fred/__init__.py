from .fred import (
    # ----------------
    # HOUSING
    # ----------------
    get_fifteen_year_fixed_morgage_rate,
    get_homeownership_rate,
    get_median_house_sale_price,
    get_new_private_housing_permits,
    get_thirty_year_mortgage_rate,
    get_total_units_new_private_homes,

    # ----------------
    # COMMODITIES
    # ----------------
    get_avg_beef_prices,
    get_avg_dairy_prices,
    get_avg_electricity_prices,
    get_egg_avg_prices,
    get_daily_crude_oil_prices,
    get_monthly_crude_oil_prices,
    get_weekly_crude_oil_prices,
    get_daily_aluminum_prices,
    get_daily_copper_prices,
    get_daily_corn_prices,
    get_daily_gold_prices,
    get_daily_pallaidium_prices,
    get_daily_platinum_prices,
    get_daily_silver_prices,
    get_daily_soybean_prices,
    get_daily_wheat_prices,
    get_monthly_aluminum_prices,
    get_monthly_copper_prices,
    get_monthly_corn_prices,
    get_monthly_gold_prices,
    get_monthly_palladium_prices,
    get_monthly_platinum_prices,
    get_monthly_silver_prices,
    get_monthly_soybean_prices,
    get_monthly_wheat_prices,
    
    # ----------------
    # INFLATION / RECESSION
    # ----------------
    get_consumer_loans,
    get_consumer_sentiment,
    get_daily_economic_policy_uncertainty,
    get_daily_five_yearly_forward_inflation_expectation_rate,
    get_delinquincy_rate,
    get_delinquincy_rate_credit_card_loans,
    get_fed_financial_conditions,
    get_financial_stress,
    get_inflation_expectation,
    get_monthly_cpi,
    get_monthly_economic_policy_uncertainty,
    get_monthly_five_yearly_forward_inflation_expectation_rate,
    get_NBER_rule_recession_indicator,
    get_personal_savings_rate,
    get_producer_price_index,
    get_real_time_sahm_recession_indicator,
    get_sahm_rule_recession_indicator,
    get_semiannual_cpi,
    get_smoothed_US_recession_probabilities,

    # ----------------
    # LABOUR MARKET
    # ----------------
    get_initial_claims,
    get_job_openings,
    get_labour_participation_rate,
    get_total_unemployed,
    get_unemployed_rate,
    get_unemployement_population_ratio,
    get_young_unemployment_rate,
    get_nonfarm_business_sector_hours_worked,

    # ----------------
    # FEDERAL / FISCAL
    # ----------------
    get_all_federal_employees,
    get_federal_expenditures_interest_payements,
    get_federal_liabilities_capital,
    get_federal_liabilities_capital_weekly_average,
    get_federal_surplus_deficit,
    get_liabilities_capital,
    get_quarterly_federal_debt,
    get_reverse_repurchase_agreements,
    get_total_assets,

    # ----------------
    # MONETARY POLICY & MONEY SUPPLY
    # ----------------
    get_annual_federal_funds_effective,
    get_daily_federal_funds_effective,
    get_monthly_federal_funds_effective,
    get_weekly_federal_funds_effective,
    get_m1_supply,
    get_m2_supply,
    get_m2_velocity,
    get_monetary_base,

    # ----------------
    # FOREIGN EXCHANGE
    # ----------------
    get_annual_US_vs_EURO_rate,
    get_daily_US_vs_EURO_rate,
    get_daily_nominal_broad_US_dollar,
    get_francs_vs_US,
    get_JPY_vs_US,
    get_monthly_nominal_broad_US_dollar,
    get_monthly_US_vs_EURO_rate,
    get_pounds_vs_US,
    get_yuan_vs_US,

    # ----------------
    # YIELDS & CREDIT SPREADS
    # ----------------
    get_ICE_BofA_CCC_L_H_Y_option_adjusted_spread,
    get_ICE_BofA_H_Y_effective_yield,
    get_ICE_BofA_H_Y_option_adjusted_spread,
    get_daily_ICE_BofA_BBB_corp,
    get_daily_ICE_BofA_corp,
    get_daily_moodys_seasoned_BAA_corp_yield,
    get_monthly_moodys_seasoned_BAA_corp_yield,
    get_weekly_moodys_seasoned_BAA_corp_yield,

    # ----------------
    # TREASURY YIELDS
    # ----------------
    get_daily_market_yield_US_treasury_ten_year_constant,
    get_daily_ten_year_treasury_constant_maturity,
    get_five_yield_us,
    get_ten_yield_us,
    get_thirty_yield_us,
    get_twenty_yield_us,
    get_two_yield_us,
    get_monthly_market_yield_US_treasury_ten_year_constant,
    get_monthly_ten_year_treasury_constant_maturity,
    get_ten_year_constant_maturity_minus_three_month_treasury_constant,
    get_weekly_market_yield_US_treasury_ten_year_constant,

    # ----------------
    # GDP & MACRO GROWTH
    # ----------------
    get_real_gdp_growth,

    # ----------------
    # CORE INFLATION
    # ----------------
    get_core_CPI,

    # ----------------
    # VOLATILITY / SENTIMENT (VIX-DERIVED)
    # ----------------
    get_consumer_sentiment_VIX,
    get_DJIA_VIX,
    get_emerging_markets_VIX,
    get_equity_market_VIX_sentiment,
    get_fiscal_policy_VIX,
    get_gold_VIX,
    get_inflation_VIX_sentiment,
    get_interest_rate_VIX_sentiment,
    get_monetary_policy_VIX,
    get_NASDAQ_VIX,
    get_oil_VIX,
    get_political_governance_VIX,
    get_real_estate_VIX,
    get_RUSSELL_VIX,
    get_trade_policy_VIX,
    get_VIX,
)


__all__ = [
    # ----------------
    # HOUSING
    # ----------------
    'get_fifteen_year_fixed_morgage_rate',
    'get_homeownership_rate',
    'get_median_house_sale_price',
    'get_new_private_housing_permits',
    'get_thirty_year_mortgage_rate',
    'get_total_units_new_private_homes',

    # ----------------
    # COMMODITIES
    # ----------------
    'get_avg_beef_prices',
    'get_avg_dairy_prices',
    'get_avg_electricity_prices',
    'get_egg_avg_prices',
    'get_daily_aluminum_prices',
    'get_daily_copper_prices',
    'get_daily_corn_prices',
    'get_daily_crude_oil_prices',
    'get_daily_gold_prices',
    'get_daily_pallaidium_prices',
    'get_daily_platinum_prices',
    'get_daily_silver_prices',
    'get_daily_soybean_prices',
    'get_daily_wheat_prices',
    'get_monthly_aluminum_prices',
    'get_monthly_copper_prices',
    'get_monthly_corn_prices',
    'get_monthly_crude_oil_prices',
    'get_monthly_gold_prices',
    'get_monthly_palladium_prices',
    'get_monthly_platinum_prices',
    'get_monthly_silver_prices',
    'get_monthly_soybean_prices',
    'get_monthly_wheat_prices',
    'get_weekly_crude_oil_prices',

    # ----------------
    # INFLATION / RECESSION
    # ----------------
    'get_consumer_loans',
    'get_consumer_sentiment',
    'get_daily_economic_policy_uncertainty',
    'get_daily_five_yearly_forward_inflation_expectation_rate',
    'get_delinquincy_rate',
    'get_delinquincy_rate_credit_card_loans',
    'get_fed_financial_conditions',
    'get_financial_stress',
    'get_inflation_expectation',
    'get_monthly_cpi',
    'get_monthly_economic_policy_uncertainty',
    'get_monthly_five_yearly_forward_inflation_expectation_rate',
    'get_NBER_rule_recession_indicator',
    'get_personal_savings_rate',
    'get_producer_price_index',
    'get_real_time_sahm_recession_indicator',
    'get_sahm_rule_recession_indicator',
    'get_semiannual_cpi',
    'get_smoothed_US_recession_probabilities',

    # ----------------
    # LABOUR MARKET
    # ----------------
    'get_initial_claims',
    'get_job_openings',
    'get_labour_participation_rate',
    'get_total_unemployed',
    'get_unemployed_rate',
    'get_unemployement_population_ratio',
    'get_young_unemployment_rate',
    'get_nonfarm_business_sector_hours_worked',

    # ----------------
    # FEDERAL / FISCAL
    # ----------------
    'get_all_federal_employees',
    'get_federal_expenditures_interest_payements',
    'get_federal_liabilities_capital',
    'get_federal_liabilities_capital_weekly_average',
    'get_federal_surplus_deficit',
    'get_liabilities_capital',
    'get_quarterly_federal_debt',
    'get_reverse_repurchase_agreements',
    'get_total_assets',

    # ----------------
    # MONETARY POLICY & MONEY SUPPLY
    # ----------------
    'get_annual_federal_funds_effective',
    'get_daily_federal_funds_effective',
    'get_monthly_federal_funds_effective',
    'get_weekly_federal_funds_effective',
    'get_m1_supply',
    'get_m2_supply',
    'get_m2_velocity',
    'get_monetary_base',

    # ----------------
    # FOREIGN EXCHANGE
    # ----------------
    'get_annual_US_vs_EURO_rate',
    'get_daily_US_vs_EURO_rate',
    'get_daily_nominal_broad_US_dollar',
    'get_francs_vs_US',
    'get_JPY_vs_US',
    'get_monthly_nominal_broad_US_dollar',
    'get_monthly_US_vs_EURO_rate',
    'get_pounds_vs_US',
    'get_yuan_vs_US',

    # ----------------
    # YIELDS & CREDIT SPREADS
    # ----------------
    'get_ICE_BofA_CCC_L_H_Y_option_adjusted_spread',
    'get_ICE_BofA_H_Y_effective_yield',
    'get_ICE_BofA_H_Y_option_adjusted_spread',
    'get_daily_ICE_BofA_BBB_corp',
    'get_daily_ICE_BofA_corp',
    'get_daily_moodys_seasoned_BAA_corp_yield',
    'get_monthly_moodys_seasoned_BAA_corp_yield',
    'get_weekly_moodys_seasoned_BAA_corp_yield',

    # ----------------
    # TREASURY YIELDS
    # ----------------
    'get_daily_market_yield_US_treasury_ten_year_constant',
    'get_daily_ten_year_treasury_constant_maturity',
    'get_five_yield_us',
    'get_ten_yield_us',
    'get_thirty_yield_us',
    'get_twenty_yield_us',
    'get_two_yield_us',
    'get_monthly_market_yield_US_treasury_ten_year_constant',
    'get_monthly_ten_year_treasury_constant_maturity',
    'get_ten_year_constant_maturity_minus_three_month_treasury_constant',
    'get_weekly_market_yield_US_treasury_ten_year_constant',

    # ----------------
    # GDP & MACRO GROWTH
    # ----------------
    'get_real_gdp_growth',

    # ----------------
    # CORE INFLATION
    # ----------------
    'get_core_CPI',

    # ----------------
    # VOLATILITY / SENTIMENT (VIX-DERIVED)
    # ----------------
    'get_consumer_sentiment_VIX',
    'get_DJIA_VIX',
    'get_emerging_markets_VIX',
    'get_equity_market_VIX_sentiment',
    'get_fiscal_policy_VIX',
    'get_gold_VIX',
    'get_inflation_VIX_sentiment',
    'get_interest_rate_VIX_sentiment',
    'get_monetary_policy_VIX',
    'get_NASDAQ_VIX',
    'get_oil_VIX',
    'get_political_governance_VIX',
    'get_real_estate_VIX',
    'get_RUSSELL_VIX',
    'get_trade_policy_VIX',
    'get_VIX',
]

__version__ = "1.0"

def describe_fred():
    description = """
    AlpaxaQuant — FRED Module Overview
    ===================================

    Provides unified access to thousands of macroeconomic and financial time-series
    indicators from the Federal Reserve Economic Data (FRED) service.

    Each function maps to a specific FRED series, returning fully structured pandas
    DataFrames for seamless integration into AlpaxaQuant’s analytical and forecasting stack.

    --------------------------------------------------------------------
    ▸ Housing & Real Estate
    --------------------------------------------------------------------
    • get_homeownership_rate() — Quarterly homeownership levels
    • get_median_house_sale_price() — Median sale prices of U.S. homes
    • get_new_private_housing_permits() — New construction activity (monthly)
    • get_fifteen_year_fixed_morgage_rate(), get_thirty_year_mortgage_rate()
    • get_total_units_new_private_homes() — Housing starts and completions

    --------------------------------------------------------------------
    ▸ Commodities & Energy
    --------------------------------------------------------------------
    • get_daily_crude_oil_prices(), get_weekly_crude_oil_prices(), get_monthly_crude_oil_prices()
    • get_daily_gold_prices(), get_daily_silver_prices(), get_daily_copper_prices()
    • get_daily_aluminum_prices(), get_daily_soybean_prices(), get_daily_wheat_prices()
    • get_avg_beef_prices(), get_avg_dairy_prices(), get_avg_electricity_prices(), get_egg_avg_prices()
    • Monthly equivalents for all metals and soft commodities

    --------------------------------------------------------------------
    ▸ Inflation, Recession & Financial Conditions
    --------------------------------------------------------------------
    • get_monthly_cpi(), get_core_CPI(), get_semiannual_cpi()
    • get_fed_financial_conditions(), get_financial_stress()
    • get_inflation_expectation(), get_producer_price_index()
    • get_consumer_sentiment(), get_daily_economic_policy_uncertainty()
    • get_NBER_rule_recession_indicator(), get_sahm_rule_recession_indicator()
    • get_smoothed_US_recession_probabilities(), get_personal_savings_rate()
    • get_consumer_loans(), get_delinquincy_rate(), get_delinquincy_rate_credit_card_loans()
    • get_monthly_five_yearly_forward_inflation_expectation_rate()

    --------------------------------------------------------------------
    ▸ Labor Market
    --------------------------------------------------------------------
    • get_unemployed_rate(), get_total_unemployed(), get_job_openings()
    • get_labour_participation_rate(), get_initial_claims()
    • get_unemployement_population_ratio(), get_young_unemployment_rate()
    • get_nonfarm_business_sector_hours_worked()

    --------------------------------------------------------------------
    ▸ Fiscal & Federal Balance Sheet
    --------------------------------------------------------------------
    • get_federal_surplus_deficit(), get_total_assets()
    • get_reverse_repurchase_agreements(), get_all_federal_employees()
    • get_federal_expenditures_interest_payements(), get_quarterly_federal_debt()
    • get_federal_liabilities_capital(), get_federal_liabilities_capital_weekly_average()
    • get_liabilities_capital()

    --------------------------------------------------------------------
    ▸ Monetary Policy & Money Supply
    --------------------------------------------------------------------
    • get_daily_federal_funds_effective(), get_weekly_federal_funds_effective(),
      get_monthly_federal_funds_effective(), get_annual_federal_funds_effective()
    • get_m1_supply(), get_m2_supply(), get_m2_velocity(), get_monetary_base()

    --------------------------------------------------------------------
    ▸ Foreign Exchange & Dollar Strength
    --------------------------------------------------------------------
    • get_daily_US_vs_EURO_rate(), get_monthly_US_vs_EURO_rate(), get_annual_US_vs_EURO_rate()
    • get_JPY_vs_US(), get_pounds_vs_US(), get_francs_vs_US(), get_yuan_vs_US()
    • get_daily_nominal_broad_US_dollar(), get_monthly_nominal_broad_US_dollar()

    --------------------------------------------------------------------
    ▸ Yields & Credit Spreads
    --------------------------------------------------------------------
    • get_ICE_BofA_H_Y_effective_yield(), get_ICE_BofA_H_Y_option_adjusted_spread()
    • get_ICE_BofA_CCC_L_H_Y_option_adjusted_spread()
    • get_daily_moodys_seasoned_BAA_corp_yield(), get_weekly_moodys_seasoned_BAA_corp_yield(),
      get_monthly_moodys_seasoned_BAA_corp_yield()
    • get_daily_ICE_BofA_BBB_corp(), get_daily_ICE_BofA_corp()

    --------------------------------------------------------------------
    ▸ Treasury Curve & Term Spreads
    --------------------------------------------------------------------
    • get_two_yield_us(), get_five_yield_us(), get_ten_yield_us(),
      get_twenty_yield_us(), get_thirty_yield_us()
    • get_daily_market_yield_US_treasury_ten_year_constant(),
      get_monthly_market_yield_US_treasury_ten_year_constant(),
      get_weekly_market_yield_US_treasury_ten_year_constant()
    • get_ten_year_constant_maturity_minus_three_month_treasury_constant()

    --------------------------------------------------------------------
    ▸ GDP & Macroeconomic Growth
    --------------------------------------------------------------------
    • get_real_gdp_growth() — Real GDP, chained volume (quarterly)

    --------------------------------------------------------------------
    ▸ Volatility & Macro Sentiment (VIX-Derived)
    --------------------------------------------------------------------
    • get_VIX(), get_gold_VIX(), get_oil_VIX(), get_NASDAQ_VIX(), get_RUSSELL_VIX(), get_DJIA_VIX()
    • get_equity_market_VIX_sentiment(), get_inflation_VIX_sentiment(),
      get_interest_rate_VIX_sentiment(), get_political_governance_VIX()
    • get_consumer_sentiment_VIX(), get_real_estate_VIX(), get_trade_policy_VIX(),
      get_fiscal_policy_VIX(), get_monetary_policy_VIX(), get_emerging_markets_VIX()

    --------------------------------------------------------------------
    Usage Example
    --------------------------------------------------------------------
    >>> from alpaxa_quant import fred
    >>> key, url = return_FRED_test_api_key(), return_FRED_base_api_endpoint()
    >>> df = fred.get_monthly_cpi(api_key=key, base_url=url, start_date="2020-01-01", end_date="2024-01-01")

    Returns a pandas.DataFrame containing date-indexed macroeconomic observations.

    --------------------------------------------------------------------
    Internal Integration
    --------------------------------------------------------------------
    • All endpoints leverage request_util() for consistent FRED API requests.
    • Handles frequency alignment ('d', 'm', 'q', 'a') and verbose logging.
    • Standardized column structure across all responses.

    Designed for robust econometric modeling, this module integrates 
    seamlessly into AlpaxaQuant’s macroeconomic and forecasting pipelines.
    """

    print(description)
