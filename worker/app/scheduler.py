from __future__ import annotations

import logging

from app.config import settings
from app.ingest import run_ingest_cycle

log = logging.getLogger("parakh.scheduler")


def build_scheduler():
    """Return a configured APScheduler; imported lazily so `import app.main` stays light."""
    from apscheduler.schedulers.background import BackgroundScheduler

    def _job() -> None:
        try:
            run_ingest_cycle()
        except Exception:
            log.exception("ingest cycle failed")

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        _job,
        "interval",
        minutes=settings.fetch_interval_minutes,
        id="ingest",
        max_instances=1,
        coalesce=True,
    )
    return scheduler
