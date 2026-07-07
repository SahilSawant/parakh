from __future__ import annotations

import logging

import feedparser
import httpx

from .normalize import build_raw_article
from .types import RawArticle, Source

log = logging.getLogger("parakh.fetch")

USER_AGENT = "ParakhBot/0.1 (+https://parakh.news; news-coverage transparency)"
DEFAULT_TIMEOUT = 12.0
MAX_ENTRIES_PER_FEED = 60  # newest items; older ones already clustered or aged out


def _client(client: httpx.Client | None) -> tuple[httpx.Client, bool]:
    if client is not None:
        return client, False
    return (
        httpx.Client(
            timeout=DEFAULT_TIMEOUT,
            follow_redirects=True,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            },
        ),
        True,
    )


def fetch_feed(url: str, source: Source, client: httpx.Client) -> list[RawArticle]:
    """Fetch and parse a single feed URL into normalized articles. Errors -> []."""
    try:
        resp = client.get(url)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("fetch failed %s (%s): %s", source.slug, url, exc)
        return []

    parsed = feedparser.parse(resp.content)
    if parsed.bozo and not parsed.entries:
        log.warning("unparseable feed %s (%s): %s", source.slug, url, parsed.get("bozo_exception"))
        return []

    out: list[RawArticle] = []
    for entry in parsed.entries[:MAX_ENTRIES_PER_FEED]:
        art = build_raw_article(entry, source.slug, source.lang)
        if art is not None:
            out.append(art)
    return out


def fetch_source(source: Source, client: httpx.Client) -> list[RawArticle]:
    """All feeds for one source. Per-source isolation: one bad feed never aborts the run."""
    if source.crawl_policy.get("disabled"):
        return []
    articles: list[RawArticle] = []
    for url in source.rss_urls:
        articles.extend(fetch_feed(url, source, client))
    return articles


def fetch_all(sources: list[Source], client: httpx.Client | None = None) -> list[RawArticle]:
    """Fetch every source's feeds. Failures are isolated and logged, not fatal."""
    c, owned = _client(client)
    try:
        articles: list[RawArticle] = []
        for source in sources:
            try:
                got = fetch_source(source, c)
                articles.extend(got)
                log.info("fetched %-18s %3d articles", source.slug, len(got))
            except Exception:  # defensive: never let one source kill the cycle
                log.exception("unexpected error fetching %s", source.slug)
        return articles
    finally:
        if owned:
            c.close()
