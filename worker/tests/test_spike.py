"""Unit tests for the bilingual-spike math (no model — synthetic vectors)."""

from app.spike.bilingual_eval import load_pairs, retrieval_at_1, summarize


def test_eval_pairs_shape():
    pairs = load_pairs()
    assert len(pairs) >= 10
    assert all(p["en"] and p["hi"] and p["topic"] for p in pairs)


def test_retrieval_at_1_perfect_when_aligned():
    en = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    hi = [[0.99, 0.1, 0], [0.05, 0.99, 0.02], [0, 0.03, 0.99]]
    assert retrieval_at_1(en, hi) == 1.0


def test_retrieval_at_1_zero_when_swapped():
    en = [[1, 0], [0, 1]]
    hi = [[0, 1], [1, 0]]  # each EN's true match is the far one
    assert retrieval_at_1(en, hi) == 0.0


def test_summarize_separation_positive_for_aligned():
    en = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    hi = [[0.98, 0.1, 0.0], [0.1, 0.98, 0.05], [0.02, 0.05, 0.98]]
    r = summarize(en, hi)
    assert r.n_pairs == 3
    assert r.separation > 0
    assert r.retrieval_at_1 == 1.0
    assert r.neg_max <= r.pos_min  # separable
    assert r.pos_min <= r.recommended_threshold <= r.pos_mean or r.recommended_threshold > 0
