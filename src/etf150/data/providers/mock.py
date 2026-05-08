from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from etf150.models import AllocationSlice, ConstituentMetric, HistoricalSeriesPoint, IndexSnapshot, PanelEntry
from etf150.reporting.charts import save_allocation_chart


class MockDataProvider:
    """In-memory data provider for development and tests."""

    def get_index_snapshot(self, index_code: str) -> IndexSnapshot:
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
            ConstituentMetric(code="000001", name="A", pe_ttm=12.0, pb=1.5, category="broad"),
            ConstituentMetric(code="000002", name="B", pe_ttm=14.0, pb=1.8, category="broad"),
            ConstituentMetric(code="000003", name="C", pe_ttm=18.0, pb=2.1, category="broad"),
            ConstituentMetric(code="000004", name="D", pe_ttm=-3.0, pb=1.2, category="broad"),
            ConstituentMetric(code="000005", name="E", pe_ttm=188.0, pb=5.0, category="broad"),
        ]
        return IndexSnapshot(
            code=index_code,
            name=index_code.upper(),
            category="broad",
            market_pe=15.2,
            market_pb=1.85,
            current_price=3.98,
            iopv=4.00,
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

    def get_iopv_snapshot(self, symbol: str) -> tuple[float, float]:
        mapping = {
            "510300": (4.02, 4.00),
            "159915": (2.50, 2.53),
        }
        return mapping.get(symbol, (3.98, 4.00))
