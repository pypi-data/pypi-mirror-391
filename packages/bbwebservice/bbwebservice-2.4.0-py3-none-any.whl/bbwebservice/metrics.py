from __future__ import annotations

from threading import Lock
from typing import Mapping

_TIMEOUT_COUNTERS: dict[str, int] = {
    'header': 0,
    'body': 0,
    'handler': 0,
}
_COUNTER_LOCK = Lock()


def record_timeout(kind: str) -> None:
    """Increment the timeout counter for ``kind`` if it is tracked."""
    normalized = kind.lower()
    with _COUNTER_LOCK:
        if normalized not in _TIMEOUT_COUNTERS:
            _TIMEOUT_COUNTERS[normalized] = 0
        _TIMEOUT_COUNTERS[normalized] += 1


def get_timeout_metrics() -> dict[str, int]:
    """Return a snapshot suitable for JSON serialization."""
    with _COUNTER_LOCK:
        return {f'timeouts.{key}': value for key, value in _TIMEOUT_COUNTERS.items()}


def reset_timeout_metrics(initial: Mapping[str, int] | None = None) -> None:
    """Reset all timeout counters (mainly useful for tests)."""
    with _COUNTER_LOCK:
        if initial:
            _TIMEOUT_COUNTERS.clear()
            for key, value in initial.items():
                _TIMEOUT_COUNTERS[key.lower()] = int(value)
        else:
            for key in list(_TIMEOUT_COUNTERS.keys()):
                _TIMEOUT_COUNTERS[key] = 0
