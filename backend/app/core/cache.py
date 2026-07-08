"""进程内 TTL 缓存（BI 热点查询等）。"""

import time
from collections.abc import Callable
from threading import Lock
from typing import TypeVar

T = TypeVar("T")

_lock = Lock()
_store: dict[str, tuple[float, object]] = {}


def cache_get(key: str, ttl: float) -> object | None:
    now = time.monotonic()
    with _lock:
        entry = _store.get(key)
        if entry is None:
            return None
        ts, value = entry
        if now - ts >= ttl:
            del _store[key]
            return None
        return value


def cache_set(key: str, value: object) -> None:
    with _lock:
        _store[key] = (time.monotonic(), value)


def cache_invalidate(prefix: str | None = None) -> int:
    with _lock:
        if prefix is None:
            count = len(_store)
            _store.clear()
            return count
        keys = [k for k in _store if k.startswith(prefix)]
        for k in keys:
            del _store[k]
        return len(keys)


def cached_call(key: str, ttl: float, fn: Callable[[], T]) -> T:
    hit = cache_get(key, ttl)
    if hit is not None:
        return hit  # type: ignore[return-value]
    value = fn()
    cache_set(key, value)
    return value
