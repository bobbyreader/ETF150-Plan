from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from etf150.backtest.engine import run_backtest
from etf150.data.providers.akshare_provider import AkshareDataProvider
from etf150.data.providers.base import DataProvider
from etf150.data.providers.mock import MockDataProvider
from etf150.reporting.console import render_json
from etf150.strategy.rotation import suggest_rotation
from etf150.strategy.signals import build_signal_report
from etf150.valuation.engine import build_valuation


def get_provider(name: str) -> DataProvider:
    """Build a provider by name."""
    if name == "mock":
        return MockDataProvider()
    if name == "akshare":
        return AkshareDataProvider()
    raise ValueError(f"unsupported provider: {name}")


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser."""
    parser = argparse.ArgumentParser(prog="etf150")
    subparsers = parser.add_subparsers(dest="command", required=True)

    valuation_parser = subparsers.add_parser("valuation")
    valuation_parser.add_argument("--provider", default="mock")
    valuation_parser.add_argument("--index", required=True)

    signal_parser = subparsers.add_parser("signal")
    signal_parser.add_argument("--provider", default="mock")
    signal_parser.add_argument("--index", required=True)
    signal_parser.add_argument("--category", default="broad")
    signal_parser.add_argument("--capital", type=float, default=150000.0)
    signal_parser.add_argument("--rotation-from", default="中证500")
    signal_parser.add_argument("--rotation-from-percentile", type=float, default=65.0)
    signal_parser.add_argument("--rotation-to", default="创业板")
    signal_parser.add_argument("--rotation-to-percentile", type=float, default=25.0)

    panel_parser = subparsers.add_parser("panel")
    panel_parser.add_argument("--provider", default="mock")

    allocation_parser = subparsers.add_parser("allocation")
    allocation_parser.add_argument("--provider", default="mock")
    allocation_parser.add_argument("--output", required=True)

    sip_parser = subparsers.add_parser("sip")
    sip_parser.add_argument("--provider", default="mock")
    sip_parser.add_argument("--units", type=int, default=1)

    backtest_parser = subparsers.add_parser("backtest")
    backtest_parser.add_argument("--provider", default="mock")
    backtest_parser.add_argument("--index", required=True)
    backtest_parser.add_argument("--years", type=int, choices=[3, 5, 10], required=True)

    iopv_parser = subparsers.add_parser("iopv")
    iopv_parser.add_argument("--provider", default="mock")
    iopv_parser.add_argument("--symbol", required=True)

    return parser


def handle_valuation(provider: DataProvider, index_code: str) -> dict[str, Any]:
    """Handle valuation command."""
    snapshot = provider.get_index_snapshot(index_code)
    valuation = build_valuation(snapshot)
    return {"valuation": valuation}


def handle_signal(provider: DataProvider, args: argparse.Namespace) -> dict[str, Any]:
    """Handle signal command."""
    snapshot = provider.get_index_snapshot(args.index)
    valuation = build_valuation(snapshot)
    current_price, iopv = provider.get_iopv_snapshot(snapshot.code if snapshot.code else args.index)
    iopv_warning = None
    if current_price > iopv:
        iopv_warning = f"现价 {current_price:.2f} 高于 IOPV {iopv:.2f}，暂不买入"

    rotation = suggest_rotation(
        args.rotation_from,
        args.rotation_from_percentile,
        args.rotation_to,
        args.rotation_to_percentile,
    )
    report = build_signal_report(
        valuation=valuation,
        total_capital=args.capital,
        category=args.category,
        iopv_warning=iopv_warning,
        rotation=rotation,
    )
    return {"signal": report}


def handle_panel(provider: DataProvider) -> dict[str, Any]:
    """Handle panel command."""
    return {"panel": provider.get_panel_entries()}


def handle_allocation(provider: DataProvider, output: str) -> dict[str, Any]:
    """Handle allocation command."""
    output_path = provider.save_allocation_chart(Path(output))
    return {"allocation": provider.get_allocation_slices(), "chart": output_path}


def handle_sip(provider: DataProvider, units: int) -> dict[str, Any]:
    """Handle SIP command."""
    return {"sip": provider.get_sip_suggestion(units)}


def handle_backtest(provider: DataProvider, index_code: str, years: int) -> dict[str, Any]:
    """Handle backtest command."""
    series = provider.get_backtest_series(index_code, years)
    result = run_backtest(index_code, series, years)
    return {"backtest": result}


def handle_iopv(provider: DataProvider, symbol: str) -> dict[str, Any]:
    """Handle IOPV command."""
    current_price, iopv = provider.get_iopv_snapshot(symbol)
    premium = round(((current_price / iopv) - 1) * 100, 2)
    return {
        "iopv": {
            "symbol": symbol,
            "current_price": current_price,
            "iopv": iopv,
            "premium_pct": premium,
            "action": "wait" if current_price > iopv else "buy_ok",
        }
    }


def main() -> None:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    provider = get_provider(args.provider)

    if args.command == "valuation":
        result = handle_valuation(provider, args.index)
    elif args.command == "signal":
        result = handle_signal(provider, args)
    elif args.command == "panel":
        result = handle_panel(provider)
    elif args.command == "allocation":
        result = handle_allocation(provider, args.output)
    elif args.command == "sip":
        result = handle_sip(provider, args.units)
    elif args.command == "backtest":
        result = handle_backtest(provider, args.index, args.years)
    elif args.command == "iopv":
        result = handle_iopv(provider, args.symbol)
    else:
        raise ValueError(f"unsupported command: {args.command}")

    print(render_json(result))


if __name__ == "__main__":
    main()
