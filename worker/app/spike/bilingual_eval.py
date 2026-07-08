"""
Hindi↔English embedding spike — the M1 week-1 question:
does the multilingual model put the same story's English and Hindi headlines
close enough to cluster, while keeping different stories apart?

    python -m app.spike.bilingual_eval                     # uses settings.embedding_model
    python -m app.spike.bilingual_eval --model intfloat/multilingual-e5-small

Reports:
  - positive similarity  = cosine(EN_i, HI_i)  (same story, cross-language)
  - negative similarity  = cosine(EN_i, HI_j), i != j (different stories)
  - retrieval@1          = for each EN headline, is its true HI translation the
                           nearest of all HI headlines?
  - separation + a recommended clustering threshold
"""

from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path

from app.pipeline.cluster import cosine

PAIRS_PATH = Path(__file__).parent / "eval_pairs.json"


def load_pairs() -> list[dict[str, str]]:
    return json.loads(PAIRS_PATH.read_text(encoding="utf-8"))


@dataclass
class Report:
    n_pairs: int
    pos_min: float
    pos_mean: float
    neg_max: float
    neg_mean: float
    separation: float          # pos_min - neg_max (>0 => linearly separable)
    retrieval_at_1: float      # fraction of EN whose nearest HI is the true match
    recommended_threshold: float


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def retrieval_at_1(en_vecs: list[list[float]], hi_vecs: list[list[float]]) -> float:
    """For each EN vector, is its same-index HI vector the nearest HI vector?"""
    n = len(en_vecs)
    hits = 0
    for i in range(n):
        best_j = max(range(n), key=lambda j: cosine(en_vecs[i], hi_vecs[j]))
        hits += int(best_j == i)
    return hits / n if n else 0.0


def summarize(
    en_vecs: list[list[float]], hi_vecs: list[list[float]]
) -> Report:
    n = len(en_vecs)
    positives = [cosine(en_vecs[i], hi_vecs[i]) for i in range(n)]
    negatives = [
        cosine(en_vecs[i], hi_vecs[j]) for i in range(n) for j in range(n) if i != j
    ]
    pos_min = min(positives) if positives else 0.0
    neg_max = max(negatives) if negatives else 0.0
    # Midpoint between the worst true match and the best false match.
    recommended = round((pos_min + neg_max) / 2, 3)
    return Report(
        n_pairs=n,
        pos_min=round(pos_min, 3),
        pos_mean=round(_mean(positives), 3),
        neg_max=round(neg_max, 3),
        neg_mean=round(_mean(negatives), 3),
        separation=round(pos_min - neg_max, 3),
        retrieval_at_1=round(retrieval_at_1(en_vecs, hi_vecs), 3),
        recommended_threshold=recommended,
    )


def evaluate(model_name: str | None = None, embedder=None) -> Report:
    pairs = load_pairs()
    if embedder is None:
        from app.pipeline.embed import get_embedder

        embedder = get_embedder(model_name)
    en_vecs = embedder.embed([p["en"] for p in pairs])
    hi_vecs = embedder.embed([p["hi"] for p in pairs])
    return summarize(en_vecs, hi_vecs)


def _print_report(model: str, r: Report) -> None:
    print(f"\n  Bilingual embedding spike — {model}")
    print(f"  pairs: {r.n_pairs}")
    print(f"  positive (same story EN↔HI): min={r.pos_min}  mean={r.pos_mean}")
    print(f"  negative (different stories): max={r.neg_max}  mean={r.neg_mean}")
    print(f"  separation (pos_min - neg_max): {r.separation}")
    print(f"  retrieval@1: {r.retrieval_at_1:.0%}")
    print(f"  recommended clustering threshold: {r.recommended_threshold}")
    ok = r.separation > 0 and r.retrieval_at_1 >= 0.9
    verdict = (
        "PASS ✓ cross-lingual clustering viable"
        if ok
        else "REVIEW — margin thin; consider translate-then-embed fallback"
    )
    print(f"  verdict: {verdict}\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="app.spike.bilingual_eval")
    p.add_argument("--model", default=None, help="model id (default: settings.embedding_model)")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    from app.config import settings

    model = args.model or settings.embedding_model
    report = evaluate(model)
    _print_report(model, report)
    return 0 if report.separation > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
