from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from etf150.models import HistoricalSeriesPoint


def coerce_date(value: Any) -> date:
    """Convert provider date values to ``date``."""
    if isinstance(value, date):
        return value
    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        raise RuntimeError(f"无法解析日期值: {value}")
    return timestamp.date()


def optional_float(value: Any) -> float | None:
    """Convert provider numeric values to floats when possible."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return round(float(value), 4)
    except (TypeError, ValueError):
        return None


def require_float(value: Any, message: str) -> float:
    """Convert provider numeric values or raise a provider-facing error."""
    result = optional_float(value)
    if result is None:
        raise RuntimeError(message)
    return round(result, 2)


def find_column(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str:
    """Find the first available column from a list of candidates."""
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    raise RuntimeError(f"数据缺少列: {', '.join(candidates)}")


def optional_column(frame: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    """Find an optional provider column."""
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    return None


def find_pe_column(frame: pd.DataFrame) -> str:
    """Find a constituent PE column in AkShare frames."""
    preferred_columns = ("市盈率-动态", "市盈率(TTM)", "市盈率TTM", "市盈率-ttm", "PE(TTM)", "PETTM")
    for column in preferred_columns:
        if column in frame.columns:
            return column
    for column in frame.columns:
        normalized = str(column).lower()
        if "ttm" in normalized and ("市盈率" in str(column) or "pe" in normalized):
            return str(column)
    for column in frame.columns:
        normalized = str(column).lower()
        if "市盈率" in str(column) or normalized == "pe":
            return str(column)
    raise RuntimeError("A 股个股 PE 数据缺少市盈率列")


def normalize_stock_code(value: Any) -> str:
    """Normalize provider stock codes to six digits."""
    text = str(value or "").strip()
    digits = "".join(char for char in text if char.isdigit())
    if len(digits) >= 6:
        return digits[-6:]
    return digits


def frame_to_points(
    frame: pd.DataFrame,
    date_columns: tuple[str, ...],
    value_columns: tuple[str, ...],
) -> list[HistoricalSeriesPoint]:
    """Convert a provider frame to dated numeric points."""
    value_column = find_column(frame, value_columns)
    date_column = optional_column(frame, date_columns)
    points: list[HistoricalSeriesPoint] = []
    for index, row in enumerate(frame.to_dict("records")):
        day = coerce_date(row.get(date_column)) if date_column else date.fromordinal(date(1970, 1, 1).toordinal() + index)
        points.append(
            HistoricalSeriesPoint(
                day=day,
                value=require_float(row.get(value_column), f"{value_column} 缺失"),
            )
        )
    if len(points) < 2:
        raise RuntimeError("历史序列样本不足")
    return points
