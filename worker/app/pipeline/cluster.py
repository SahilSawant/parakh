from __future__ import annotations

from .types import EmbeddedArticle


def cluster(articles: list[EmbeddedArticle]) -> dict[str, list[EmbeddedArticle]]:
    """
    Incremental clustering (design §4): ANN (pgvector cosine) vs last 72h;
    sim >= ~0.82 -> attach to existing story, else open a new story. A nightly
    merge/split repair pass corrects drift.

    M0: returns an empty mapping (no live embeddings yet).
    """
    _ = articles
    return {}
