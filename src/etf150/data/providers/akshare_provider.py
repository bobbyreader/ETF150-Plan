from __future__ import annotations

from pathlib import Path

from etf150.data.providers.mock import MockDataProvider


class AkshareDataProvider(MockDataProvider):
    """Placeholder provider that keeps the interface stable for future AkShare integration."""

    def __init__(self) -> None:
        try:
            import akshare as ak  # noqa: F401
        except ImportError as error:
            raise RuntimeError("AkShare is not installed") from error

    def save_allocation_chart(self, output_path: Path) -> Path:
        return super().save_allocation_chart(output_path)
