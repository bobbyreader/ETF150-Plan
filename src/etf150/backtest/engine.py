from __future__ import annotations

from etf150.backtest.metrics import calculate_annualized_return, calculate_max_drawdown
from etf150.models import BacktestResult


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
