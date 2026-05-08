"""Project configuration constants."""

MARKET_LOW_PB = 2.0
MARKET_EXTREME_PB = 1.6
MARKET_RISK_PE = 46.0
TOTAL_UNITS = 150
EXTREME_BOTTOM_MONTHLY_UNIT_CAP = 40
CENTER_REBALANCE_PERCENTILE_LOW = 45.0
CENTER_REBALANCE_PERCENTILE_HIGH = 55.0
CENTER_REBALANCE_EQUITY_MIN = 40.0
CENTER_REBALANCE_EQUITY_MAX = 45.0
LOW_PERCENTILE_THRESHOLD = 35.0
GOLDEN_THRESHOLD = 20.0
DIAMOND_THRESHOLD = 10.0
RISK_THRESHOLD = 80.0
ROTATION_PERCENTILE_GAP = 20.0

SUPPORTED_INDEXES = {
    "hs300": {
        "name": "沪深300",
        "category": "broad",
        "etf": "510300",
        "akshare_symbol": "sh000300",
        "csindex_symbol": "000300",
    },
    "zz500": {
        "name": "中证500",
        "category": "small_mid",
        "etf": "510500",
        "akshare_symbol": "sh000905",
        "csindex_symbol": "000905",
    },
    "cyb": {
        "name": "创业板",
        "category": "chinext",
        "etf": "159915",
        "akshare_symbol": "sz399006",
        "csindex_symbol": "399006",
    },
    "hongli": {
        "name": "红利",
        "category": "dividend",
        "etf": "515180",
        "akshare_symbol": "sh000922",
        "csindex_symbol": "000922",
    },
}

PANEL_MARKETS = [
    ("A股", "sh000300"),
    ("港股", "hkHSI"),
    ("美股", "usDJI"),
    ("德国", "xetra_dax"),
    ("黄金", "AU0"),
    ("原油", "CL0"),
]

DEFAULT_ROTATION_FROM = "中证500"
DEFAULT_ROTATION_TO = "创业板"
DEFAULT_ROTATION_FROM_PERCENTILE = 65.0
DEFAULT_ROTATION_TO_PERCENTILE = 25.0
DEFAULT_TOTAL_CAPITAL = 150000.0
DEFAULT_SIP_UNITS = 1
DEFAULT_BACKTEST_YEARS = 3
DEFAULT_CATEGORY = "broad"
DEFAULT_PROVIDER = "mock"
DEFAULT_INDEX = "hs300"
DEFAULT_ETF_SYMBOL = "510300"
