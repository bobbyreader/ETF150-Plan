from __future__ import annotations

import pandas as pd
import pytest

from etf150.data.providers.akshare_provider import AkshareDataProvider


class DummyAk:
    def stock_index_pe_lg(self, symbol: str) -> pd.DataFrame:
        if symbol == "bad":
            raise ValueError("boom")
        return pd.DataFrame(
            [
                {"日期": "2024-01-01", "滚动市盈率": 10, "等权滚动市盈率": 11},
                {"日期": "2024-01-02", "滚动市盈率": 12, "等权滚动市盈率": 13},
            ]
        )

    def stock_index_pb_lg(self, symbol: str) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"日期": "2024-01-01", "市净率": 1.2},
                {"日期": "2024-01-02", "市净率": 1.3},
            ]
        )

    def stock_zh_index_daily_em(self, symbol: str) -> pd.DataFrame:
        return pd.DataFrame([{"close": 10.0}, {"close": 12.0}, {"close": 13.0}])

    def fund_etf_spot_em(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"代码": "510300", "最新价": 4.9, "IOPV实时估值": 4.8},
                {"代码": "159915", "最新价": 2.5, "IOPV实时估值": None},
            ]
        )

    def fund_etf_hist_em(self, symbol: str, period: str, adjust: str) -> pd.DataFrame:
        return pd.DataFrame([{"收盘": 1.0}, {"收盘": 1.1}, {"收盘": 1.2}])

    def index_stock_cons_weight_csindex(self, symbol: str) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"成分券代码": "000001", "成分券名称": "平安银行"},
                {"成分券代码": "000002", "成分券名称": "万科A"},
            ]
        )


@pytest.fixture
def provider(monkeypatch: pytest.MonkeyPatch) -> AkshareDataProvider:
    monkeypatch.setattr("etf150.data.providers.akshare_provider.AkshareDataProvider.__init__", lambda self: setattr(self, "_ak", DummyAk()))
    instance = AkshareDataProvider()
    instance._get_index_pe_frame.cache_clear()
    instance._get_index_pb_frame.cache_clear()
    instance._get_index_daily_frame.cache_clear()
    instance._get_etf_spot_frame.cache_clear()
    return instance


def test_get_iopv_snapshot_wait(provider: AkshareDataProvider) -> None:
    snapshot = provider.get_iopv_snapshot("510300")
    assert snapshot.action == "wait"
    assert snapshot.premium_pct > 0


def test_get_iopv_snapshot_unknown_when_iopv_missing(provider: AkshareDataProvider) -> None:
    snapshot = provider.get_iopv_snapshot("159915")
    assert snapshot.action == "unknown"
    assert snapshot.iopv is None


def test_get_backtest_series_returns_prices(provider: AkshareDataProvider) -> None:
    series = provider.get_backtest_series("hs300", 3)
    assert series == [10.0, 12.0, 13.0]


def test_get_price_series_prefers_etf_history(provider: AkshareDataProvider) -> None:
    series = provider.get_price_series("510300", 3)
    assert series == [1.0, 1.1, 1.2]


def test_get_index_snapshot_builds_payload(provider: AkshareDataProvider) -> None:
    snapshot = provider.get_index_snapshot("hs300")
    assert snapshot.name == "沪深300"
    assert snapshot.market_pe == 12.0
    assert snapshot.market_pb == 1.3
    assert len(snapshot.constituents) == 2
    assert len(snapshot.history_5y) == 2


def test_latest_percentile_uses_equal_weight_pe(provider: AkshareDataProvider) -> None:
    frame = pd.DataFrame([{"等权滚动市盈率": 10}, {"等权滚动市盈率": 20}, {"等权滚动市盈率": 20}])
    assert provider._latest_percentile_from_frame(frame) == 100.0


def test_get_lg_symbol_raises_for_unsupported(provider: AkshareDataProvider) -> None:
    with pytest.raises(RuntimeError, match="乐咕乐股估值映射"):
        provider._get_lg_symbol("unknown")
