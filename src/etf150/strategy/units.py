from __future__ import annotations

from etf150.config import EXTREME_BOTTOM_MONTHLY_UNIT_CAP, TOTAL_UNITS
from etf150.models import UnitSuggestion


def suggest_units(total_capital: float, valuation_zone: str, market_pb_zone: str) -> UnitSuggestion:
    """Suggest how many of the 150 units to deploy."""
    unit_amount = total_capital / TOTAL_UNITS
    suggested_units = 1
    rationale = "常规买入1份"

    if valuation_zone == "diamond":
        suggested_units = 4
        rationale = "钻石区域加速买入4份"
    elif valuation_zone == "golden":
        suggested_units = 2
        rationale = "黄金区域加速买入2份"

    if market_pb_zone == "extreme_bottom":
        suggested_units = EXTREME_BOTTOM_MONTHLY_UNIT_CAP
        rationale = "全市场PB接近极限区域，单月最高投入40份"

    suggested_amount = round(unit_amount * suggested_units, 2)
    return UnitSuggestion(
        total_capital=total_capital,
        total_units=TOTAL_UNITS,
        unit_amount=round(unit_amount, 2),
        suggested_units=suggested_units,
        suggested_amount=suggested_amount,
        rationale=rationale,
    )
