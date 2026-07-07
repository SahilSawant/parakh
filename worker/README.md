# Parakh — ingestion / ML worker

Python (FastAPI + APScheduler). Containerized target: Fly.io / Railway.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"          # add ".[ml]" once the M1 embedding spike starts
uvicorn app.main:app --reload    # http://localhost:8000/health

# Run one ingest cycle on demand
curl -X POST localhost:8000/ingest/run

# Enable the 10-min scheduler
PARAKH_ENABLE_SCHEDULER=1 uvicorn app.main:app
```

## Status (M0)

The pipeline **seam** is wired end to end (`fetch → dedupe → lang → embed → cluster
→ story_update`) with stubbed bodies, so orchestration, config, and the API are
testable now. Heavy ML deps (`sentence-transformers`, `psycopg`, `pgvector`,
`datasketch`, `lingua`) live under the `ml` extra and land in **M1**, alongside:

- feedparser fetch over each source's `rss_urls`, respecting `crawl_policy`
- MinHash/SimHash near-dup detection
- `multilingual-e5-large` embeddings + the Hindi↔English clustering spike
- incremental pgvector-cosine clustering vs the last 72h (sim ≈ 0.82)
- per-story stats, blindspot flags, and Claude Haiku titles/summaries

All tunable knobs (thresholds, intervals, model id) are in `app/config.py`.
