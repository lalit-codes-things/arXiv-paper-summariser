"""Logging helpers."""

from __future__ import annotations

import logging


def configure_logging(level: int | str = logging.INFO) -> None:
    """Configure package-wide logging once with a compact format."""

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
