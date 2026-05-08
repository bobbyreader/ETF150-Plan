from etf150.backtest.engine import run_backtest


def test_run_backtest_returns_core_metrics() -> None:
    result = run_backtest("hs300", [100, 90, 120], 3)

    assert result.index_code == "hs300"
    assert result.cumulative_return_pct == 20.0
    assert result.max_drawdown_pct == 10.0
    assert result.annualized_return_pct > 0
