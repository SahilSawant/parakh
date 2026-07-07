from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Source:
    """A publisher we ingest. Loaded from the `sources` table (or a demo fallback)."""

    id: str | None
    slug: str
    name: str
    rss_urls: list[str]
    lang: str = "en"
    crawl_policy: dict = field(default_factory=dict)


@dataclass
class RawArticle:
    """Normalized RSS item — legal constraint: snippet <= 200 chars, canonical link only."""

    source_slug: str
    url: str
    title: str
    snippet: str = ""
    image_url: str | None = None
    lang: str = "en"
    published_at: str | None = None  # ISO 8601


@dataclass
class EmbeddedArticle:
    article: RawArticle
    embedding: list[float] = field(default_factory=list)  # dim 1024
    simhash: int | None = None
