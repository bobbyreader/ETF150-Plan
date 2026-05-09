from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Callable

import pandas as pd


class FrameCache:
    """Small disk cache for provider data frames."""

    def __init__(self, cache_dir: Path, ttl_seconds: int = 24 * 60 * 60) -> None:
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds

    def get(self, key: str, loader: Callable[[], pd.DataFrame]) -> pd.DataFrame:
        """Load a frame with stale-cache fallback when the live loader fails."""
        path = self._path_for_key(key)
        try:
            frame = loader()
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            frame.to_pickle(path)
            return frame.copy()
        except Exception:
            cached = self.read_stale(key)
            if cached is not None:
                return cached
            raise

    def read_fresh(self, key: str) -> pd.DataFrame | None:
        """Read a cache entry only if it is still inside the configured TTL."""
        path = self._path_for_key(key)
        if not path.exists() or time.time() - path.stat().st_mtime > self.ttl_seconds:
            return None
        return pd.read_pickle(path).copy()

    def read_stale(self, key: str) -> pd.DataFrame | None:
        """Read a cache entry regardless of age."""
        path = self._path_for_key(key)
        if not path.exists():
            return None
        return pd.read_pickle(path).copy()

    def _path_for_key(self, key: str) -> Path:
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        return self.cache_dir / f"{digest}.pkl"
