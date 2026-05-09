from __future__ import annotations

from statistics import mean, median

from etf150.backtest.metrics import calculate_annualized_return, calculate_max_drawdown
from etf150.models import BacktestResult, EntryBacktestBucket, EntryBacktestResult, HistoricalSeriesPoint


def run_backtest(index_code: str, series: list[float], years: int) -> BacktestResult:
    """Run a simple buy-and-hold backtest over the provided series."""
    if len(series) < 2:
        raise ValueError("series must contain at least two points")

    start_value = series[0]
    end_value = series[-1]
    cumulative_return_pct = round(((end_value / start_value) - 1) * 100, 2)
    annualized_return_pct = calculate_annualized_return(start_value, end_value, years)
    max_drawdown_pct = calculate_max_drawdown(series)

    return BacktestResult(
        index_code=index_code,
        holding_years=years,
        start_value=round(start_value, 2),
        end_value=round(end_value, 2),
        annualized_return_pct=annualized_return_pct,
        cumulative_return_pct=cumulative_return_pct,
        max_drawdown_pct=max_drawdown_pct,
    )


def run_valuation_entry_backtest(
    index_code: str,
    price_points: list[HistoricalSeriesPoint],
    valuation_points: list[HistoricalSeriesPoint],
    holding_days: int,
) -> EntryBacktestResult:
    """Compare forward returns from low, normal, and high valuation entries."""
    if holding_days <= 0:
        raise ValueError("holding_days must be positive")
    if len(price_points) < holding_days + 1:
        raise ValueError("price_points must cover at least one holding window")

    prices_by_day = {point.day: point.value for point in price_points}
    valuation_by_day = {point.day: point.value for point in valuation_points}
    common_days = sorted(set(prices_by_day) & set(valuation_by_day))
    if not common_days:
        raise ValueError("price and valuation series do not overlap")

    valuation_values = [valuation_by_day[day] for day in common_days]
    returns_by_bucket: dict[str, list[float]] = {"low": [], "normal": [], "high": []}
    ordered_prices = [(point.day, point.value) for point in sorted(price_points, key=lambda item: item.day)]
    index_by_day = {day: index for index, (day, _) in enumerate(ordered_prices)}

    for day in common_days:
        start_index = index_by_day.get(day)
        if start_index is None or start_index + holding_days >= len(ordered_prices):
            continue
        start_price = prices_by_day[day]
        end_price = ordered_prices[start_index + holding_days][1]
        if start_price <= 0:
            continue
        percentile = _percentile_rank(valuation_by_day[day], valuation_values)
        bucket = _entry_bucket(percentile)
        returns_by_bucket[bucket].append(round(((end_price / start_price) - 1) * 100, 2))

    return EntryBacktestResult(
        index_code=index_code,
        holding_days=holding_days,
        entries=[
            _build_bucket("low", "低估起点(<20%)", 0.0, 20.0, returns_by_bucket["low"]),
            _build_bucket("normal", "正常起点(20%-80%)", 20.0, 80.0, returns_by_bucket["normal"]),
            _build_bucket("high", "高估起点(>80%)", 80.0, 100.0, returns_by_bucket["high"]),
        ],
    )


def _percentile_rank(value: float, values: list[float]) -> float:
    below_or_equal = sum(1 for item in values if item <= value)
    return (below_or_equal / len(values)) * 100


def _entry_bucket(percentile: float) -> str:
    if percentile < 20:
        return "low"
    if percentile > 80:
        return "high"
    return "normal"


def _build_bucket(
    bucket: str,
    label: str,
    percentile_min: float,
    percentile_max: float,
    returns: list[float],
) -> EntryBacktestBucket:
    if not returns:
        return EntryBacktestBucket(
            bucket=bucket,
            label=label,
            percentile_min=percentile_min,
            percentile_max=percentile_max,
            sample_size=0,
            average_return_pct=None,
            median_return_pct=None,
            best_return_pct=None,
            worst_return_pct=None,
        )
    return EntryBacktestBucket(
        bucket=bucket,
        label=label,
        percentile_min=percentile_min,
        percentile_max=percentile_max,
        sample_size=len(returns),
        average_return_pct=round(mean(returns), 2),
        median_return_pct=round(median(returns), 2),
        best_return_pct=max(returns),
        worst_return_pct=min(returns),
    )
