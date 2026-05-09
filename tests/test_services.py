from etf150.data.providers.mock import MockDataProvider
from etf150.services import (
    get_allocation,
    get_backtest,
    get_entry_backtest,
    get_iopv,
    get_panel,
    get_signal,
    get_sip,
    get_valuation,
)


def test_get_valuation_returns_valuation_result() -> None:
    result = get_valuation(MockDataProvider(), "hs300")
    assert result["valuation"].index_code == "hs300"


def test_get_signal_returns_signal_report() -> None:
    result = get_signal(
        provider=MockDataProvider(),
        index_code="hs300",
        category="broad",
        capital=150000,
        rotation_from="中证500",
        rotation_from_percentile=65,
        rotation_to="创业板",
        rotation_to_percentile=25,
    )
    assert result["signal"].signal == "data_insufficient"
    assert result["signal"].units.suggested_units == 0
    assert "数据质量不足" in result["signal"].worst_case_message


def test_get_panel_returns_entries() -> None:
    result = get_panel(MockDataProvider())
    assert len(result["panel"]) == 6


def test_get_allocation_can_include_figure() -> None:
    result = get_allocation(MockDataProvider(), include_figure=True)
    assert len(result["allocation"]) > 0
    assert result["figure"] is not None


def test_get_sip_returns_text() -> None:
    result = get_sip(MockDataProvider(), 3)
    assert "3 份" in result["sip"]


def test_get_backtest_returns_result() -> None:
    result = get_backtest(MockDataProvider(), "hs300", 5)
    assert result["backtest"].holding_years == 5


def test_get_entry_backtest_returns_bucketed_result() -> None:
    result = get_entry_backtest(MockDataProvider(), "hs300", 20)
    assert result["entry_backtest"].index_code == "hs300"
    assert len(result["entry_backtest"].entries) == 3


def test_get_iopv_returns_payload() -> None:
    result = get_iopv(MockDataProvider(), "510300")
    assert result["iopv"]["action"] == "wait"
