from datetime import date, timedelta

from etf150.backtest.engine import run_backtest, run_valuation_entry_backtest
from etf150.models import HistoricalSeriesPoint


def test_run_backtest_returns_core_metrics() -> None:
    result = run_backtest("hs300", [100, 90, 120], 3)

    assert result.index_code == "hs300"
    assert result.cumulative_return_pct == 20.0
    assert result.max_drawdown_pct == 10.0
    assert result.annualized_return_pct > 0


def test_run_valuation_entry_backtest_groups_by_entry_percentile() -> None:
    base_day = date(2020, 1, 1)
    prices = [100, 100, 100, 110, 90, 150, 80]
    valuations = [10, 60, 90, 15, 85, 55, 50]
    price_points = [
        HistoricalSeriesPoint(day=base_day + timedelta(days=index), value=value)
        for index, value in enumerate(prices)
    ]
    valuation_points = [
        HistoricalSeriesPoint(day=base_day + timedelta(days=index), value=value)
        for index, value in enumerate(valuations)
    ]

    result = run_valuation_entry_backtest(
        index_code="hs300",
        price_points=price_points,
        valuation_points=valuation_points,
        holding_days=2,
    )

    buckets = {item.bucket: item for item in result.entries}
    assert buckets["low"].sample_size == 1
    assert buckets["normal"].sample_size == 2
    assert buckets["high"].sample_size == 2
    assert buckets["low"].average_return_pct > buckets["high"].average_return_pct
