from __future__ import annotations

import argparse
from typing import Any

from etf150.data.providers.akshare_provider import AkshareDataProvider
from etf150.data.providers.base import DataProvider
from etf150.data.providers.mock import MockDataProvider
from etf150.reporting.console import render_json
from etf150.services import get_allocation, get_backtest, get_entry_backtest, get_iopv, get_panel, get_signal, get_sip, get_valuation


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

    entry_backtest_parser = subparsers.add_parser("entry-backtest")
    entry_backtest_parser.add_argument("--provider", default="mock")
    entry_backtest_parser.add_argument("--index", required=True)
    entry_backtest_parser.add_argument("--holding-days", type=int, default=252)
    entry_backtest_parser.add_argument("--history-years", type=int, choices=[3, 5, 10], default=10)

    iopv_parser = subparsers.add_parser("iopv")
    iopv_parser.add_argument("--provider", default="mock")
    iopv_parser.add_argument("--symbol", required=True)

    return parser


def handle_valuation(provider: DataProvider, index_code: str) -> dict[str, Any]:
    """Handle valuation command."""
    return get_valuation(provider, index_code)


def handle_signal(provider: DataProvider, args: argparse.Namespace) -> dict[str, Any]:
    """Handle signal command."""
    return get_signal(
        provider=provider,
        index_code=args.index,
        category=args.category,
        capital=args.capital,
        rotation_from=args.rotation_from,
        rotation_from_percentile=args.rotation_from_percentile,
        rotation_to=args.rotation_to,
        rotation_to_percentile=args.rotation_to_percentile,
    )


def handle_panel(provider: DataProvider) -> dict[str, Any]:
    """Handle panel command."""
    return get_panel(provider)


def handle_allocation(provider: DataProvider, output: str) -> dict[str, Any]:
    """Handle allocation command."""
    return get_allocation(provider, output)


def handle_sip(provider: DataProvider, units: int) -> dict[str, Any]:
    """Handle SIP command."""
    return get_sip(provider, units)


def handle_backtest(provider: DataProvider, index_code: str, years: int) -> dict[str, Any]:
    """Handle backtest command."""
    return get_backtest(provider, index_code, years)


def handle_entry_backtest(provider: DataProvider, index_code: str, holding_days: int, history_years: int = 10) -> dict[str, Any]:
    """Handle valuation-entry backtest command."""
    return get_entry_backtest(provider, index_code, holding_days, history_years)


def handle_iopv(provider: DataProvider, symbol: str) -> dict[str, Any]:
    """Handle IOPV command."""
    return get_iopv(provider, symbol)


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
    elif args.command == "entry-backtest":
        result = handle_entry_backtest(provider, args.index, args.holding_days, args.history_years)
    elif args.command == "iopv":
        result = handle_iopv(provider, args.symbol)
    else:
        raise ValueError(f"unsupported command: {args.command}")

    print(render_json(result))


if __name__ == "__main__":
    main()
