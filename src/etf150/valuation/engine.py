from __future__ import annotations

from statistics import mean, median

from etf150.config import (
    DIAMOND_THRESHOLD,
    GOLDEN_THRESHOLD,
    MARKET_EXTREME_PB,
    MARKET_LOW_PB,
    MARKET_RISK_PE,
    RISK_THRESHOLD,
)
from etf150.models import ConstituentMetric, IndexSnapshot, ValuationResult
from etf150.valuation.percentile import calculate_percentile

MIN_ACTIONABLE_SAMPLE_SIZE = 30


def filter_valid_pe_samples(constituents: list[ConstituentMetric]) -> list[ConstituentMetric]:
    """Keep only positive and non-extreme PE samples."""
    return [item for item in constituents if 0 < item.pe_ttm <= 150]


def calculate_equal_weight_pe(constituents: list[ConstituentMetric]) -> tuple[float, float, int]:
    """Calculate equal-weight PE mean and median."""
    valid_samples = filter_valid_pe_samples(constituents)
    if not valid_samples:
        raise ValueError("no valid PE samples after filtering")

    pe_values = [item.pe_ttm for item in valid_samples]
    return round(mean(pe_values), 2), round(median(pe_values), 2), len(valid_samples)


def determine_market_pb_zone(current_pb: float) -> str:
    """Determine the market PB zone."""
    if current_pb < MARKET_EXTREME_PB:
        return "extreme_bottom"
    if current_pb < MARKET_LOW_PB:
        return "undervalued"
    return "normal"


def determine_valuation_zone(percentile: float, market_pe: float) -> str:
    """Determine the valuation zone."""
    if percentile > RISK_THRESHOLD or market_pe > MARKET_RISK_PE:
        return "risk"
    if percentile < DIAMOND_THRESHOLD:
        return "diamond"
    if percentile < GOLDEN_THRESHOLD:
        return "golden"
    return "normal"


def uses_proxy_samples(constituents: list[ConstituentMetric]) -> bool:
    """Return whether a snapshot uses index proxy rows instead of constituents."""
    return any(item.code.startswith("index_proxy_") for item in constituents)


def assess_data_quality(
    constituents: list[ConstituentMetric],
    valid_sample_size: int,
) -> tuple[bool, bool, str]:
    """Assess whether valuation data is strong enough for trading actions."""
    proxy_samples = uses_proxy_samples(constituents)
    notes: list[str] = []
    if proxy_samples:
        notes.append("使用指数代理样本，未取得完整成分股估值")
    if valid_sample_size < MIN_ACTIONABLE_SAMPLE_SIZE:
        notes.append(f"有效估值样本不足：{valid_sample_size} < {MIN_ACTIONABLE_SAMPLE_SIZE}")
    return not notes, proxy_samples, "；".join(notes)


def build_valuation(snapshot: IndexSnapshot) -> ValuationResult:
    """Build valuation metrics from a market snapshot."""
    equal_weight_pe_mean, equal_weight_pe_median, valid_sample_size = calculate_equal_weight_pe(
        snapshot.constituents
    )
    percentile_5y = calculate_percentile(equal_weight_pe_mean, snapshot.history_5y)
    percentile_10y = calculate_percentile(equal_weight_pe_mean, snapshot.history_10y)
    composite_percentile = min(percentile_5y, percentile_10y)
    valuation_zone = determine_valuation_zone(composite_percentile, snapshot.market_pe)
    market_pb_zone = determine_market_pb_zone(snapshot.market_pb)
    is_actionable, proxy_samples, data_quality_note = assess_data_quality(
        snapshot.constituents,
        valid_sample_size,
    )

    return ValuationResult(
        index_code=snapshot.code,
        index_name=snapshot.name,
        equal_weight_pe_mean=equal_weight_pe_mean,
        equal_weight_pe_median=equal_weight_pe_median,
        valid_sample_size=valid_sample_size,
        current_pb=snapshot.market_pb,
        percentile_5y=percentile_5y,
        percentile_10y=percentile_10y,
        valuation_zone=valuation_zone,
        market_pb_zone=market_pb_zone,
        is_risk_zone=valuation_zone == "risk",
        is_actionable=is_actionable,
        uses_proxy_samples=proxy_samples,
        data_quality_note=data_quality_note,
    )
