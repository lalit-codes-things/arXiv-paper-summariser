from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings
from app.workers.tasks import run_worker_once


def create_scheduler() -> BackgroundScheduler:
    settings = get_settings()
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        run_worker_once,
        "interval",
        seconds=settings.worker_interval_seconds,
        id="process_research_jobs",
        replace_existing=True,
        max_instances=1,
    )
    return scheduler
