import json

from etf150.cli import build_parser, handle_allocation, handle_backtest, handle_panel, handle_signal, handle_sip, handle_valuation
from etf150.data.providers.mock import MockDataProvider


def test_parser_accepts_valuation_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["valuation", "--provider", "mock", "--index", "hs300"])
    assert args.command == "valuation"
    assert args.index == "hs300"


def test_handle_valuation_returns_payload() -> None:
    result = handle_valuation(MockDataProvider(), "hs300")
    assert result["valuation"].index_code == "hs300"


def test_handle_signal_returns_wait_for_iopv_premium() -> None:
    parser = build_parser()
    args = parser.parse_args(["signal", "--provider", "mock", "--index", "510300", "--category", "broad"])
    result = handle_signal(MockDataProvider(), args)
    assert result["signal"].signal == "wait"


def test_handle_panel_returns_entries() -> None:
    result = handle_panel(MockDataProvider())
    assert len(result["panel"]) >= 3


def test_handle_allocation_writes_chart(tmp_path) -> None:
    result = handle_allocation(MockDataProvider(), str(tmp_path / "allocation.png"))
    assert (tmp_path / "allocation.png").exists()
    assert len(result["allocation"]) > 0


def test_handle_sip_returns_text() -> None:
    result = handle_sip(MockDataProvider(), 2)
    assert "2 份" in result["sip"]


def test_handle_backtest_returns_result() -> None:
    result = handle_backtest(MockDataProvider(), "hs300", 3)
    assert result["backtest"].holding_years == 3


def test_renderable_payload_can_be_json_encoded() -> None:
    result = handle_panel(MockDataProvider())
    json.dumps({"count": len(result["panel"])})
