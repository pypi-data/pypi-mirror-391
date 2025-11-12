"""
AlpaxaQuant — Command-Line Entry Point
======================================

This file enables the package to be executed directly with:
    python -m alpaxa_quant

It displays version information and a concise summary of all available modules.
"""

from . import __version__, describe

def main():
    banner = f"""
AlpaxaQuant v{__version__}
A comprehensive quantitative finance and data acquisition library.

Available Modules:
    • utils           – Helper functions for HTTP requests, retries, and API normalization.
    • eodhd           – Market, financial, and sentiment data from EODHD API.
    • insider_trades  – Insider trading data scraper with advanced filters and caching.
    • finra           – Market structure, debt, and short interest data from FINRA.
    • fred            – Macroeconomic and commodity data from the FRED API.

Usage Examples:
    import alpaxa_quant as aq
    df = aq.eodhd.get_historical_ticker_price(ticker="AAPL", fmt="json", period="d")
    print(df.head())

    python -m alpaxa_quant --version

"""
    print(banner.strip())


if __name__ == "__main__":
    import sys

    # Optional: simple CLI flag for version
    if len(sys.argv) > 1 and sys.argv[1] in ("-v", "--version"):
        print(f"AlpaxaQuant {__version__}")
    else:
        main()
