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


# ---------- Embeddings + clustering (pgvector) ----------

def _vec_literal(v: list[float]) -> str:
    """pgvector text form '[x,y,z]' — lets us pass vectors without the pgvector pkg."""
    return "[" + ",".join(f"{x:.7f}" for x in v) + "]"


def get_article_id(conn: psycopg.Connection, source_slug: str, url: str) -> str | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.id::text FROM articles a
            JOIN sources s ON s.id = a.source_id
            WHERE s.slug = %s AND a.url = %s
            """,
            (source_slug, url),
        )
        row = cur.fetchone()
    return row[0] if row else None


def set_article_embedding(
    conn: psycopg.Connection, article_id: str, embedding: list[float], simhash: int | None = None
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE articles SET embedding = %s::vector, simhash = %s WHERE id = %s",
            (_vec_literal(embedding), simhash, article_id),
        )
    conn.commit()


def _nearest_story(
    conn: psycopg.Connection, embedding_text: str, window_hours: int
) -> tuple[str, float] | None:
    """Nearest already-clustered article within the window; returns (story_id, cosine_sim)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT story_id::text, 1 - (embedding <=> %s::vector) AS sim
            FROM articles
            WHERE story_id IS NOT NULL
              AND embedding IS NOT NULL
              AND COALESCE(published_at, created_at) > now() - make_interval(hours => %s)
            ORDER BY embedding <=> %s::vector
            LIMIT 1
            """,
            (embedding_text, window_hours, embedding_text),
        )
        row = cur.fetchone()
    return (row[0], float(row[1])) if row else None


def _create_story(conn: psycopg.Connection) -> str:
    """Open an empty story with a unique slug; stats are filled by a later pass."""
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO stories (slug) VALUES ('s-' || replace(gen_random_uuid()::text,'-','')) "
            "RETURNING id::text"
        )
        return cur.fetchone()[0]


def _attach(conn: psycopg.Connection, article_id: str, story_id: str) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE articles SET story_id = %s WHERE id = %s", (story_id, article_id))
        cur.execute(
            """
            UPDATE stories
            SET article_count = (SELECT count(*) FROM articles WHERE story_id = %s),
                last_updated = now()
            WHERE id = %s
            """,
            (story_id, story_id),
        )


def load_unembedded_articles(
    conn: psycopg.Connection, limit: int = 500
) -> list[tuple[str, RawArticle]]:
    """Articles with no embedding yet, oldest first, as (article_id, RawArticle)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.id::text, s.slug, a.url, a.title, COALESCE(a.snippet, ''), a.lang
            FROM articles a
            JOIN sources s ON s.id = a.source_id
            WHERE a.embedding IS NULL
            ORDER BY a.created_at
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
    return [
        (r[0], RawArticle(source_slug=r[1], url=r[2], title=r[3], snippet=r[4], lang=r[5]))
        for r in rows
    ]


def cluster_pending_articles(
    conn: psycopg.Connection, threshold: float, window_hours: int
) -> dict[str, int]:
    """
    Incremental clustering pass: for each embedded, still-unclustered article
    (oldest first), attach to the nearest story if cosine sim >= threshold, else
    open a new story. Mirrors pipeline.cluster.incremental_cluster over pgvector.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT id::text, embedding::text
            FROM articles
            WHERE story_id IS NULL AND embedding IS NOT NULL
            ORDER BY COALESCE(published_at, created_at)
            """
        )
        pending = cur.fetchall()

    attached = 0
    created = 0
    for article_id, emb_text in pending:
        hit = _nearest_story(conn, emb_text, window_hours)
        if hit and hit[1] >= threshold:
            story_id = hit[0]
        else:
            story_id = _create_story(conn)
            created += 1
        _attach(conn, article_id, story_id)
        attached += 1
    conn.commit()
    return {"pending": len(pending), "attached": attached, "new_stories": created}
