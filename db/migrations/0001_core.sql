-- ============================================================
-- Parakh — core data model (§4)
-- Postgres 15+ with the pgvector extension.
-- Ratings are OURS (hybrid pipeline, §5); never seeded from mockups.
-- ============================================================

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto; -- gen_random_uuid()

-- ---------- Enums ----------
DO $$ BEGIN
  CREATE TYPE govt_alignment AS ENUM ('pro','lean_pro','mixed','lean_critical','critical');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE ideology AS ENUM ('left','lean_left','centre','lean_right','right');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE factuality AS ENUM ('very_high','high','mixed','low','very_low');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE bias_axis AS ENUM ('govt','ideology');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE rater_kind AS ENUM ('mbfc_seed','llm','panel','editorial');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE disputant_type AS ENUM ('reader','outlet','researcher');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE dispute_status AS ENUM ('open','under_review','responded','closed');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TYPE follow_kind AS ENUM ('topic','source','state');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ---------- Ownership ----------
CREATE TABLE IF NOT EXISTS ownership_groups (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL,
  parent_company  TEXT,
  owner_notes     TEXT,
  other_holdings  JSONB NOT NULL DEFAULT '[]'::jsonb,
  evidence_source TEXT,                       -- e.g. "from exchange filings"
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS uq_ownership_name ON ownership_groups(name);

-- ---------- Sources ----------
CREATE TABLE IF NOT EXISTS sources (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name              TEXT NOT NULL,
  slug              TEXT NOT NULL UNIQUE,
  url               TEXT,
  rss_urls          TEXT[] NOT NULL DEFAULT '{}',
  lang              TEXT NOT NULL DEFAULT 'en',     -- 'en' | 'hi' | ...
  state             TEXT,                            -- NULL for national
  ownership_group_id UUID REFERENCES ownership_groups(id) ON DELETE SET NULL,

  -- Ratings are ours; NULL == "Rating pending" until the pipeline publishes.
  govt_alignment    govt_alignment,
  ideology          ideology,
  factuality        factuality,

  rating_method     JSONB NOT NULL DEFAULT '{}'::jsonb,
  rating_updated_at TIMESTAMPTZ,
  crawl_policy      JSONB NOT NULL DEFAULT '{}'::jsonb,

  is_govt_official  BOOLEAN NOT NULL DEFAULT FALSE, -- PIB etc — never in the bias bar
  is_fact_checker   BOOLEAN NOT NULL DEFAULT FALSE, -- own content type -> fact-check chips
  medium_meta       TEXT,                            -- "English · TV + digital · Delhi"

  created_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sources_lang ON sources(lang);
CREATE INDEX IF NOT EXISTS idx_sources_state ON sources(state);

-- Rating history is PUBLIC (design 6a).
CREATE TABLE IF NOT EXISTS source_rating_history (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id    UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  axis         bias_axis NOT NULL,
  old_value    TEXT,
  new_value    TEXT NOT NULL,
  effective_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  public_note  TEXT
);
CREATE INDEX IF NOT EXISTS idx_rating_history_source ON source_rating_history(source_id, effective_at DESC);

-- ---------- Articles ----------
-- multilingual-e5-large / bge-m3 => 1024-dim embeddings.
CREATE TABLE IF NOT EXISTS articles (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id    UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  story_id     UUID,  -- FK added after stories exists (below)
  url          TEXT NOT NULL,
  title        TEXT NOT NULL,
  snippet      TEXT,                    -- <= 200 chars (legal constraint, §3.2)
  image_url    TEXT,
  lang         TEXT NOT NULL DEFAULT 'en',
  published_at TIMESTAMPTZ,
  embedding    VECTOR(1024),
  simhash      BIGINT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (source_id, url)
);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_story ON articles(story_id);
CREATE INDEX IF NOT EXISTS idx_articles_simhash ON articles(simhash);
-- ANN over last-72h clustering. HNSW + cosine (pgvector >= 0.5).
CREATE INDEX IF NOT EXISTS idx_articles_embedding
  ON articles USING hnsw (embedding vector_cosine_ops);

-- ---------- Stories (clusters) ----------
CREATE TABLE IF NOT EXISTS stories (
  id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug               TEXT NOT NULL UNIQUE,
  title_ai_en        TEXT,
  title_ai_hi        TEXT,
  summary_ai_en      TEXT,
  summary_ai_hi      TEXT,
  top_image          TEXT,
  first_seen         TIMESTAMPTZ NOT NULL DEFAULT now(),
  last_updated       TIMESTAMPTZ NOT NULL DEFAULT now(),
  article_count      INTEGER NOT NULL DEFAULT 0,
  rated_source_count INTEGER NOT NULL DEFAULT 0,   -- gates the bias bar (>= 5)
  dist_govt          JSONB NOT NULL DEFAULT '{}'::jsonb,
  dist_ideology      JSONB NOT NULL DEFAULT '{}'::jsonb,
  blindspot_flags    JSONB NOT NULL DEFAULT '{}'::jsonb,
  topic_tags         TEXT[] NOT NULL DEFAULT '{}',
  state_tags         TEXT[] NOT NULL DEFAULT '{}',
  coverage_series    JSONB NOT NULL DEFAULT '[]'::jsonb  -- 48h sparkline series
);
CREATE INDEX IF NOT EXISTS idx_stories_last_updated ON stories(last_updated DESC);

ALTER TABLE articles
  DROP CONSTRAINT IF EXISTS fk_articles_story;
ALTER TABLE articles
  ADD CONSTRAINT fk_articles_story
  FOREIGN KEY (story_id) REFERENCES stories(id) ON DELETE SET NULL;

-- ---------- Rating evidence (feeds the public evidence table) ----------
CREATE TABLE IF NOT EXISTS rating_evidence (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id   UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  axis        bias_axis NOT NULL,
  rater       rater_kind NOT NULL,
  score       TEXT NOT NULL,       -- the bucket assigned by this rater
  rationale   TEXT,
  article_url TEXT,                -- the scored article (rubric-scored recent articles only)
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_evidence_source ON rating_evidence(source_id, axis);

-- ---------- Disputes (PUBLIC permanent log; 30-day SLA, design 9c) ----------
CREATE TABLE IF NOT EXISTS rating_disputes (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id      UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  axis           bias_axis NOT NULL,
  disputant_type disputant_type NOT NULL,
  claim          TEXT NOT NULL,
  evidence_urls  TEXT[] NOT NULL DEFAULT '{}',
  status         dispute_status NOT NULL DEFAULT 'open',
  panel_response TEXT,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  responded_at   TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_disputes_source ON rating_disputes(source_id);
CREATE INDEX IF NOT EXISTS idx_disputes_status ON rating_disputes(status);

-- ---------- Users (Supporters-with-sync only) ----------
CREATE TABLE IF NOT EXISTS users (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email      TEXT NOT NULL UNIQUE,
  otp_secret TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Follows keyed by user OR anonymous device id (reading_log stays on-device).
CREATE TABLE IF NOT EXISTS follows (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_or_device_id TEXT NOT NULL,
  kind              follow_kind NOT NULL,
  target_id         TEXT NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_or_device_id, kind, target_id)
);
