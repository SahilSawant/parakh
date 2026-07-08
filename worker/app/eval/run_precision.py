"""
M1 precision harness. Clusters a labelled gold set with the REAL pipeline
(embed → incremental_cluster) and scores pairwise precision/recall/F1, then sweeps
thresholds to find the operating point.

    python -m app.eval.run_precision                       # settings.embedding_model
    python -m app.eval.run_precision --model intfloat/multilingual-e5-large --sweep
    python -m app.eval.run_precision --gold path/to/labelled.jsonl

Gate (work order §7): >= 85% pairwise precision. Precision is the gate because a
false merge corrupts a story's bias distribution — the product's core claim.

NOTE: the shipped gold set is honestly *authored* (bootstrap), not the hand-labelled
100 from live feeds. It validates the harness and gives a realistic number incl.
hard adjacent pairs (ISRO NVS vs SpaDeX, Budget vs GST). Formally closing the gate
means running this over the real labelled set (see export_for_labeling).
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from app.config import settings
from app.eval.metrics import PairwiseScore, pairwise_score
from app.pipeline.cluster import incremental_cluster
from app.pipeline.embed import text_for_embedding
from app.pipeline.types import EmbeddedArticle, RawArticle

log = logging.getLogger("parakh.eval")

GOLD_PATH = Path(__file__).parent / "gold_stories.jsonl"
DEFAULT_GATE = 0.85


def load_gold(path: Path = GOLD_PATH) -> list[dict]:
    items: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            items.append(json.loads(line))
    return items


def _articles(items: list[dict]) -> list[RawArticle]:
    return [
        RawArticle(
            source_slug=it.get("outlet", "gold"),
            url=it["id"],
            title=it["title"],
            snippet=it.get("snippet", ""),
            lang=it.get("lang", "en"),
        )
        for it in items
    ]


def embed_gold(items: list[dict], embedder) -> list[list[float]]:
    texts = [text_for_embedding(a) for a in _articles(items)]
    return embedder.embed(texts)


def cluster_labels(items: list[dict], vectors: list[list[float]], threshold: float) -> list[str]:
    emb = [
        EmbeddedArticle(
            article=RawArticle(source_slug="g", url=str(i), title=it["title"]), embedding=v
        )
        for i, (it, v) in enumerate(zip(items, vectors))
    ]
    return [a.cluster_id for a in incremental_cluster(emb, existing=[], threshold=threshold)]


def evaluate_at(items: list[dict], vectors: list[list[float]], threshold: float) -> PairwiseScore:
    gold = [it["story"] for it in items]
    pred = cluster_labels(items, vectors, threshold)
    return pairwise_score(gold, pred)


def sweep(
    items: list[dict], vectors: list[list[float]], thresholds: list[float]
) -> list[tuple[float, PairwiseScore]]:
    return [(t, evaluate_at(items, vectors, t)) for t in thresholds]


def _threshold_grid(lo: float = 0.70, hi: float = 0.95, step: float = 0.01) -> list[float]:
    n = round((hi - lo) / step)
    return [round(lo + i * step, 2) for i in range(n + 1)]


def _print_sweep(model: str, rows: list[tuple[float, PairwiseScore]], gate: float) -> None:
    print(f"\n  Precision sweep — {model}")
    print(f"  {'thr':>5}  {'prec':>6}  {'recall':>7}  {'f1':>6}  {'clusters':>8}")
    for t, s in rows:
        mark = "  ← gate" if s.precision >= gate else ""
        print(
            f"  {t:>5.2f}  {s.precision:>6.3f}  {s.recall:>7.3f}  "
            f"{s.f1:>6.3f}  {s.n_pred_clusters:>8}{mark}"
        )


def report(model: str, gate: float = DEFAULT_GATE, embedder=None) -> int:
    from app.pipeline.embed import get_embedder

    items = load_gold()
    embedder = embedder or get_embedder(model)
    vectors = embed_gold(items, embedder)

    grid = _threshold_grid()
    rows = sweep(items, vectors, grid)
    _print_sweep(model, rows, gate)

    best_f1_t, best_f1 = max(rows, key=lambda r: r[1].f1)
    # Lowest threshold that satisfies the precision gate (max recall among those).
    passing = [(t, s) for t, s in rows if s.precision >= gate]
    op = evaluate_at(items, vectors, settings.cluster_sim_threshold)

    n_gold = rows[0][1].n_gold_clusters
    print(f"\n  gold: {len(items)} articles · {n_gold} stories")
    print(f"  operating threshold {settings.cluster_sim_threshold}: "
          f"precision={op.precision:.3f} recall={op.recall:.3f} f1={op.f1:.3f} "
          f"(fp_pairs={op.fp})")
    print(f"  best F1: {best_f1.f1:.3f} at threshold {best_f1_t}")
    if passing:
        t_gate, s_gate = passing[0]
        print(f"  gate ≥{gate:.0%} precision first met at threshold {t_gate} "
              f"(recall {s_gate.recall:.3f})")
    else:
        print(f"  gate ≥{gate:.0%} precision NOT met at any swept threshold")

    met = op.gate_met(gate)
    print(f"  verdict @ operating threshold: {'PASS ✓' if met else 'BELOW GATE ✗'}\n")
    return 0 if met else 1


def export_for_labeling(db_limit: int = 500, out: str = "to_label.jsonl") -> int:
    """Bootstrap the real gold set: dump ingested articles as a labelling template
    (blank `story` field for a human to fill). The path to the hand-labelled 100."""
    from app.db import connect

    rows = []
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT a.id::text, s.slug, a.lang, a.title FROM articles a "
            "JOIN sources s ON s.id = a.source_id ORDER BY a.created_at DESC LIMIT %s",
            (db_limit,),
        )
        for aid, slug, lang, title in cur.fetchall():
            rows.append({"id": aid, "story": "", "lang": lang, "outlet": slug, "title": title})
    payload = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows)
    Path(out).write_text(payload, encoding="utf-8")
    print(f"wrote {len(rows)} rows to {out} — fill the empty 'story' field, then run --gold {out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="app.eval.run_precision")
    p.add_argument("--model", default=None, help="model id (default: settings.embedding_model)")
    p.add_argument("--gate", type=float, default=DEFAULT_GATE, help="precision gate (default 0.85)")
    p.add_argument("--sweep", action="store_true", help="(default) print the threshold sweep")
    p.add_argument("--export-labeling", metavar="OUT", help="dump DB articles to label")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    if args.export_labeling:
        return export_for_labeling(out=args.export_labeling)

    model = args.model or settings.embedding_model
    return report(model, gate=args.gate)


if __name__ == "__main__":
    raise SystemExit(main())
