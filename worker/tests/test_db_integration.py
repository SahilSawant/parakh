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
