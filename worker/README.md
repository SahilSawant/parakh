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

**Precision harness + REAL-data run** (`app/eval/`, `docs/M1-precision.md`).
Pairwise precision/recall/F1 + threshold sweep, run on **108 real articles** from 9
live outlets (EN + हिंदी) labelled by same-event grouping into 74 stories / 14
multi-outlet clusters (`gold_realset.jsonl`).

- **Gate MET on real data: precision 0.979 @ threshold 0.86** (the lone "false
  merge" is a labelling edge — LPG vs petrol daily-price briefs).
- Real data tuned `cluster_sim_threshold` to **0.86** (the authored set wanted 0.88).
- **Recall is the real gap:** ~57% pair recall; 8/14 multi-outlet stories fragment.

## Still open (gate met on precision; not formally closed)

- **Human-audit the labels** in `gold_realset.jsonl` (AI-assigned by event); scale
  toward the full hand-labelled 100 across several news days.
- **Recall/fragmentation** — the priority: nightly merge/split repair pass, two-stage
  gate (SimHash pre-filter → vector confirm), title+snippet embedding.
- Fix seed feeds that failed live: news18 (403 on our UA), dainik-jagran (404),
  the-print (malformed RSS).
- Claude Haiku neutral titles + EN/HI summaries; 48h coverage sparkline series.

Tunable knobs (thresholds, intervals, model id) live in `app/config.py`.
