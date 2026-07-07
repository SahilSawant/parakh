from __future__ import annotations

from .types import RawArticle

# NOTE (M0): stubbed. M1 wires feedparser over each source's rss_urls, respects
# per-source crawl_policy / robots.txt, and truncates snippet to 200 chars.


def fetch_all(rss_urls: list[str]) -> list[RawArticle]:
    """Fetch + normalize RSS items across all source feeds. Stub returns []."""
    _ = rss_urls
    return []
