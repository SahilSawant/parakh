from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.ingest import run_ingest_cycle

logging.basicConfig(level=logging.INFO)

_scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler
    # Scheduler is opt-in so imports/tests/CI don't spawn background jobs.
    if _run_scheduler_enabled():
        from app.scheduler import build_scheduler

        _scheduler = build_scheduler()
        _scheduler.start()
    yield
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)


def _run_scheduler_enabled() -> bool:
    import os

    return os.environ.get("PARAKH_ENABLE_SCHEDULER", "0") == "1"


app = FastAPI(title="Parakh ingestion worker", version="0.0.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "embedding_model": settings.embedding_model,
        "fetch_interval_minutes": settings.fetch_interval_minutes,
    }


@app.post("/ingest/run")
def ingest_run(dry_run: bool = False, source: str | None = None) -> dict[str, object]:
    """Trigger a single ingestion cycle on demand. dry_run skips DB writes."""
    return run_ingest_cycle(only_slug=source, dry_run=dry_run)
