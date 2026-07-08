"""Incremental clustering — pure vector math, no DB, so it unit-tests directly.

Design §4: attach an article to the nearest existing story if cosine similarity
>= threshold (~0.82, tuned on real data), else open a new story. The DB-backed
production path (pgvector ANN over the last 72h) lives in app/db.py and mirrors
this logic; this module is the reference + the within-batch clusterer.
"""

from __future__ import annotations

from dataclasses import dataclass

from .types import EmbeddedArticle

Vector = list[float]


def cosine(a: Vector, b: Vector) -> float:
    dot = 0.0
    na = 0.0
    nb = 0.0
    for x, y in zip(a, b):
        dot += x * y
        na += x * x
        nb += y * y
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na**0.5 * nb**0.5)


def nearest(vec: Vector, centroids: list[tuple[str, Vector]]) -> tuple[str | None, float]:
    """Best (cluster_id, similarity) over candidate centroids; (None, -1) if empty."""
    best_id: str | None = None
    best_sim = -1.0
    for cid, c in centroids:
        s = cosine(vec, c)
        if s > best_sim:
            best_sim = s
            best_id = cid
    return best_id, best_sim


@dataclass
class Assignment:
    article: EmbeddedArticle
    cluster_id: str
    similarity: float
    is_new: bool


def incremental_cluster(
    items: list[EmbeddedArticle],
    existing: list[tuple[str, Vector]],
    threshold: float,
) -> list[Assignment]:
    """
    Assign each item to an existing story centroid or open a new cluster. Centroids
    update as a running mean so several new articles in one batch coalesce. New
    clusters get synthetic ids "new:0", "new:1", ... for the caller to persist.
    """
    # cluster_id -> (sum_vector, count); centroid = sum / count
    sums: dict[str, list[float]] = {cid: list(v) for cid, v in existing}
    counts: dict[str, int] = {cid: 1 for cid, _ in existing}

    assignments: list[Assignment] = []
    new_idx = 0
    for it in items:
        centroids = [(cid, [x / counts[cid] for x in s]) for cid, s in sums.items()]
        cid, sim = nearest(it.embedding, centroids)

        if cid is not None and sim >= threshold:
            sums[cid] = [a + b for a, b in zip(sums[cid], it.embedding)]
            counts[cid] += 1
            assignments.append(Assignment(it, cid, sim, is_new=False))
        else:
            cid = f"new:{new_idx}"
            new_idx += 1
            sums[cid] = list(it.embedding)
            counts[cid] = 1
            assignments.append(Assignment(it, cid, max(sim, 0.0), is_new=True))

    return assignments
