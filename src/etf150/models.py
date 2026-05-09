from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any


@dataclass(slots=True)
class ConstituentMetric:
    code: str
    name: str
    pe_ttm: float
    pb: float
    category: str = ""


@dataclass(slots=True)
class HistoricalSeriesPoint:
    day: date
    value: float


@dataclass(slots=True)
class IndexSnapshot:
    code: str
    name: str
    category: str
    market_pe: float
    market_pb: float
    current_price: float | None = None
    iopv: float | None = None
    constituents: list[ConstituentMetric] = field(default_factory=list)
    history_5y: list[HistoricalSeriesPoint] = field(default_factory=list)
    history_10y: list[HistoricalSeriesPoint] = field(default_factory=list)


@dataclass(slots=True)
class ValuationResult:
    index_code: str
    index_name: str
    equal_weight_pe_mean: float
    equal_weight_pe_median: float
    valid_sample_size: int
    current_pb: float
    percentile_5y: float
    percentile_10y: float
    valuation_zone: str
    market_pb_zone: str
    is_risk_zone: bool
    is_actionable: bool = True
    uses_proxy_samples: bool = False
    data_quality_note: str = ""


@dataclass(slots=True)
class PositionSuggestion:
    target_equity_pct: float
    current_percentile: float
    rationale: str


@dataclass(slots=True)
class UnitSuggestion:
    total_capital: float
    total_units: int
    unit_amount: float
    suggested_units: int
    suggested_amount: float
    rationale: str


@dataclass(slots=True)
class RotationSuggestion:
    should_rotate: bool
    from_asset: str | None
    to_asset: str | None
    rationale: str


@dataclass(slots=True)
class SignalReport:
    signal: str
    valuation: ValuationResult
    position: PositionSuggestion
    units: UnitSuggestion
    max_drawdown_range: str
    iopv_warning: str | None
    rotation: RotationSuggestion | None
    worst_case_message: str


@dataclass(slots=True)
class BacktestResult:
    index_code: str
    holding_years: int
    start_value: float
    end_value: float
    annualized_return_pct: float
    cumulative_return_pct: float
    max_drawdown_pct: float


@dataclass(slots=True)
class EntryBacktestBucket:
    bucket: str
    label: str
    percentile_min: float
    percentile_max: float
    sample_size: int
    average_return_pct: float | None
    median_return_pct: float | None
    best_return_pct: float | None
    worst_return_pct: float | None


@dataclass(slots=True)
class EntryBacktestResult:
    index_code: str
    holding_days: int
    entries: list[EntryBacktestBucket]


@dataclass(slots=True)
class AllocationSlice:
    name: str
    weight: float


@dataclass(slots=True)
class PanelEntry:
    market: str
    percentile: float
    zone: str
    note: str


@dataclass(slots=True)
class IOPVSnapshot:
    symbol: str
    current_price: float
    iopv: float | None
    premium_pct: float | None
    action: str
    note: str


JSONValue = dict[str, Any] | list[Any] | str | int | float | bool | None
