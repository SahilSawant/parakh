# Parakh — ingestion / ML worker

Python (FastAPI + APScheduler). Containerized target: Fly.io / Railway.

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"          # add ".[ml]" once the embedding spike starts

# Validate the LIVE fetch path against real feeds — no DB needed:
python -m app.ingest --dry-run --show 8

# Full cycle into Postgres (needs DATABASE_URL + applied migrations/seed):
export PARAKH_DATABASE_URL=postgres://postgres:postgres@localhost:5432/parakh
python -m app.ingest                     # all sources
python -m app.ingest --source the-hindu  # one source

# Or via the API:
uvicorn app.main:app --reload            # http://localhost:8000/health
curl -X POST 'localhost:8000/ingest/run?dry_run=true'

# Enable the 10-min scheduler
PARAKH_ENABLE_SCHEDULER=1 uvicorn app.main:app
```

## Status (M1 — live RSS ingestion ✅)

**Live and tested:** `fetch → dedupe → lang → persist`.

- `app/pipeline/fetch.py` — feedparser + httpx over each source's `rss_urls`;
  per-source error isolation (one bad feed never aborts a cycle); `crawl_policy.disabled` honored.
- `app/pipeline/normalize.py` — strip HTML, snippet ≤200 chars (legal constraint),
  image extraction (media:content / thumbnail / enclosure), `published_at` → ISO, language.
- `app/pipeline/dedupe.py` — URL canonicalization (drops tracking params) collapses syndicated copies.
- `app/db.py` — `load_active_sources()` + idempotent `upsert_articles()` (`ON CONFLICT (source_id,url) DO NOTHING`).
- `app/ingest.py` — cycle orchestration + CLI; wired into the scheduler and `/ingest/run`.

Tests: `pytest -m "not integration"` (offline, httpx MockTransport + RSS fixture) and
`pytest -m integration` (against a real Postgres). Both run in CI.

## Next M1 slices (still stubbed)

Embedding + clustering — `app/pipeline/{embed,cluster,story_update}.py` are stubs. Deferred:

- MinHash/SimHash near-dup detection (article-body level)
- `multilingual-e5-large` / `bge-m3` embeddings + the Hindi↔English clustering spike
- incremental pgvector-cosine clustering vs the last 72h (sim ≈ 0.82) + nightly merge/split
- per-story stats, blindspot flags, and Claude Haiku titles/summaries
- the ≥85%-precision clustering eval gate

Tunable knobs (thresholds, intervals, model id) live in `app/config.py`.
