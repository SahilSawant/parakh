"""Embedding abstraction.

A small `Embedder` seam lets clustering logic be tested with cheap deterministic
vectors while production uses a real multilingual model. No silent fallback: if a
real model is requested but unavailable, we raise rather than emit garbage vectors
that would quietly wreck clustering.
"""

from __future__ import annotations

import hashlib
import logging
import math
from typing import Protocol

from app.config import settings

from .dedupe import simhash64
from .types import EmbeddedArticle, RawArticle

log = logging.getLogger("parakh.embed")

EMBED_DIM = 1024  # matches articles.embedding VECTOR(1024) and multilingual-e5-large


def text_for_embedding(a: RawArticle) -> str:
    return f"{a.title}. {a.snippet}".strip() if a.snippet else a.title


class Embedder(Protocol):
    dim: int

    def embed(self, texts: list[str]) -> list[list[float]]: ...


class E5Embedder:
    """intfloat/multilingual-e5-* (or bge-m3). e5 wants a 'query:' prefix and
    cosine over L2-normalized vectors."""

    def __init__(self, model_name: str):
        from sentence_transformers import SentenceTransformer

        self._model = SentenceTransformer(model_name)
        self.dim = self._model.get_sentence_embedding_dimension()
        self._prefix = "query: " if "e5" in model_name.lower() else ""

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        prefixed = [self._prefix + t for t in texts]
        vecs = self._model.encode(prefixed, normalize_embeddings=True, convert_to_numpy=True)
        return [v.tolist() for v in vecs]


class HashEmbedder:
    """Deterministic, NON-semantic vectors for tests / CI / offline dry-runs.

    Same text -> same unit vector; different text -> different vector. It has NO
    semantic meaning, so cross-lingual clustering must be validated with a real
    model (the bilingual spike), never with this.
    """

    def __init__(self, dim: int = EMBED_DIM):
        self.dim = dim

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        seed = hashlib.sha256(text.encode("utf-8")).digest()
        vals: list[float] = []
        counter = 0
        while len(vals) < self.dim:
            block = hashlib.sha256(seed + counter.to_bytes(4, "big")).digest()
            for j in range(0, len(block), 2):
                if len(vals) >= self.dim:
                    break
                vals.append(int.from_bytes(block[j : j + 2], "big") / 65535.0 - 0.5)
            counter += 1
        norm = math.sqrt(sum(v * v for v in vals)) or 1.0
        return [v / norm for v in vals]


def get_embedder(model_name: str | None = None) -> Embedder:
    """Return the configured embedder. `embedding_model = "hash"` selects the fake."""
    name = model_name or settings.embedding_model
    if name == "hash":
        return HashEmbedder()
    return E5Embedder(name)


def embed(articles: list[RawArticle], embedder: Embedder | None = None) -> list[EmbeddedArticle]:
    """Embed title+snippet and compute a SimHash for each article."""
    embedder = embedder or get_embedder()
    texts = [text_for_embedding(a) for a in articles]
    vectors = embedder.embed(texts)
    return [
        EmbeddedArticle(article=a, embedding=v, simhash=simhash64(t))
        for a, v, t in zip(articles, vectors, texts)
    ]
