from app.eval.metrics import pairwise_score


def test_perfect_clustering():
    s = pairwise_score(["a", "a", "b", "b"], ["x", "x", "y", "y"])
    assert s.precision == 1.0
    assert s.recall == 1.0
    assert s.f1 == 1.0
    assert (s.tp, s.fp, s.fn) == (2, 0, 0)


def test_bad_merge_lowers_precision():
    # gold: {0,1}=A, {2}=B ; pred lumps all three together
    s = pairwise_score(["A", "A", "B"], ["X", "X", "X"])
    # pairs: (0,1) TP, (0,2) FP, (1,2) FP
    assert (s.tp, s.fp, s.fn) == (1, 2, 0)
    assert round(s.precision, 3) == 0.333
    assert s.recall == 1.0


def test_over_split_perfect_precision_low_recall():
    # gold says {0,1} together; pred splits them
    s = pairwise_score(["A", "A"], ["X", "Y"])
    assert (s.tp, s.fp, s.fn) == (0, 0, 1)
    assert s.precision == 1.0     # no false merges
    assert s.recall == 0.0


def test_all_singletons_both_sides():
    s = pairwise_score(["a", "b", "c"], ["x", "y", "z"])
    assert s.precision == 1.0     # vacuous — no pairs merged
    assert s.recall == 1.0        # nothing needed merging
    assert s.n_pred_clusters == 3
    assert s.n_gold_clusters == 3


def test_gate_helper():
    s = pairwise_score(["a", "a"], ["x", "x"])
    assert s.gate_met(0.85) is True


def test_length_mismatch_raises():
    try:
        pairwise_score(["a"], ["x", "y"])
    except ValueError:
        return
    raise AssertionError("expected ValueError")
