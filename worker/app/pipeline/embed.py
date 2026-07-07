from __future__ import annotations

from .types import EmbeddedArticle, RawArticle

# M1: load `intfloat/multilingual-e5-large` (or bge-m3). Validate Hindi<->English
# clustering week 1; fallback = Claude Haiku translation of Hindi titles pre-embed.
EMBED_DIM = 1024


def embed(articles: list[RawArticle]) -> list[EmbeddedArticle]:
    """Embed title+snippet (+lead paras transiently, then discarded). Stub only."""
    return [EmbeddedArticle(article=a) for a in articles]
