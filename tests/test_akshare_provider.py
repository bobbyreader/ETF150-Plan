from __future__ import annotations

import pandas as pd
import pytest

from etf150.data.cache import FrameCache
from etf150.data.providers.akshare_provider import AkshareDataProvider


class DummyAk:
    fail_pe = False
    fail_stock_spot = False
    fail_constituents = False

    def stock_index_pe_lg(self, symbol: str) -> pd.DataFrame:
        if self.fail_pe:
            raise ValueError("temporary outage")
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
        if self.fail_constituents:
            raise ValueError("constituent outage")
        return pd.DataFrame(
            [
                {"成分券代码": "000001", "成分券名称": "平安银行"},
                {"成分券代码": "000002", "成分券名称": "万科A"},
            ]
        )

    def stock_zh_a_spot_em(self) -> pd.DataFrame:
        if self.fail_stock_spot:
            raise ValueError("spot outage")
        return pd.DataFrame(
            [
                {"代码": "000001", "市盈率-动态": 8.0},
                {"代码": "000002", "市盈率-动态": 12.0},
                {"代码": "000003", "市盈率-动态": 220.0},
            ]
        )

    def stock_hk_index_daily_sina(self, symbol: str) -> pd.DataFrame:
        return pd.DataFrame([{"date": "2024-01-01", "close": 100}, {"date": "2024-01-02", "close": 110}])

    def index_global_hist_em(self, symbol: str) -> pd.DataFrame:
        return pd.DataFrame([{"日期": "2024-01-01", "收盘": 100}, {"日期": "2024-01-02", "收盘": 120}])

    def futures_global_hist_em(self, symbol: str) -> pd.DataFrame:
        return pd.DataFrame([{"日期": "2024-01-01", "收盘": 100}, {"日期": "2024-01-02", "收盘": 80}])


@pytest.fixture
def provider(monkeypatch: pytest.MonkeyPatch, tmp_path) -> AkshareDataProvider:
    monkeypatch.setattr("etf150.data.providers.akshare_provider.AkshareDataProvider.__init__", lambda self: setattr(self, "_ak", DummyAk()))
    instance = AkshareDataProvider()
    instance._cache = FrameCache(tmp_path / "akshare-cache")
    instance._get_index_pe_frame.cache_clear()
    instance._get_index_pb_frame.cache_clear()
    instance._get_index_daily_frame.cache_clear()
    instance._get_etf_spot_frame.cache_clear()
    instance._get_a_share_pe_lookup.cache_clear()
    instance._get_constituent_frame.cache_clear()
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
    assert [item.pe_ttm for item in snapshot.constituents] == [8.0, 12.0]
    assert len(snapshot.history_5y) == 2


def test_get_index_snapshot_falls_back_to_index_proxy_when_stock_pe_unavailable(provider: AkshareDataProvider) -> None:
    provider._ak.fail_stock_spot = True
    provider._get_a_share_pe_lookup.cache_clear()

    snapshot = provider.get_index_snapshot("hs300")

    assert [item.code for item in snapshot.constituents] == ["index_proxy_equal_weight", "index_proxy_market_weight"]


def test_get_index_snapshot_falls_back_to_index_proxy_when_constituents_unavailable(provider: AkshareDataProvider) -> None:
    provider._ak.fail_constituents = True
    provider._get_constituent_frame.cache_clear()

    snapshot = provider.get_index_snapshot("hs300")

    assert [item.code for item in snapshot.constituents] == ["index_proxy_equal_weight", "index_proxy_market_weight"]


def test_latest_percentile_uses_equal_weight_pe(provider: AkshareDataProvider) -> None:
    frame = pd.DataFrame([{"等权滚动市盈率": 10}, {"等权滚动市盈率": 20}, {"等权滚动市盈率": 20}])
    assert provider._latest_percentile_from_frame(frame) == 100.0


def test_get_lg_symbol_raises_for_unsupported(provider: AkshareDataProvider) -> None:
    with pytest.raises(RuntimeError, match="乐咕乐股估值映射"):
        provider._get_lg_symbol("unknown")


def test_get_index_pe_frame_uses_stale_cache_after_error(provider: AkshareDataProvider) -> None:
    first = provider._get_index_pe_frame("hs300")
    provider._ak.fail_pe = True
    provider._get_index_pe_frame.cache_clear()

    second = provider._get_index_pe_frame("hs300")

    assert second.equals(first)


def test_get_panel_entries_uses_real_proxy_data_for_all_markets(provider: AkshareDataProvider) -> None:
    entries = provider.get_panel_entries()
    notes = {entry.market: entry.note for entry in entries}

    assert "真实数据" in notes["港股"]
    assert "真实数据" in notes["美股"]
    assert "真实数据" in notes["德国"]
    assert "真实数据" in notes["黄金"]
    assert "真实数据" in notes["原油"]
