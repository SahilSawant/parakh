# Parakh — database

Postgres 15+ with **pgvector**. Local dev image: `pgvector/pgvector:pg16`.

## Apply

```bash
export DATABASE_URL=postgres://postgres:postgres@localhost:5432/parakh
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f migrations/0001_core.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f migrations/0002_billing.sql
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f seed/0001_sources.sql
```

## Notes

- **Migrations are ordered and idempotent** (`IF NOT EXISTS`, guarded enum creation, `ON CONFLICT`). Re-running is safe.
- `articles.embedding VECTOR(1024)` matches `multilingual-e5-large` / `bge-m3`. HNSW + cosine index for the 72h clustering ANN.
- **Ratings are not seeded.** Sources start `NULL` on all three rating axes → the UI renders "Rating pending" until the §5 pipeline publishes. This is deliberate — mock ratings must never reach the DB.
- Rating history, evidence, and disputes are **public** surfaces (design 6a / 9c).
- The bias-bar gate (`rated_source_count >= 5`) is enforced at the API layer; `stories.rated_source_count` is the stored counter.

A proper migration runner (e.g. sqlx/drizzle/Atlas) lands with the API in M2; for M0 these are plain SQL applied in order.
