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

# Embed + cluster the ingested articles (loads the ML model; needs .[ml] + DB)
pip install -e ".[ml]"
python -m app.ingest --cluster

# Bilingual embedding validation spike (see docs/M1-embedding-spike.md)
python -m app.spike.bilingual_eval --model intfloat/multilingual-e5-large

# Clustering precision harness — the M1 gate (see docs/M1-precision.md)
python -m app.eval.run_precision --model intfloat/multilingual-e5-large
python -m app.eval.run_precision --export-labeling to_label.jsonl   # build real gold set

# Enable the 10-min scheduler
PARAKH_ENABLE_SCHEDULER=1 uvicorn app.main:app
```

## Status (M1 — ingestion ✅ · embedding + clustering ✅ · precision gate open)

**Live and tested:** `fetch → dedupe → lang → persist → embed → cluster`.

- `app/pipeline/fetch.py` — feedparser + httpx over each source's `rss_urls`;
  per-source error isolation (one bad feed never aborts a cycle); `crawl_policy.disabled` honored.
- `app/pipeline/normalize.py` — strip HTML, snippet ≤200 chars (legal constraint),
  image extraction (media:content / thumbnail / enclosure), `published_at` → ISO, language.
- `app/pipeline/dedupe.py` — URL canonicalization collapses syndicated copies; 64-bit SimHash.
- `app/pipeline/embed.py` — `Embedder` seam: `E5Embedder` (multilingual-e5, `ml` extra) +
  deterministic `HashEmbedder` for tests/CI. No silent fallback to garbage vectors.
- `app/pipeline/cluster.py` — pure cosine-threshold incremental clustering (reference + tests).
- `app/pipeline/story_update.py` — per-story distributions (excludes unrated), ≥5 gate, blindspot flags.
- `app/db.py` — idempotent `upsert_articles()` + pgvector nearest-neighbour clustering pass
  (`cluster_pending_articles`), vectors passed as `::vector` literals (no pgvector pkg needed).
- `app/ingest.py` — fetch cycle + `run_cluster_pass()` (`--cluster`); wired into scheduler / API.

Tests: `pytest -m "not integration"` (offline — MockTransport, RSS fixture, synthetic vectors)
and `pytest -m integration` (real Postgres: upsert + pgvector clustering). Both run in CI.
The ML model stays out of CI; clustering is exercised with `HashEmbedder`.

**Precision harness built** (`app/eval/`, `docs/M1-precision.md`): pairwise
precision/recall/F1 + threshold sweep over a 71-article / 21-story labelled set
(bilingual, multi-outlet, hard-adjacent pairs). On e5-large the ≥85% gate is met at
threshold **0.88** (precision 1.0, recall 0.82, F1 0.90) — which **corrected** the
bilingual spike's 0.85 (that over-merges to precision 0.29). `cluster_sim_threshold`
is now 0.88.

## Still open (M1 gate — harness ready, not formally closed)

- The shipped gold set is **authored**, not hand-labelled from live feeds. Run
  `--export-labeling`, label ~100 real stories, and re-tune. Expect lower precision
  on real data.
- Consider a two-stage gate (SimHash pre-filter → vector confirm) for the sharp
  0.87→0.88 precision cliff.
- Nightly merge/split repair pass (recall safety net).
- Claude Haiku neutral titles + EN/HI summaries; 48h coverage sparkline series.

Tunable knobs (thresholds, intervals, model id) live in `app/config.py`.
