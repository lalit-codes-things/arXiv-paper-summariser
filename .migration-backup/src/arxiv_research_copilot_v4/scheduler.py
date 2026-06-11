"""Scheduling logic for autonomous daily paper monitoring."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import datetime, time as datetime_time, timedelta, timezone

from .models import DailyDigest
from .monitoring import DailyMonitoringWorkflow


class DailyScheduler:
    """Lightweight non-blocking scheduler helper for daily monitoring jobs."""

    def __init__(self, workflow: DailyMonitoringWorkflow, *, run_at: datetime_time = datetime_time(hour=8, minute=0, tzinfo=timezone.utc)) -> None:
        self.workflow = workflow
        self.run_at = run_at

    def next_run_after(self, now: datetime | None = None) -> datetime:
        """Return the next scheduled run time."""

        now = now or datetime.now(timezone.utc)
        candidate = datetime.combine(now.date(), self.run_at, tzinfo=self.run_at.tzinfo or timezone.utc)
        if candidate <= now:
            candidate += timedelta(days=1)
        return candidate

    def run_once(self, **kwargs: object) -> DailyDigest:
        """Run the workflow immediately."""

        return self.workflow.run(**kwargs)

    def run_forever(self, *, sleep: Callable[[float], None] = time.sleep, **kwargs: object) -> None:
        """Run monitoring every day at the configured time."""

        while True:
            seconds = max(0.0, (self.next_run_after() - datetime.now(timezone.utc)).total_seconds())
            sleep(seconds)
            self.workflow.run(**kwargs)
