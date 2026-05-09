import json
import os
import subprocess
import sys

from etf150.cli import (
    build_parser,
    handle_allocation,
    handle_backtest,
    handle_entry_backtest,
    handle_panel,
    handle_signal,
    handle_sip,
    handle_valuation,
)
from etf150.data.providers.mock import MockDataProvider


def test_parser_accepts_valuation_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["valuation", "--provider", "mock", "--index", "hs300"])
    assert args.command == "valuation"
    assert args.index == "hs300"


def test_cli_import_does_not_load_matplotlib() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; import etf150.cli; print('matplotlib' in sys.modules); print('matplotlib.pyplot' in sys.modules)",
        ],
        check=True,
        capture_output=True,
        env={**os.environ, "PYTHONPATH": "src"},
        text=True,
    )
    assert result.stdout.strip().splitlines() == ["False", "False"]


def test_handle_valuation_returns_payload() -> None:
    result = handle_valuation(MockDataProvider(), "hs300")
    assert result["valuation"].index_code == "hs300"


def test_handle_signal_returns_data_insufficient_for_low_quality_valuation() -> None:
    parser = build_parser()
    args = parser.parse_args(["signal", "--provider", "mock", "--index", "510300", "--category", "broad"])
    result = handle_signal(MockDataProvider(), args)
    assert result["signal"].signal == "data_insufficient"


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


def test_parser_accepts_entry_backtest_command() -> None:
    parser = build_parser()
    args = parser.parse_args(["entry-backtest", "--provider", "mock", "--index", "hs300", "--holding-days", "20"])
    assert args.command == "entry-backtest"
    assert args.holding_days == 20


def test_handle_entry_backtest_returns_bucketed_result() -> None:
    result = handle_entry_backtest(MockDataProvider(), "hs300", 20)
    assert result["entry_backtest"].entries[0].bucket == "low"


def test_renderable_payload_can_be_json_encoded() -> None:
    result = handle_panel(MockDataProvider())
    json.dumps({"count": len(result["panel"])})
