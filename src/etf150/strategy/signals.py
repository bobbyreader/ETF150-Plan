from __future__ import annotations

from etf150.models import RotationSuggestion, SignalReport, ValuationResult
from etf150.strategy.position import suggest_position
from etf150.strategy.risk import estimate_max_drawdown
from etf150.strategy.units import suggest_units


def build_signal_report(
    valuation: ValuationResult,
    total_capital: float,
    category: str,
    iopv_warning: str | None = None,
    rotation: RotationSuggestion | None = None,
) -> SignalReport:
    """Combine valuation and strategy outputs into a final signal report."""
    current_percentile = min(valuation.percentile_5y, valuation.percentile_10y)
    position = suggest_position(current_percentile)
    units = suggest_units(total_capital, valuation.valuation_zone, valuation.market_pb_zone)
    max_drawdown_range = estimate_max_drawdown(category)

    if iopv_warning:
        signal = "wait"
    elif valuation.valuation_zone == "risk":
        signal = "sell_or_reduce"
    elif valuation.valuation_zone in {"diamond", "golden"}:
        signal = "buy"
    else:
        signal = "watch"

    worst_case_message = f"最坏情况预估回撤：{max_drawdown_range}，请只按计划投入并做好心理预期。"
    return SignalReport(
        signal=signal,
        valuation=valuation,
        position=position,
        units=units,
        max_drawdown_range=max_drawdown_range,
        iopv_warning=iopv_warning,
        rotation=rotation,
        worst_case_message=worst_case_message,
    )
