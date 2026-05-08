from __future__ import annotations

from pathlib import Path
from typing import Protocol

from etf150.models import AllocationSlice, IndexSnapshot, PanelEntry


class DataProvider(Protocol):
    def get_index_snapshot(self, index_code: str) -> IndexSnapshot:
        """Return a current index snapshot with constituents and history."""

    def get_panel_entries(self) -> list[PanelEntry]:
        """Return multi-market percentile panel entries."""

    def get_allocation_slices(self) -> list[AllocationSlice]:
        """Return asset allocation slices."""

    def get_backtest_series(self, index_code: str, years: int) -> list[float]:
        """Return price-like historical series for backtest."""

    def save_allocation_chart(self, output_path: Path) -> Path:
        """Create an allocation chart and return the output path."""

    def get_sip_suggestion(self, units: int) -> str:
        """Return SIP monthly suggestion."""

    def get_iopv_snapshot(self, symbol: str) -> tuple[float, float]:
        """Return current price and IOPV."""
