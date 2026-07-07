"""Ingestion orchestration + CLI.

    python -m app.ingest --dry-run --show 5      # fetch live, print samples, no DB
    python -m app.ingest --source the-hindu      # ingest one source into the DB
    python -m app.ingest                         # full cycle (needs DATABASE_URL)
"""

from __future__ import annotations

import argparse
import logging

from app.pipeline import dedupe, detect_language, fetch_all
from app.pipeline.types import RawArticle, Source

log = logging.getLogger("parakh.ingest")

# A handful of real seeded feeds so `--dry-run` validates the live path with no DB.
def _demo(slug: str, name: str, url: str, lang: str) -> Source:
    return Source(id=None, slug=slug, name=name, rss_urls=[url], lang=lang)


DEMO_SOURCES: list[Source] = [
    _demo("the-hindu", "The Hindu",
          "https://www.thehindu.com/news/national/feeder/default.rss", "en"),
    _demo("indian-express", "The Indian Express",
          "https://indianexpress.com/section/india/feed/", "en"),
    _demo("ndtv", "NDTV", "https://feeds.feedburner.com/ndtvnews-top-stories", "en"),
    _demo("bbc-hindi", "BBC News हिंदी", "https://feeds.bbci.co.uk/hindi/rss.xml", "hi"),
    _demo("the-wire", "The Wire", "https://thewire.in/rss", "en"),
]


def resolve_sources(only_slug: str | None = None, allow_demo: bool = False) -> list[Source]:
    """Load sources from the DB; fall back to DEMO_SOURCES only when allow_demo (dry-run)."""
    sources: list[Source]
    try:
        from app.db import connect, load_active_sources

        with connect() as conn:
            sources = load_active_sources(conn)
        log.info("loaded %d sources from DB", len(sources))
    except Exception as exc:
        if not allow_demo:
            raise
        log.warning("DB unavailable (%s) — using %d demo sources", exc, len(DEMO_SOURCES))
        sources = DEMO_SOURCES

    if only_slug:
        sources = [s for s in sources if s.slug == only_slug]
        if not sources:
            log.warning("no source matched slug %r", only_slug)
    return sources


def collect(sources: list[Source]) -> list[RawArticle]:
    """Fetch → dedupe → fill language. The read-only half of a cycle."""
    raw = fetch_all(sources)
    deduped = dedupe(raw)
    for a in deduped:
        if not a.lang:
            a.lang = detect_language(a.title)
    return deduped


def run_ingest_cycle(only_slug: str | None = None, dry_run: bool = False) -> dict[str, object]:
    """One ingestion cycle. Persists unless dry_run. Returns counts."""
    sources = resolve_sources(only_slug, allow_demo=dry_run)
    articles = collect(sources)

    if dry_run:
        log.info("dry-run: %d articles (not persisted)", len(articles))
        return {"sources": len(sources), "articles": len(articles), "inserted": 0, "dry_run": True}

    from app.db import connect, upsert_articles

    with connect() as conn:
        inserted = upsert_articles(conn, articles)
    log.info(
        "ingest: %d sources -> %d articles -> %d inserted",
        len(sources), len(articles), inserted,
    )
    return {
        "sources": len(sources),
        "articles": len(articles),
        "inserted": inserted,
        "dry_run": False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="app.ingest", description="Parakh RSS ingestion")
    p.add_argument("--dry-run", action="store_true", help="fetch + parse but skip DB writes")
    p.add_argument("--source", metavar="SLUG", help="ingest only this source slug")
    p.add_argument("--show", type=int, default=0, metavar="N", help="print N sample articles")
    args = p.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    if args.dry_run and args.show:
        sources = resolve_sources(args.source, allow_demo=True)
        articles = collect(sources)
        print(f"\n{len(articles)} articles from {len(sources)} sources (dry-run)\n")
        for a in articles[: args.show]:
            img = "🖼" if a.image_url else "  "
            print(f"[{a.lang}] {img} {a.source_slug:16} {a.title[:80]}")
            if a.snippet:
                print(f"        {a.snippet[:100]}")
        return 0

    stats = run_ingest_cycle(only_slug=args.source, dry_run=args.dry_run)
    print(stats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
