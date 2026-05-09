from __future__ import annotations

from pathlib import Path
from typing import Protocol

from etf150.models import AllocationSlice, HistoricalSeriesPoint, IOPVSnapshot, IndexSnapshot, PanelEntry


class DataProvider(Protocol):
    def get_index_snapshot(self, index_code: str) -> IndexSnapshot:
        """Return a current index snapshot with constituents and history."""

    def get_panel_entries(self) -> list[PanelEntry]:
        """Return multi-market percentile panel entries."""

    def get_allocation_slices(self) -> list[AllocationSlice]:
        """Return asset allocation slices."""

    def get_backtest_series(self, index_code: str, years: int) -> list[float]:
        """Return price-like historical series for backtest."""

    def get_backtest_points(self, index_code: str, years: int) -> list[HistoricalSeriesPoint]:
        """Return dated price-like historical points for entry backtests."""

    def get_valuation_history(self, index_code: str, years: int) -> list[HistoricalSeriesPoint]:
        """Return dated valuation history points."""

    def save_allocation_chart(self, output_path: Path) -> Path:
        """Create an allocation chart and return the output path."""

    def get_sip_suggestion(self, units: int) -> str:
        """Return SIP monthly suggestion."""

    def get_iopv_snapshot(self, symbol: str) -> IOPVSnapshot:
        """Return current price and IOPV style snapshot."""

    def get_supported_indexes(self) -> dict[str, dict[str, str]]:
        """Return configured supported indexes."""

    def get_supported_symbols(self) -> list[str]:
        """Return known ETF symbols."""

    def get_provider_name(self) -> str:
        """Return provider display name."""

    def supports_live_data(self) -> bool:
        """Return whether the provider serves live market data."""

    def get_backtest_year_options(self) -> list[int]:
        """Return supported backtest holding year options."""

    def get_default_rotation_pair(self) -> tuple[str, float, str, float]:
        """Return the default rotation comparison pair."""

    def get_supported_categories(self) -> list[str]:
        """Return supported strategy categories."""

    def get_capability_notes(self) -> list[str]:
        """Return provider capability notes for UI and CLI display."""

    def get_allocation_figure(self):
        """Return a matplotlib figure for allocation display."""

    def get_price_series(self, symbol: str, years: int) -> list[float]:
        """Return a price series for visualization if available."""

    def get_index_display_name(self, index_code: str) -> str:
        """Return a human-friendly index name."""

    def get_index_category(self, index_code: str) -> str:
        """Return the default category for an index."""

    def resolve_etf_symbol(self, index_code: str) -> str:
        """Resolve an ETF symbol for an index code."""

    def get_market_source_note(self, market: str) -> str:
        """Return a source note for a market panel row."""

    def is_experimental_market(self, market: str) -> bool:
        """Return whether a market panel row is approximate or experimental."""

    def get_streamlit_title(self) -> str:
        """Return a Streamlit app title for this provider."""

    def get_streamlit_description(self) -> str:
        """Return a Streamlit app description for this provider."""

    def get_streamlit_sidebar_note(self) -> str:
        """Return a Streamlit sidebar note for this provider."""

    def get_streamlit_default_index(self) -> str:
        """Return the default UI index code."""

    def get_streamlit_default_symbol(self) -> str:
        """Return the default UI ETF symbol."""

    def get_streamlit_default_capital(self) -> float:
        """Return the default UI capital value."""

    def get_streamlit_default_sip_units(self) -> int:
        """Return the default UI SIP units."""

    def get_streamlit_default_backtest_years(self) -> int:
        """Return the default UI backtest years."""

    def get_streamlit_default_category(self) -> str:
        """Return the default UI category."""

    def get_streamlit_provider_badge(self) -> str:
        """Return a provider badge string."""

    def get_streamlit_market_warning(self) -> str:
        """Return a market caveat string."""

    def get_streamlit_live_data_warning(self) -> str:
        """Return a live-data caveat string."""

    def get_streamlit_worst_case_note(self) -> str:
        """Return a global risk reminder."""

    def get_streamlit_prediction_note(self) -> str:
        """Return a no-prediction reminder."""

    def get_streamlit_supported_index_labels(self) -> dict[str, str]:
        """Return UI labels for supported indexes."""

    def get_streamlit_supported_symbol_labels(self) -> dict[str, str]:
        """Return UI labels for known symbols."""

    def get_streamlit_default_rotation_inputs(self) -> tuple[str, float, str, float]:
        """Return default UI rotation inputs."""

    def get_streamlit_footer_note(self) -> str:
        """Return a footer note for the Streamlit app."""
