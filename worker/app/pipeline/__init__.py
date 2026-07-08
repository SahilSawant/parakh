"""
Ingestion pipeline (design §4):

    cron (every 10 min)
     └─ FETCH   : RSS all sources -> normalize
     └─ DEDUPE  : URL canonicalization -> SimHash on title+snippet
     └─ LANG    : Devanagari heuristic (lingua in a later slice)
     └─ EMBED   : multilingual-e5 on title+snippet -> VECTOR(1024)
     └─ CLUSTER : cosine >= ~0.82 vs last 72h -> attach, else new story
     └─ STORY   : per-story stats, distributions, blindspot flags

FETCH/DEDUPE/LANG/EMBED are live; CLUSTER/STORY have pure reference
implementations here and DB-backed orchestration in app/db.py + app/ingest.py.
"""

from .cluster import Assignment, cosine, incremental_cluster, nearest
from .dedupe import canonicalize_url, dedupe, hamming, simhash64
from .embed import EMBED_DIM, embed, get_embedder
from .fetch import fetch_all
from .langdetect import detect_language
from .story_update import compute_blindspot, compute_distribution, story_stats

__all__ = [
    "fetch_all",
    "dedupe",
    "canonicalize_url",
    "simhash64",
    "hamming",
    "detect_language",
    "embed",
    "get_embedder",
    "EMBED_DIM",
    "cosine",
    "nearest",
    "incremental_cluster",
    "Assignment",
    "compute_distribution",
    "compute_blindspot",
    "story_stats",
]
