from etf150.cli import handle_iopv
from etf150.data.providers.mock import MockDataProvider


def test_iopv_marks_wait_when_price_exceeds_iopv() -> None:
    result = handle_iopv(MockDataProvider(), "510300")
    assert result["iopv"]["action"] == "wait"
    assert result["iopv"]["premium_pct"] > 0


def test_iopv_marks_buy_ok_when_price_below_iopv() -> None:
    result = handle_iopv(MockDataProvider(), "159915")
    assert result["iopv"]["action"] == "buy_ok"
