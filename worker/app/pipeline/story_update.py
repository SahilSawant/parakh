from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from app.config import settings

GOVT_ORDER = ["pro", "lean_pro", "mixed", "lean_critical", "critical"]
IDEOLOGY_ORDER = ["left", "lean_left", "centre", "lean_right", "right"]


def compute_distribution(buckets: list[str | None], order: list[str]) -> dict[str, float]:
    """
    Percent of *rated* sources in each bucket. Unrated (None) outlets are listed
    but excluded from percentages (design rule). Empty if nothing is rated.
    """
    rated = [b for b in buckets if b]
    n = len(rated)
    if n == 0:
        return {}
    counts = Counter(rated)
    return {b: round(100 * counts[b] / n, 1) for b in order if counts[b]}


def compute_blindspot(rated: int, share_x: float, share_opposite: float, is_politics: bool) -> bool:
    """
    Design §4 blindspot rule for side X:
      rated >= 5 AND share(X) < 20% AND share(opposite) > 60% AND politics-tagged.
    Shares are percentages (0..100). Tune on real data.
    """
    return (
        rated >= settings.blindspot_min_rated
        and share_x < settings.blindspot_low_share * 100
        and share_opposite > settings.blindspot_high_share * 100
        and is_politics
    )


def _pole_shares(dist: dict[str, float], low: list[str], high: list[str]) -> tuple[float, float]:
    return sum(dist.get(k, 0.0) for k in low), sum(dist.get(k, 0.0) for k in high)


@dataclass
class StoryStats:
    article_count: int
    rated_source_count: int
    dist_govt: dict[str, float]
    dist_ideology: dict[str, float]
    distribution_ready: bool  # >= 5 rated -> the bias bar may render
    blindspot_flags: dict[str, bool] = field(default_factory=dict)


def story_stats(
    source_ratings: list[dict[str, str | None]],
    article_count: int,
    is_politics: bool = False,
) -> StoryStats:
    """
    Aggregate a story's per-source ratings into distributions + flags.

    `source_ratings`: one dict per DISTINCT source in the cluster, e.g.
        {"govt_alignment": "pro", "ideology": "lean_left"}  (values may be None).
    """
    govt = compute_distribution([s.get("govt_alignment") for s in source_ratings], GOVT_ORDER)
    ideo = compute_distribution([s.get("ideology") for s in source_ratings], IDEOLOGY_ORDER)

    rated_count = sum(1 for s in source_ratings if s.get("govt_alignment"))
    ready = rated_count >= settings.min_rated_for_distribution

    flags: dict[str, bool] = {}
    if ready:
        pro_share, crit_share = _pole_shares(
            govt, ["pro", "lean_pro"], ["critical", "lean_critical"]
        )
        flags["govt_missed_by_pro"] = compute_blindspot(
            rated_count, pro_share, crit_share, is_politics
        )
        flags["govt_missed_by_critical"] = compute_blindspot(
            rated_count, crit_share, pro_share, is_politics
        )

    return StoryStats(
        article_count=article_count,
        rated_source_count=rated_count,
        dist_govt=govt,
        dist_ideology=ideo,
        distribution_ready=ready,
        blindspot_flags=flags,
    )
