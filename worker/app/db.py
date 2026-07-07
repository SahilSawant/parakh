"""Postgres access for ingestion. Thin psycopg layer — no ORM."""

from __future__ import annotations

import logging
from collections.abc import Iterator, Sequence
from contextlib import contextmanager

import psycopg

from app.config import settings
from app.pipeline.types import RawArticle, Source

log = logging.getLogger("parakh.db")


@contextmanager
def connect(dsn: str | None = None) -> Iterator[psycopg.Connection]:
    conn = psycopg.connect(dsn or settings.database_url)
    try:
        yield conn
    finally:
        conn.close()


def load_active_sources(conn: psycopg.Connection) -> list[Source]:
    """All sources with at least one feed. PIB/fact-checkers included (labeled downstream)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id::text, slug, name, rss_urls, lang, crawl_policy
            FROM sources
            WHERE array_length(rss_urls, 1) >= 1
            ORDER BY slug
            """
        )
        rows = cur.fetchall()
    return [
        Source(
            id=r[0],
            slug=r[1],
            name=r[2],
            rss_urls=list(r[3] or []),
            lang=r[4],
            crawl_policy=r[5] or {},
        )
        for r in rows
    ]


def _slug_to_id(conn: psycopg.Connection, slugs: Sequence[str]) -> dict[str, str]:
    if not slugs:
        return {}
    with conn.cursor() as cur:
        cur.execute("SELECT slug, id::text FROM sources WHERE slug = ANY(%s)", (list(set(slugs)),))
        return {slug: sid for slug, sid in cur.fetchall()}


def upsert_articles(conn: psycopg.Connection, articles: list[RawArticle]) -> int:
    """
    Insert new articles; existing (source_id, url) pairs are skipped (idempotent).
    Embedding/simhash stay NULL — the embed+cluster stages fill them in M1's next slice.
    Returns the count of rows actually inserted.
    """
    if not articles:
        return 0

    slug_map = _slug_to_id(conn, [a.source_slug for a in articles])
    inserted = 0
    with conn.cursor() as cur:
        for a in articles:
            source_id = slug_map.get(a.source_slug)
            if source_id is None:
                log.warning("no source row for slug %s — skipping %s", a.source_slug, a.url)
                continue
            cur.execute(
                """
                INSERT INTO articles (source_id, url, title, snippet, image_url, lang, published_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id, url) DO NOTHING
                """,
                (source_id, a.url, a.title, a.snippet, a.image_url, a.lang, a.published_at),
            )
            inserted += cur.rowcount  # 1 if inserted, 0 if conflict
    conn.commit()
    return inserted
