"""DB integration — runs only when DATABASE_URL is set (CI's pgvector service).

Assumes migrations + seed are already applied (CI does this before pytest).
"""

import os

import pytest

pytestmark = pytest.mark.integration

DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("PARAKH_DATABASE_URL")

pytest.importorskip("psycopg")
if not DATABASE_URL:
    pytest.skip("DATABASE_URL not set", allow_module_level=True)

from app.db import connect, load_active_sources, upsert_articles  # noqa: E402
from app.pipeline.types import RawArticle  # noqa: E402

TEST_URL = "https://example.org/parakh-it/data-rules-it"


@pytest.fixture()
def conn():
    with connect(DATABASE_URL) as c:
        yield c
        # cleanup any rows this test inserted
        with c.cursor() as cur:
            cur.execute("DELETE FROM articles WHERE url = %s", (TEST_URL,))
        c.commit()


def test_load_active_sources_from_seed(conn):
    sources = load_active_sources(conn)
    slugs = {s.slug for s in sources}
    assert "ndtv" in slugs
    ndtv = next(s for s in sources if s.slug == "ndtv")
    assert ndtv.rss_urls  # seeded with at least one feed
    assert ndtv.id is not None


def test_upsert_is_idempotent(conn):
    art = RawArticle(
        source_slug="ndtv",
        url=TEST_URL,
        title="Integration: data rules notified",
        snippet="fixture snippet",
        lang="en",
        published_at="2026-07-04T09:30:00+00:00",
    )
    assert upsert_articles(conn, [art]) == 1  # first insert
    assert upsert_articles(conn, [art]) == 0  # ON CONFLICT DO NOTHING

    with conn.cursor() as cur:
        cur.execute("SELECT title, lang FROM articles WHERE url = %s", (TEST_URL,))
        row = cur.fetchone()
    assert row == ("Integration: data rules notified", "en")


def test_upsert_skips_unknown_slug(conn):
    art = RawArticle(source_slug="does-not-exist", url=TEST_URL + "-x", title="x")
    assert upsert_articles(conn, [art]) == 0


# ---------- clustering over pgvector ----------

import math  # noqa: E402

from app.db import (  # noqa: E402
    cluster_pending_articles,
    get_article_id,
    set_article_embedding,
)

CL_URLS = [f"https://example.org/parakh-it/cluster-{i}" for i in range(3)]


def _unit(dim: int, idx: int, second: int | None = None, w: float = 0.15) -> list[float]:
    v = [0.0] * dim
    v[idx] = 1.0
    if second is not None:
        v[second] = w
    norm = math.sqrt(sum(x * x for x in v))
    return [x / norm for x in v]


def test_cluster_pending_attaches_near_separates_far(conn):
    dim = 1024
    # a0 and a1 point mostly along dim 0 (cosine ~0.98); a2 is orthogonal.
    vecs = [_unit(dim, 0, 1), _unit(dim, 0, 2), _unit(dim, 500)]
    arts = [
        RawArticle(source_slug="ndtv", url=u, title=f"cluster fixture {i}")
        for i, u in enumerate(CL_URLS)
    ]
    upsert_articles(conn, arts)
    ids = [get_article_id(conn, "ndtv", u) for u in CL_URLS]
    assert all(ids)
    for aid, v in zip(ids, vecs):
        set_article_embedding(conn, aid, v)

    try:
        stats = cluster_pending_articles(conn, threshold=0.5, window_hours=72)
        assert stats["pending"] >= 3

        with conn.cursor() as cur:
            cur.execute("SELECT id::text, story_id::text FROM articles WHERE id = ANY(%s)", (ids,))
            story_of = dict(cur.fetchall())

        assert story_of[ids[0]] is not None
        assert story_of[ids[0]] == story_of[ids[1]]   # near-duplicates merged
        assert story_of[ids[2]] != story_of[ids[0]]   # far article separate
    finally:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT story_id::text FROM articles WHERE id = ANY(%s)", (ids,))
            story_ids = [r[0] for r in cur.fetchall() if r[0]]
            cur.execute("DELETE FROM articles WHERE id = ANY(%s)", (ids,))
            if story_ids:
                cur.execute("DELETE FROM stories WHERE id = ANY(%s)", (story_ids,))
        conn.commit()


PASS_URLS = [f"https://example.org/parakh-it/pass-{i}" for i in range(2)]


def test_run_cluster_pass_embeds_and_assigns(conn):
    """End-to-end wiring: unembedded articles get an embedding + a story.

    Uses the non-semantic HashEmbedder so CI needs no ML model — this asserts the
    plumbing (load → embed → set → cluster), not cross-lingual quality (that's the
    bilingual spike).
    """
    from app.ingest import run_cluster_pass
    from app.pipeline.embed import HashEmbedder

    arts = [
        RawArticle(source_slug="ndtv", url=u, title=f"pass fixture {i}")
        for i, u in enumerate(PASS_URLS)
    ]
    upsert_articles(conn, arts)
    ids = [get_article_id(conn, "ndtv", u) for u in PASS_URLS]

    try:
        run_cluster_pass(embedder=HashEmbedder())
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id::text, story_id::text, embedding IS NOT NULL "
                "FROM articles WHERE id = ANY(%s)",
                (ids,),
            )
            rows = cur.fetchall()
        assert len(rows) == 2
        assert all(has_emb for _, _, has_emb in rows)   # embedded
        assert all(sid is not None for _, sid, _ in rows)  # assigned to a story
    finally:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT story_id::text FROM articles WHERE id = ANY(%s)", (ids,))
            story_ids = [r[0] for r in cur.fetchall() if r[0]]
            cur.execute("DELETE FROM articles WHERE id = ANY(%s)", (ids,))
            if story_ids:
                cur.execute("DELETE FROM stories WHERE id = ANY(%s)", (story_ids,))
        conn.commit()
