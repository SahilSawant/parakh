from app.pipeline.story_update import (
    GOVT_ORDER,
    compute_distribution,
    story_stats,
)


def test_distribution_excludes_unrated():
    buckets = ["pro", "pro", "mixed", None, None]  # 2 unrated
    dist = compute_distribution(buckets, GOVT_ORDER)
    # percentages over the 3 rated, not 5
    assert dist == {"pro": 66.7, "mixed": 33.3}


def test_distribution_empty_when_none_rated():
    assert compute_distribution([None, None], GOVT_ORDER) == {}


def test_stats_gate_below_five_rated():
    ratings = [{"govt_alignment": "pro", "ideology": "centre"} for _ in range(4)]
    s = story_stats(ratings, article_count=4, is_politics=True)
    assert s.rated_source_count == 4
    assert s.distribution_ready is False
    assert s.blindspot_flags == {}  # no flags below the gate


def test_stats_ready_at_five_rated():
    ratings = [{"govt_alignment": "pro", "ideology": "centre"} for _ in range(5)]
    s = story_stats(ratings, article_count=5, is_politics=False)
    assert s.distribution_ready is True


def test_blindspot_missed_by_pro():
    # 5 critical + 1 mixed, politics-tagged: pro media absent, critical media present
    ratings = [{"govt_alignment": "critical"} for _ in range(5)] + [{"govt_alignment": "mixed"}]
    s = story_stats(ratings, article_count=6, is_politics=True)
    assert s.rated_source_count == 6
    assert s.blindspot_flags["govt_missed_by_pro"] is True
    assert s.blindspot_flags["govt_missed_by_critical"] is False


def test_blindspot_requires_politics():
    ratings = [{"govt_alignment": "critical"} for _ in range(6)]
    s = story_stats(ratings, article_count=6, is_politics=False)
    assert s.blindspot_flags["govt_missed_by_pro"] is False
