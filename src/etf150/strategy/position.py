from __future__ import annotations

from etf150.config import (
    CENTER_REBALANCE_EQUITY_MAX,
    CENTER_REBALANCE_EQUITY_MIN,
    CENTER_REBALANCE_PERCENTILE_HIGH,
    CENTER_REBALANCE_PERCENTILE_LOW,
    LOW_PERCENTILE_THRESHOLD,
)
from etf150.models import PositionSuggestion


def suggest_position(current_percentile: float) -> PositionSuggestion:
    """Suggest target equity position based on current percentile."""
    target = 100.0 - current_percentile
    rationale_parts: list[str] = [f"基准仓位={target:.2f}%"]

    if current_percentile > 50:
        target = target / 2
        rationale_parts.append("高估区减半")
    elif CENTER_REBALANCE_PERCENTILE_LOW <= current_percentile <= CENTER_REBALANCE_PERCENTILE_HIGH:
        target = max(CENTER_REBALANCE_EQUITY_MIN, min(CENTER_REBALANCE_EQUITY_MAX, target))
        rationale_parts.append("中枢回归到40%-45%")
    elif current_percentile < LOW_PERCENTILE_THRESHOLD:
        uplift = min(10.0, (LOW_PERCENTILE_THRESHOLD - current_percentile) * 0.4)
        target = min(100.0, target + uplift)
        rationale_parts.append(f"低估放大+{uplift:.2f}%")

    return PositionSuggestion(
        target_equity_pct=round(target, 2),
        current_percentile=current_percentile,
        rationale="；".join(rationale_parts),
    )
