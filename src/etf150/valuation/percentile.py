from __future__ import annotations

from etf150.models import HistoricalSeriesPoint


def calculate_percentile(current_value: float, history: list[HistoricalSeriesPoint]) -> float:
    """Calculate the percentile rank of the current value within history."""
    if not history:
        raise ValueError("history cannot be empty")

    values = sorted(point.value for point in history)
    count = sum(1 for value in values if value <= current_value)
    return round((count / len(values)) * 100, 2)
