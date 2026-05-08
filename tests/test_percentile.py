from datetime import date

from etf150.models import HistoricalSeriesPoint
from etf150.valuation.percentile import calculate_percentile


def test_calculate_percentile_returns_expected_rank() -> None:
    history = [
        HistoricalSeriesPoint(day=date(2026, 1, 1), value=10),
        HistoricalSeriesPoint(day=date(2026, 1, 2), value=20),
        HistoricalSeriesPoint(day=date(2026, 1, 3), value=30),
        HistoricalSeriesPoint(day=date(2026, 1, 4), value=40),
    ]

    assert calculate_percentile(20, history) == 50.0
    assert calculate_percentile(35, history) == 75.0
