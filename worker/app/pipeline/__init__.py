"""
Ingestion pipeline (design §4):

    cron (every 10 min)
     └─ FETCH   : RSS all sources -> normalize
     └─ DEDUPE  : URL canonicalization -> MinHash/SimHash on title+snippet
     └─ LANG    : fasttext / lingua
     └─ EMBED   : multilingual-e5 on title+snippet(+lead paras transiently)
     └─ CLUSTER : ANN (pgvector cosine) vs last 72h; sim >= ~0.82 -> attach, else new
     └─ STORY   : per-story stats, blindspot flags, AI title/summary, sparkline

Each stage is a pure-ish function over dataclasses so it is unit-testable. M0
ships the shapes and the orchestration seam; the ML bodies land in M1.
"""

from .fetch import fetch_all
from .dedupe import dedupe
from .langdetect import detect_language
from .embed import embed
from .cluster import cluster
from .story_update import update_story_stats

__all__ = [
    "fetch_all",
    "dedupe",
    "detect_language",
    "embed",
    "cluster",
    "update_story_stats",
]
