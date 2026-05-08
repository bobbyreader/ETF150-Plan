from __future__ import annotations

from etf150.config import ROTATION_PERCENTILE_GAP
from etf150.models import RotationSuggestion


def suggest_rotation(from_asset: str, from_percentile: float, to_asset: str, to_percentile: float) -> RotationSuggestion:
    """Suggest rotation when two same-class assets have a large valuation gap."""
    gap = from_percentile - to_percentile
    if gap >= ROTATION_PERCENTILE_GAP:
        return RotationSuggestion(
            should_rotate=True,
            from_asset=from_asset,
            to_asset=to_asset,
            rationale=f"{from_asset} 相对高估，较 {to_asset} 高 {gap:.2f} 个百分位，建议内部换马",
        )

    return RotationSuggestion(
        should_rotate=False,
        from_asset=None,
        to_asset=None,
        rationale="同类资产估值差不足，不建议换马",
    )
