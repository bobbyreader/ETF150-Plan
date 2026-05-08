from datetime import date

from etf150.models import ConstituentMetric, HistoricalSeriesPoint, IndexSnapshot
from etf150.valuation.engine import build_valuation, calculate_equal_weight_pe, filter_valid_pe_samples


def test_filter_valid_pe_samples_excludes_negative_and_extreme_values() -> None:
    constituents = [
        ConstituentMetric(code="a", name="A", pe_ttm=12, pb=1.2),
        ConstituentMetric(code="b", name="B", pe_ttm=-1, pb=1.1),
        ConstituentMetric(code="c", name="C", pe_ttm=151, pb=1.3),
    ]

    filtered = filter_valid_pe_samples(constituents)

    assert [item.code for item in filtered] == ["a"]


def test_calculate_equal_weight_pe_returns_mean_median_and_count() -> None:
    constituents = [
        ConstituentMetric(code="a", name="A", pe_ttm=10, pb=1.2),
        ConstituentMetric(code="b", name="B", pe_ttm=20, pb=1.1),
        ConstituentMetric(code="c", name="C", pe_ttm=30, pb=1.3),
    ]

    result = calculate_equal_weight_pe(constituents)

    assert result == (20, 20, 3)


def test_build_valuation_uses_filtered_equal_weight_pe() -> None:
    history = [HistoricalSeriesPoint(day=date(2026, 1, day), value=value) for day, value in enumerate([10, 12, 14, 16, 18], start=1)]
    snapshot = IndexSnapshot(
        code="hs300",
        name="HS300",
        category="broad",
        market_pe=14,
        market_pb=1.8,
        constituents=[
            ConstituentMetric(code="a", name="A", pe_ttm=10, pb=1.0),
            ConstituentMetric(code="b", name="B", pe_ttm=20, pb=1.0),
            ConstituentMetric(code="c", name="C", pe_ttm=-2, pb=1.0),
        ],
        history_5y=history,
        history_10y=history,
    )

    valuation = build_valuation(snapshot)

    assert valuation.equal_weight_pe_mean == 15
    assert valuation.equal_weight_pe_median == 15
    assert valuation.valid_sample_size == 2
    assert valuation.market_pb_zone == "undervalued"
