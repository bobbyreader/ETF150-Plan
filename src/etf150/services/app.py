from __future__ import annotations

from pathlib import Path
from typing import Any

from etf150.backtest.engine import run_backtest, run_valuation_entry_backtest
from etf150.data.providers.base import DataProvider
from etf150.strategy.rotation import suggest_rotation
from etf150.strategy.signals import build_signal_report
from etf150.valuation.engine import build_valuation


def get_valuation(provider: DataProvider, index_code: str) -> dict[str, Any]:
    """Build a valuation payload for an index."""
    snapshot = provider.get_index_snapshot(index_code)
    valuation = build_valuation(snapshot)
    return {"valuation": valuation}


def get_signal(
    provider: DataProvider,
    index_code: str,
    category: str,
    capital: float,
    rotation_from: str,
    rotation_from_percentile: float,
    rotation_to: str,
    rotation_to_percentile: float,
) -> dict[str, Any]:
    """Build a signal payload for an index."""
    snapshot = provider.get_index_snapshot(index_code)
    valuation = build_valuation(snapshot)
    iopv_snapshot = provider.get_iopv_snapshot(provider.resolve_etf_symbol(index_code))
    iopv_warning = iopv_snapshot.note if iopv_snapshot.action == "wait" else None
    rotation = suggest_rotation(
        rotation_from,
        rotation_from_percentile,
        rotation_to,
        rotation_to_percentile,
    )
    report = build_signal_report(
        valuation=valuation,
        total_capital=capital,
        category=category,
        iopv_warning=iopv_warning,
        rotation=rotation,
    )
    return {"signal": report}


def get_panel(provider: DataProvider) -> dict[str, Any]:
    """Build a panel payload."""
    return {"panel": provider.get_panel_entries()}


def get_allocation(
    provider: DataProvider,
    output_path: str | Path | None = None,
    include_figure: bool = False,
) -> dict[str, Any]:
    """Build an allocation payload and optionally save a chart."""
    result: dict[str, Any] = {"allocation": provider.get_allocation_slices()}
    if include_figure:
        result["figure"] = provider.get_allocation_figure()
    if output_path is not None:
        result["chart"] = provider.save_allocation_chart(Path(output_path))
    return result


def get_sip(provider: DataProvider, units: int) -> dict[str, Any]:
    """Build a SIP payload."""
    return {"sip": provider.get_sip_suggestion(units)}


def get_backtest(provider: DataProvider, index_code: str, years: int) -> dict[str, Any]:
    """Build a backtest payload."""
    series = provider.get_backtest_series(index_code, years)
    result = run_backtest(index_code, series, years)
    return {"backtest": result}


def get_entry_backtest(provider: DataProvider, index_code: str, holding_days: int, history_years: int = 10) -> dict[str, Any]:
    """Build a valuation-entry backtest payload."""
    price_points = provider.get_backtest_points(index_code, history_years)
    valuation_points = provider.get_valuation_history(index_code, history_years)
    result = run_valuation_entry_backtest(index_code, price_points, valuation_points, holding_days)
    return {"entry_backtest": result}


def get_iopv(provider: DataProvider, symbol: str) -> dict[str, Any]:
    """Build an IOPV payload."""
    snapshot = provider.get_iopv_snapshot(symbol)
    return {
        "iopv": {
            "symbol": snapshot.symbol,
            "current_price": snapshot.current_price,
            "iopv": snapshot.iopv,
            "premium_pct": snapshot.premium_pct,
            "action": snapshot.action,
            "note": snapshot.note,
        }
    }


def get_provider_defaults(provider: DataProvider) -> dict[str, Any]:
    """Build provider defaults for UI consumers."""
    return {
        "provider_name": provider.get_provider_name(),
        "supports_live_data": provider.supports_live_data(),
        "supported_indexes": provider.get_supported_indexes(),
        "supported_symbols": provider.get_supported_symbols(),
        "supported_categories": provider.get_supported_categories(),
        "backtest_year_options": provider.get_backtest_year_options(),
        "default_rotation_pair": provider.get_default_rotation_pair(),
        "default_index": provider.get_streamlit_default_index(),
        "default_symbol": provider.get_streamlit_default_symbol(),
        "default_capital": provider.get_streamlit_default_capital(),
        "default_sip_units": provider.get_streamlit_default_sip_units(),
        "default_backtest_years": provider.get_streamlit_default_backtest_years(),
        "default_category": provider.get_streamlit_default_category(),
    }


def get_streamlit_config(provider: DataProvider) -> dict[str, Any]:
    """Build Streamlit-facing provider configuration."""
    return {
        "title": provider.get_streamlit_title(),
        "description": provider.get_streamlit_description(),
        "sidebar_note": provider.get_streamlit_sidebar_note(),
        "provider_badge": provider.get_streamlit_provider_badge(),
        "market_warning": provider.get_streamlit_market_warning(),
        "live_data_warning": provider.get_streamlit_live_data_warning(),
        "worst_case_note": provider.get_streamlit_worst_case_note(),
        "prediction_note": provider.get_streamlit_prediction_note(),
        "supported_index_labels": provider.get_streamlit_supported_index_labels(),
        "supported_symbol_labels": provider.get_streamlit_supported_symbol_labels(),
        "default_rotation_inputs": provider.get_streamlit_default_rotation_inputs(),
        "footer_note": provider.get_streamlit_footer_note(),
        "capability_notes": provider.get_capability_notes(),
    }
