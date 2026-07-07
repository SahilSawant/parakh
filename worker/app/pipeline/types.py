from __future__ import annotations

from dataclasses import dataclass, field


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
