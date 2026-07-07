from __future__ import annotations

import logging

from app.config import settings
from app.pipeline import (
    cluster,
    dedupe,
    embed,
    fetch_all,
)

log = logging.getLogger("parakh.pipeline")


def run_ingest_cycle() -> dict[str, int]:
    """
    One ingestion cycle (design: cron every 10 min). Wires the stages together;
    the bodies are M0 stubs so this is a no-op that proves the seam.
    """
    raw = fetch_all(rss_urls=[])
    deduped = dedupe(raw)
    embedded = embed(deduped)
    clusters = cluster(embedded)
    log.info("ingest cycle: %d raw -> %d deduped -> %d clusters",
             len(raw), len(deduped), len(clusters))
    return {"raw": len(raw), "deduped": len(deduped), "clusters": len(clusters)}


def build_scheduler():
    """Return a configured APScheduler; imported lazily so `import app.main` stays light."""
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        run_ingest_cycle,
        "interval",
        minutes=settings.fetch_interval_minutes,
        id="ingest",
        max_instances=1,
        coalesce=True,
    )
    return scheduler
