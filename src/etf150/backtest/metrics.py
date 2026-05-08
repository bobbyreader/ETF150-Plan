from __future__ import annotations


def calculate_max_drawdown(series: list[float]) -> float:
    """Calculate max drawdown percentage from a value series."""
    if not series:
        raise ValueError("series cannot be empty")

    peak = series[0]
    max_drawdown = 0.0
    for value in series:
        peak = max(peak, value)
        drawdown = (peak - value) / peak * 100
        max_drawdown = max(max_drawdown, drawdown)
    return round(max_drawdown, 2)


def calculate_annualized_return(start_value: float, end_value: float, years: int) -> float:
    """Calculate annualized return percentage."""
    if start_value <= 0 or years <= 0:
        raise ValueError("start_value and years must be positive")
    return round((((end_value / start_value) ** (1 / years)) - 1) * 100, 2)
