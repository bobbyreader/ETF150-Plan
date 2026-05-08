from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def to_serializable(value: Any) -> Any:
    """Convert dataclass-rich values into JSON serializable data."""
    if is_dataclass(value):
        return {key: to_serializable(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: to_serializable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_serializable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def render_json(value: Any) -> str:
    """Render any supported value as pretty JSON."""
    return json.dumps(to_serializable(value), ensure_ascii=False, indent=2)
