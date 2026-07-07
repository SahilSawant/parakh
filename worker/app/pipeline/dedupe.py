from __future__ import annotations

from .types import RawArticle


def canonicalize_url(url: str) -> str:
    """Strip tracking params / fragments so the same article dedupes across feeds."""
    # M1: drop utm_*, gclid, fbclid, fragments; normalize host + trailing slash.
    return url.split("#", 1)[0].split("?", 1)[0].rstrip("/")


def dedupe(articles: list[RawArticle]) -> list[RawArticle]:
    """URL canonicalization now; MinHash/SimHash on title+snippet lands in M1."""
    seen: set[str] = set()
    out: list[RawArticle] = []
    for a in articles:
        key = canonicalize_url(a.url)
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out
