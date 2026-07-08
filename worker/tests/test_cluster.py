import math

from app.pipeline.cluster import cosine, incremental_cluster, nearest
from app.pipeline.types import EmbeddedArticle, RawArticle


def _art(vec):
    return EmbeddedArticle(article=RawArticle(source_slug="s", url="u", title="t"), embedding=vec)


def test_cosine_bounds():
    assert math.isclose(cosine([1, 0], [1, 0]), 1.0)
    assert math.isclose(cosine([1, 0], [0, 1]), 0.0)
    assert cosine([0, 0], [1, 0]) == 0.0  # zero vector guard


def test_nearest_picks_best():
    cents = [("a", [1, 0, 0]), ("b", [0, 1, 0])]
    cid, sim = nearest([0.9, 0.1, 0], cents)
    assert cid == "a" and sim > 0.9


def test_incremental_separates_two_groups():
    # two well-separated directions + a near-duplicate of the first
    items = [
        _art([1.0, 0.0, 0.0]),
        _art([0.98, 0.20, 0.0]),   # ~same story as item 0
        _art([0.0, 0.0, 1.0]),     # different story
    ]
    out = incremental_cluster(items, existing=[], threshold=0.82)
    assert out[0].is_new is True
    assert out[1].cluster_id == out[0].cluster_id  # merged
    assert out[1].is_new is False
    assert out[2].cluster_id != out[0].cluster_id  # separate
    assert out[2].is_new is True


def test_cross_lingual_near_duplicate_merges():
    # simulate EN/HI embeddings of the same story landing very close
    en = _art([0.90, 0.30, 0.10])
    hi = _art([0.88, 0.33, 0.12])
    out = incremental_cluster([en, hi], existing=[], threshold=0.82)
    assert out[1].cluster_id == out[0].cluster_id


def test_high_threshold_opens_all_new():
    items = [_art([0.9, 0.1, 0.0]), _art([0.8, 0.2, 0.0])]
    out = incremental_cluster(items, existing=[], threshold=0.999)
    assert all(a.is_new for a in out)
    assert out[0].cluster_id != out[1].cluster_id


def test_attaches_to_existing_centroid():
    out = incremental_cluster(
        [_art([1.0, 0.0])], existing=[("story-x", [0.99, 0.02])], threshold=0.82
    )
    assert out[0].cluster_id == "story-x"
    assert out[0].is_new is False
