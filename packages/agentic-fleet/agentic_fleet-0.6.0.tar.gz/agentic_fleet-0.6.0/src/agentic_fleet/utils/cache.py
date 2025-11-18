"""
Simple in-memory caching utilities with TTL support.
"""

from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Dict, Generic, Optional, TypeVar


K = TypeVar("K")
V = TypeVar("V")


@dataclass
class _CacheEntry(Generic[V]):
    value: V
    expires_at: float


class TTLCache(Generic[K, V]):
    """A lightweight in-memory cache with time-to-live semantics."""

    def __init__(self, ttl_seconds: float):
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl = float(ttl_seconds)
        self._store: Dict[K, _CacheEntry[V]] = {}

    def get(self, key: K) -> Optional[V]:
        """Retrieve a cached value if it exists and hasn't expired."""

        entry = self._store.get(key)
        if not entry:
            return None
        if entry.expires_at < time.time():
            self._store.pop(key, None)
            return None
        return entry.value

    def set(self, key: K, value: V) -> None:
        """Store a value in the cache."""

        self._store[key] = _CacheEntry(value=value, expires_at=time.time() + self._ttl)

    def clear(self) -> None:
        """Clear all cached entries."""

        self._store.clear()
