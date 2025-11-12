"""
AlpaxaQuant — Quantitative Finance and Data Acquisition Library
===============================================================

Central metadata for the AlpaxaQuant package.  
This file defines package-level constants for versioning, authorship,
licensing, and repository information.  
These variables are imported by setup scripts, documentation builders,
and runtime modules to ensure consistency across the ecosystem.
"""

__title__ = "AlpaxaQuant"
__summary__ = (
    "An end-to-end quantitative finance and econometric data platform "
    "providing unified access to EODHD, FINRA, FRED, and insider trade datasets."
)
__uri__ = "https://github.com/Joanmascastella/AlpaxaQuant"

__version__ = "1.0.1"

__author__ = "Joan Mas Castella"
__email__ = "jmascastella@gmail.com"

__license__ = "Apache License 2.0"
__copyright__ = "© 2025 Joan Mas Castella"

__maintainer__ = "Joan Mas Castella"
__status__ = "Production"

__keywords__ = [
    "quantitative finance",
    "financial data",
    "macroeconomics",
    "insider trading",
    "market data",
    "FRED",
    "EODHD",
    "FINRA",
    "econometrics",
    "trading models",
]

if __name__ == "__main__":
    print(f"{__title__} v{__version__}")
    print(f"Author: {__author__} <{__email__}>")
    print(f"License: {__license__}")
    print(f"URL: {__uri__}")
