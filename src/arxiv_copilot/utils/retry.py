"""Retry and backoff utilities."""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")
LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RetryConfig:
    attempts: int = 3
    initial_delay: float = 0.5
    max_delay: float = 8.0
    multiplier: float = 2.0
    jitter: float = 0.1


def retry(operation: Callable[[], T], config: RetryConfig | None = None, *, label: str = "operation") -> T:
    """Run an operation with exponential backoff and jitter."""

    cfg = config or RetryConfig()
    if cfg.attempts < 1:
        raise ValueError("Retry attempts must be at least 1")

    delay = cfg.initial_delay
    last_error: Exception | None = None
    for attempt in range(1, cfg.attempts + 1):
        try:
            return operation()
        except Exception as exc:  # noqa: BLE001 - retry wrapper must be generic.
            last_error = exc
            if attempt == cfg.attempts:
                LOGGER.exception("%s failed after %s attempts", label, attempt)
                break
            sleep_for = min(delay, cfg.max_delay)
            if cfg.jitter:
                sleep_for += random.uniform(0, cfg.jitter)
            LOGGER.warning("%s failed on attempt %s/%s: %s; retrying in %.2fs", label, attempt, cfg.attempts, exc, sleep_for)
            time.sleep(sleep_for)
            delay *= cfg.multiplier

    assert last_error is not None
    raise last_error
