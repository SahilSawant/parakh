from __future__ import annotations

from app.config import settings


def compute_blindspot(rated: int, share_x: float, share_opposite: float, is_politics: bool) -> bool:
    """
    Design §4 blindspot rule for side X:
      rated_sources >= 5 AND share(X) < 20% AND share(opposite) > 60% AND politics-tagged.
    Computed on both axes; feed defaults to the govt axis. Tune on real data.
    """
    return (
        rated >= settings.blindspot_min_rated
        and share_x < settings.blindspot_low_share
        and share_opposite > settings.blindspot_high_share
        and is_politics
    )


def update_story_stats(story_id: str) -> None:
    """
    Recompute per-story stats: source counts, distribution across the 5 govt +
    5 ideology buckets, blindspot flags, AI title/summary (EN + HI), and the 48h
    coverage sparkline. Unrated outlets are listed but excluded from percentages.
    Distribution renders only at rated_source_count >= 5 (bias-bar gate). Stub.
    """
    _ = story_id
