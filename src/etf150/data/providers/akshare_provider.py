from __future__ import annotations

from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

import pandas as pd

from etf150.config import DEFAULT_INDEX, SUPPORTED_INDEXES
from etf150.data.providers.mock import MockDataProvider
from etf150.models import ConstituentMetric, HistoricalSeriesPoint, IOPVSnapshot, IndexSnapshot, PanelEntry


class AkshareDataProvider(MockDataProvider):
    """AkShare-backed provider with explicit capability boundaries."""

    _LG_SYMBOLS = {
        "hs300": "沪深300",
        "zz500": "中证500",
        "cyb": "创业板50",
        "hongli": "深证红利",
    }
    _PANEL_INDEX_SYMBOLS = {
        "A股": "沪深300",
        "港股": None,
        "美股": None,
        "德国": None,
        "黄金": None,
        "原油": None,
    }

    def __init__(self) -> None:
        try:
            import akshare as ak
        except ImportError as error:
            raise RuntimeError("AkShare is not installed") from error
        self._ak = ak

    def get_index_snapshot(self, index_code: str) -> IndexSnapshot:
        index_meta = self._get_index_meta(index_code)
        pe_frame = self._get_index_pe_frame(index_code)
        pb_frame = self._get_index_pb_frame(index_code)
        latest_pe = pe_frame.iloc[-1]
        latest_pb = pb_frame.iloc[-1]
        iopv_snapshot = self.get_iopv_snapshot(index_meta["etf"])
        history_5y = self._build_history_points(pe_frame, years=5)
        history_10y = self._build_history_points(pe_frame, years=10)

        return IndexSnapshot(
            code=index_code,
            name=index_meta["name"],
            category=index_meta["category"],
            market_pe=self._require_float(latest_pe.get("滚动市盈率"), f"{index_meta['name']} 当前滚动市盈率缺失"),
            market_pb=self._require_float(latest_pb.get("市净率"), f"{index_meta['name']} 当前市净率缺失"),
            current_price=iopv_snapshot.current_price,
            iopv=iopv_snapshot.iopv,
            constituents=self._build_constituents(index_code, latest_pe, latest_pb),
            history_5y=history_5y,
            history_10y=history_10y,
        )

    def get_panel_entries(self) -> list[PanelEntry]:
        entries: list[PanelEntry] = []
        for market, symbol in self._PANEL_INDEX_SYMBOLS.items():
            if symbol is None:
                entries.append(
                    PanelEntry(
                        market=market,
                        percentile=50.0,
                        zone="normal",
                        note=self.get_market_source_note(market),
                    )
                )
                continue
            try:
                index_code = self._find_index_code_by_lg_symbol(symbol)
                pe_frame = self._get_index_pe_frame(index_code)
                percentile = self._latest_percentile_from_frame(pe_frame)
                entries.append(
                    PanelEntry(
                        market=market,
                        percentile=percentile,
                        zone=self._percentile_to_zone(percentile),
                        note=self.get_market_source_note(market),
                    )
                )
            except Exception as error:
                entries.append(
                    PanelEntry(
                        market=market,
                        percentile=50.0,
                        zone="normal",
                        note=f"{self.get_market_source_note(market)}；{error}",
                    )
                )
        return entries

    def get_backtest_series(self, index_code: str, years: int) -> list[float]:
        frame = self._get_index_daily_frame(index_code)
        trailing = frame.tail(max(years * 252, 2))
        series = [self._require_float(value, "指数历史收盘价缺失") for value in trailing["close"].tolist()]
        if len(series) < 2:
            raise RuntimeError("AkShare 历史价格样本不足，无法回测")
        return series

    def get_price_series(self, symbol: str, years: int) -> list[float]:
        try:
            return self._get_etf_price_series(symbol, years)
        except RuntimeError:
            return self.get_backtest_series(self._find_index_code_by_etf(symbol), years)

    def get_iopv_snapshot(self, symbol: str) -> IOPVSnapshot:
        row = self._get_etf_spot_row(symbol)
        current_price = self._require_float(row.get("最新价"), f"ETF {symbol} 最新价缺失")
        iopv = self._optional_float(row.get("IOPV实时估值"))
        premium_pct = None
        action = "buy_ok"
        note = "现价未高于IOPV，可按计划执行"
        if iopv is None:
            action = "unknown"
            note = "暂无 IOPV 数据，无法判断溢价，请谨慎执行。"
        elif iopv > 0:
            premium_pct = round(((current_price / iopv) - 1) * 100, 2)
            if current_price > iopv:
                action = "wait"
                note = f"现价 {current_price:.2f} 高于 IOPV {iopv:.2f}，暂不买入"
        return IOPVSnapshot(
            symbol=symbol,
            current_price=current_price,
            iopv=iopv,
            premium_pct=premium_pct,
            action=action,
            note=note,
        )

    def get_provider_name(self) -> str:
        return "akshare"

    def supports_live_data(self) -> bool:
        return True

    def get_capability_notes(self) -> list[str]:
        return [
            "指数估值与回测基于 AkShare 实时/历史数据",
            "A股面板优先真实数据，其余市场首版为实验性占位",
            "若接口缺失或不稳定，会明确报错而不是回退到 mock",
        ]

    def get_market_source_note(self, market: str) -> str:
        if market == "A股":
            return "A股使用 AkShare + 乐咕乐股指数估值数据"
        return f"{market} 暂为实验性占位口径"

    def is_experimental_market(self, market: str) -> bool:
        return market != "A股"

    def get_streamlit_sidebar_note(self) -> str:
        return "AkShare provider 会拉取真实数据；接口波动时会直接提示错误。"

    def get_streamlit_provider_badge(self) -> str:
        return "AKSHARE"

    def get_streamlit_live_data_warning(self) -> str:
        return "真实行情与估值接口可能波动，不支持时会直接报错。"

    def save_allocation_chart(self, output_path: Path) -> Path:
        return super().save_allocation_chart(output_path)

    def _get_index_meta(self, index_code: str) -> dict[str, str]:
        return SUPPORTED_INDEXES.get(index_code, SUPPORTED_INDEXES[DEFAULT_INDEX])

    def _get_lg_symbol(self, index_code: str) -> str:
        symbol = self._LG_SYMBOLS.get(index_code)
        if symbol is None:
            raise RuntimeError(f"AkShare 暂不支持指数 {index_code} 的乐咕乐股估值映射")
        return symbol

    def _find_index_code_by_etf(self, symbol: str) -> str:
        for index_code, meta in SUPPORTED_INDEXES.items():
            if meta["etf"] == symbol:
                return index_code
        raise RuntimeError(f"未找到 ETF {symbol} 对应的指数映射")

    def _find_index_code_by_lg_symbol(self, symbol: str) -> str:
        for index_code, lg_symbol in self._LG_SYMBOLS.items():
            if lg_symbol == symbol:
                return index_code
        raise RuntimeError(f"未找到乐咕乐股符号 {symbol} 对应的指数映射")

    @lru_cache(maxsize=16)
    def _get_index_pe_frame(self, index_code: str) -> pd.DataFrame:
        try:
            frame = self._ak.stock_index_pe_lg(symbol=self._get_lg_symbol(index_code))
        except Exception as error:
            raise RuntimeError(f"AkShare 无法获取 {index_code} 的指数 PE 数据: {error}") from error
        if frame.empty:
            raise RuntimeError(f"AkShare 返回了空的 {index_code} 指数 PE 数据")
        return frame.copy()

    @lru_cache(maxsize=16)
    def _get_index_pb_frame(self, index_code: str) -> pd.DataFrame:
        try:
            frame = self._ak.stock_index_pb_lg(symbol=self._get_lg_symbol(index_code))
        except Exception as error:
            raise RuntimeError(f"AkShare 无法获取 {index_code} 的指数 PB 数据: {error}") from error
        if frame.empty:
            raise RuntimeError(f"AkShare 返回了空的 {index_code} 指数 PB 数据")
        return frame.copy()

    @lru_cache(maxsize=16)
    def _get_index_daily_frame(self, index_code: str) -> pd.DataFrame:
        symbol = self._get_index_meta(index_code)["akshare_symbol"]
        try:
            frame = self._ak.stock_zh_index_daily_em(symbol=symbol)
        except Exception as error:
            raise RuntimeError(f"AkShare 无法获取 {index_code} 的指数历史行情: {error}") from error
        if frame.empty:
            raise RuntimeError(f"AkShare 返回了空的 {index_code} 指数历史行情")
        return frame.copy()

    @lru_cache(maxsize=1)
    def _get_etf_spot_frame(self) -> pd.DataFrame:
        try:
            frame = self._ak.fund_etf_spot_em()
        except Exception as error:
            raise RuntimeError(f"AkShare 无法获取 ETF 实时行情: {error}") from error
        if frame.empty:
            raise RuntimeError("AkShare 返回了空的 ETF 实时行情")
        return frame.copy()

    def _get_etf_spot_row(self, symbol: str) -> dict[str, Any]:
        frame = self._get_etf_spot_frame()
        match = frame.loc[frame["代码"].astype(str) == symbol]
        if match.empty:
            raise RuntimeError(f"AkShare ETF 实时行情中找不到代码 {symbol}")
        return match.iloc[0].to_dict()

    def _get_etf_price_series(self, symbol: str, years: int) -> list[float]:
        try:
            frame = self._ak.fund_etf_hist_em(symbol=symbol, period="daily", adjust="qfq")
        except Exception as error:
            raise RuntimeError(f"AkShare 无法获取 ETF {symbol} 历史行情: {error}") from error
        if frame.empty:
            raise RuntimeError(f"AkShare 返回了空的 ETF {symbol} 历史行情")
        trailing = frame.tail(max(years * 252, 2))
        close_column = "收盘"
        if close_column not in trailing.columns:
            raise RuntimeError(f"ETF {symbol} 历史行情缺少 {close_column} 列")
        series = [self._require_float(value, f"ETF {symbol} 历史收盘价缺失") for value in trailing[close_column].tolist()]
        if len(series) < 2:
            raise RuntimeError(f"ETF {symbol} 历史行情样本不足")
        return series

    def _build_constituents(self, index_code: str, latest_pe: pd.Series, latest_pb: pd.Series) -> list[ConstituentMetric]:
        index_meta = self._get_index_meta(index_code)
        equal_weight_pe = self._require_float(latest_pe.get("等权滚动市盈率"), f"{index_meta['name']} 等权滚动市盈率缺失")
        market_pe = self._require_float(latest_pe.get("滚动市盈率"), f"{index_meta['name']} 滚动市盈率缺失")
        pb = self._require_float(latest_pb.get("市净率"), f"{index_meta['name']} 市净率缺失")
        try:
            cons_frame = self._ak.index_stock_cons_weight_csindex(symbol=index_meta["csindex_symbol"])
        except Exception as error:
            raise RuntimeError(f"AkShare 无法获取 {index_meta['name']} 成分股列表: {error}") from error
        if cons_frame.empty:
            raise RuntimeError(f"AkShare 返回了空的 {index_meta['name']} 成分股列表")
        constituents: list[ConstituentMetric] = []
        for row in cons_frame.head(20).to_dict("records"):
            constituents.append(
                ConstituentMetric(
                    code=str(row.get("成分券代码", "")),
                    name=str(row.get("成分券名称", "")),
                    pe_ttm=equal_weight_pe,
                    pb=pb,
                    category=index_meta["category"],
                )
            )
        if not constituents:
            raise RuntimeError(f"{index_meta['name']} 成分股列表为空，无法构建估值样本")
        constituents[0].pe_ttm = market_pe
        return constituents

    def _build_history_points(self, frame: pd.DataFrame, years: int) -> list[HistoricalSeriesPoint]:
        trailing = frame.tail(max(years * 252, 2))
        points: list[HistoricalSeriesPoint] = []
        for row in trailing.to_dict("records"):
            points.append(
                HistoricalSeriesPoint(
                    day=self._coerce_date(row.get("日期")),
                    value=self._require_float(row.get("等权滚动市盈率"), "历史等权滚动市盈率缺失"),
                )
            )
        if len(points) < 2:
            raise RuntimeError(f"历史估值序列不足，无法构建 {years} 年分位")
        return points

    def _latest_percentile_from_frame(self, frame: pd.DataFrame) -> float:
        latest = self._require_float(frame.iloc[-1].get("等权滚动市盈率"), "当前等权滚动市盈率缺失")
        series = [self._require_float(value, "历史等权滚动市盈率缺失") for value in frame["等权滚动市盈率"].tolist()]
        below_or_equal = sum(1 for value in series if value <= latest)
        return round((below_or_equal / len(series)) * 100, 2)

    def _percentile_to_zone(self, percentile: float) -> str:
        if percentile < 10:
            return "diamond"
        if percentile < 20:
            return "golden"
        if percentile > 80:
            return "risk"
        return "normal"

    def _coerce_date(self, value: Any) -> date:
        if isinstance(value, date):
            return value
        timestamp = pd.to_datetime(value, errors="coerce")
        if pd.isna(timestamp):
            raise RuntimeError(f"无法解析日期值: {value}")
        return timestamp.date()

    def _optional_float(self, value: Any) -> float | None:
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        try:
            return round(float(value), 4)
        except (TypeError, ValueError):
            return None

    def _require_float(self, value: Any, message: str) -> float:
        result = self._optional_float(value)
        if result is None:
            raise RuntimeError(message)
        return round(result, 2)
