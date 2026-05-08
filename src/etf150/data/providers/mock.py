from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from etf150.config import DEFAULT_BACKTEST_YEARS, DEFAULT_CATEGORY, DEFAULT_ETF_SYMBOL, DEFAULT_INDEX, DEFAULT_PROVIDER, DEFAULT_ROTATION_FROM, DEFAULT_ROTATION_FROM_PERCENTILE, DEFAULT_ROTATION_TO, DEFAULT_ROTATION_TO_PERCENTILE, DEFAULT_SIP_UNITS, DEFAULT_TOTAL_CAPITAL, SUPPORTED_INDEXES
from etf150.models import AllocationSlice, ConstituentMetric, HistoricalSeriesPoint, IOPVSnapshot, IndexSnapshot, PanelEntry
from etf150.reporting.charts import build_allocation_figure, save_allocation_chart


class MockDataProvider:
    """In-memory data provider for development and tests."""

    def get_index_snapshot(self, index_code: str) -> IndexSnapshot:
        index_meta = self.get_supported_indexes().get(index_code, self.get_supported_indexes()[DEFAULT_INDEX])
        symbol = index_meta["etf"]
        iopv_snapshot = self.get_iopv_snapshot(symbol)
        today = date(2026, 5, 8)
        history_5y = [
            HistoricalSeriesPoint(day=today - timedelta(days=index), value=value)
            for index, value in enumerate([9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
        ]
        history_10y = [
            HistoricalSeriesPoint(day=today - timedelta(days=index), value=value)
            for index, value in enumerate([8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21])
        ]
        constituents = [
            ConstituentMetric(code="000001", name="A", pe_ttm=12.0, pb=1.5, category=index_meta["category"]),
            ConstituentMetric(code="000002", name="B", pe_ttm=14.0, pb=1.8, category=index_meta["category"]),
            ConstituentMetric(code="000003", name="C", pe_ttm=18.0, pb=2.1, category=index_meta["category"]),
            ConstituentMetric(code="000004", name="D", pe_ttm=-3.0, pb=1.2, category=index_meta["category"]),
            ConstituentMetric(code="000005", name="E", pe_ttm=188.0, pb=5.0, category=index_meta["category"]),
        ]
        return IndexSnapshot(
            code=index_code,
            name=index_meta["name"],
            category=index_meta["category"],
            market_pe=15.2,
            market_pb=1.85,
            current_price=iopv_snapshot.current_price,
            iopv=iopv_snapshot.iopv,
            constituents=constituents,
            history_5y=history_5y,
            history_10y=history_10y,
        )

    def get_panel_entries(self) -> list[PanelEntry]:
        return [
            PanelEntry(market="A股", percentile=18.0, zone="golden", note="估值偏低"),
            PanelEntry(market="港股", percentile=12.0, zone="golden", note="价值修复区"),
            PanelEntry(market="美股", percentile=82.0, zone="risk", note="估值偏高"),
            PanelEntry(market="德国", percentile=46.0, zone="normal", note="中性"),
            PanelEntry(market="黄金", percentile=65.0, zone="normal", note="防守配置"),
            PanelEntry(market="原油", percentile=28.0, zone="normal", note="波动较大"),
        ]

    def get_allocation_slices(self) -> list[AllocationSlice]:
        return [
            AllocationSlice(name="大盘权益", weight=30),
            AllocationSlice(name="中小盘", weight=20),
            AllocationSlice(name="行业", weight=10),
            AllocationSlice(name="固收", weight=20),
            AllocationSlice(name="海外", weight=10),
            AllocationSlice(name="商品", weight=10),
        ]

    def get_backtest_series(self, index_code: str, years: int) -> list[float]:
        base = {
            3: [100, 102, 110, 95, 120, 135],
            5: [100, 92, 105, 98, 126, 150],
            10: [100, 85, 90, 108, 125, 160],
        }
        return base.get(years, [100, 110])

    def save_allocation_chart(self, output_path: Path) -> Path:
        return save_allocation_chart(self.get_allocation_slices(), output_path)

    def get_sip_suggestion(self, units: int) -> str:
        return f"月初定投建议：投入 {units} 份。"

    def get_iopv_snapshot(self, symbol: str) -> IOPVSnapshot:
        mapping = {
            "510300": (4.02, 4.00),
            "159915": (2.50, 2.53),
            "510500": (5.86, 5.80),
            "515180": (1.32, 1.30),
        }
        current_price, iopv = mapping.get(symbol, (3.98, 4.00))
        premium_pct = round(((current_price / iopv) - 1) * 100, 2) if iopv else None
        action = "wait" if iopv and current_price > iopv else "buy_ok"
        note = f"现价 {current_price:.2f} 高于 IOPV {iopv:.2f}，暂不买入" if action == "wait" else "现价未高于IOPV，可按计划执行"
        return IOPVSnapshot(
            symbol=symbol,
            current_price=current_price,
            iopv=iopv,
            premium_pct=premium_pct,
            action=action,
            note=note,
        )

    def get_supported_indexes(self) -> dict[str, dict[str, str]]:
        return SUPPORTED_INDEXES

    def get_supported_symbols(self) -> list[str]:
        return [item["etf"] for item in self.get_supported_indexes().values()]

    def get_provider_name(self) -> str:
        return DEFAULT_PROVIDER

    def supports_live_data(self) -> bool:
        return False

    def get_backtest_year_options(self) -> list[int]:
        return [3, 5, 10]

    def get_default_rotation_pair(self) -> tuple[str, float, str, float]:
        return (
            DEFAULT_ROTATION_FROM,
            DEFAULT_ROTATION_FROM_PERCENTILE,
            DEFAULT_ROTATION_TO,
            DEFAULT_ROTATION_TO_PERCENTILE,
        )

    def get_supported_categories(self) -> list[str]:
        return sorted({item["category"] for item in self.get_supported_indexes().values()})

    def get_capability_notes(self) -> list[str]:
        return ["内置演示数据", "适合离线测试", "不代表真实市场行情"]

    def get_allocation_figure(self):
        return build_allocation_figure(self.get_allocation_slices())

    def get_price_series(self, symbol: str, years: int) -> list[float]:
        return self.get_backtest_series(symbol, years)

    def get_index_display_name(self, index_code: str) -> str:
        return self.get_supported_indexes().get(index_code, self.get_supported_indexes()[DEFAULT_INDEX])["name"]

    def get_index_category(self, index_code: str) -> str:
        return self.get_supported_indexes().get(index_code, self.get_supported_indexes()[DEFAULT_INDEX])["category"]

    def resolve_etf_symbol(self, index_code: str) -> str:
        return self.get_supported_indexes().get(index_code, self.get_supported_indexes()[DEFAULT_INDEX])["etf"]

    def get_market_source_note(self, market: str) -> str:
        return f"{market} 使用 mock 数据"

    def is_experimental_market(self, market: str) -> bool:
        return market != "A股"

    def get_streamlit_title(self) -> str:
        return "ETF150 决策助手"

    def get_streamlit_description(self) -> str:
        return "基于150份计划的估值、信号、面板、回测与IOPV演示。"

    def get_streamlit_sidebar_note(self) -> str:
        return "Mock provider 适合本地演示与测试。"

    def get_streamlit_default_index(self) -> str:
        return DEFAULT_INDEX

    def get_streamlit_default_symbol(self) -> str:
        return DEFAULT_ETF_SYMBOL

    def get_streamlit_default_capital(self) -> float:
        return DEFAULT_TOTAL_CAPITAL

    def get_streamlit_default_sip_units(self) -> int:
        return DEFAULT_SIP_UNITS

    def get_streamlit_default_backtest_years(self) -> int:
        return DEFAULT_BACKTEST_YEARS

    def get_streamlit_default_category(self) -> str:
        return DEFAULT_CATEGORY

    def get_streamlit_provider_badge(self) -> str:
        return "MOCK"

    def get_streamlit_market_warning(self) -> str:
        return "除A股外，其余面板口径仅作演示。"

    def get_streamlit_live_data_warning(self) -> str:
        return "当前为模拟数据，不构成真实行情。"

    def get_streamlit_worst_case_note(self) -> str:
        return "最坏情况要先接受，再执行计划。"

    def get_streamlit_prediction_note(self) -> str:
        return "不预测，只计算。"

    def get_streamlit_supported_index_labels(self) -> dict[str, str]:
        return {code: data["name"] for code, data in self.get_supported_indexes().items()}

    def get_streamlit_supported_symbol_labels(self) -> dict[str, str]:
        return {data["etf"]: data["name"] for data in self.get_supported_indexes().values()}

    def get_streamlit_default_rotation_inputs(self) -> tuple[str, float, str, float]:
        return self.get_default_rotation_pair()

    def get_streamlit_footer_note(self) -> str:
        return "仅作策略演示，请勿替代独立判断。"
