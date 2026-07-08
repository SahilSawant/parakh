"""Runner plumbing tests — synthetic vectors, no model (kept out of CI)."""

from pathlib import Path

from app.eval.run_precision import cluster_labels, evaluate_at, load_gold

REALSET = Path(__file__).resolve().parents[1] / "app" / "eval" / "gold_realset.jsonl"


def test_load_gold_shipped_set():
    items = load_gold()
    assert len(items) >= 60
    assert all(it["id"] and it["story"] and it["title"] for it in items)
    stories = {it["story"] for it in items}
    assert len(stories) >= 15
    # the two hard-adjacent pairs are present and distinctly labelled
    assert {"isro-nvs", "isro-spadex", "budget-tax", "gst-council"} <= stories


def test_evaluate_at_perfect_when_separated():
    items = [{"story": "A", "title": "a1"}, {"story": "A", "title": "a2"},
             {"story": "B", "title": "b1"}, {"story": "B", "title": "b2"}]
    vecs = [[1, 0, 0], [0.98, 0.2, 0], [0, 0, 1], [0.02, 0, 0.99]]
    s = evaluate_at(items, vecs, threshold=0.5)
    assert s.precision == 1.0
    assert s.recall == 1.0
    assert s.n_pred_clusters == 2


def test_evaluate_at_false_merge_when_all_similar():
    items = [{"story": "A", "title": "a1"}, {"story": "A", "title": "a2"},
             {"story": "B", "title": "b1"}, {"story": "B", "title": "b2"}]
    vecs = [[1, 0, 0], [0.99, 0.1, 0], [0.98, 0.0, 0.1], [0.99, 0.05, 0.05]]
    s = evaluate_at(items, vecs, threshold=0.5)
    assert s.n_pred_clusters == 1
    assert s.fp > 0
    assert s.precision < 0.5


def test_cluster_labels_length_matches():
    items = [{"story": "A", "title": "x"}, {"story": "B", "title": "y"}]
    labels = cluster_labels(items, [[1, 0], [0, 1]], threshold=0.9)
    assert len(labels) == 2
    assert labels[0] != labels[1]


def test_real_gold_set_parses():
    items = load_gold(REALSET)
    assert len(items) >= 100
    assert all(it["id"] and it["story"] and it["title"] for it in items)
    stories = {it["story"] for it in items}
    # multi-outlet clusters + many singletons
    assert len(stories) >= 50
    assert "bishnoi-crackdown" in stories
    bishnoi = [it for it in items if it["story"] == "bishnoi-crackdown"]
    assert len(bishnoi) >= 5  # genuine cross-outlet cluster
