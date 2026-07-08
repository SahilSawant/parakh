"""
Fetch a real corpus from live feeds for the precision gate — no DB needed.

    python -m app.eval.build_realset --per-feed 12 --out realset_raw.jsonl

Writes a labelling template: one JSON object per article with a blank `story`
field for a human (or an audited pass) to fill. The ARTICLES are real; only the
cluster labels are added afterwards. This is how the authored bootstrap set is
replaced with real data.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from app.pipeline.dedupe import dedupe
from app.pipeline.fetch import fetch_all
from app.pipeline.types import Source

log = logging.getLogger("parakh.realset")

def _feed(slug: str, url: str, lang: str) -> Source:
    return Source(id=None, slug=slug, name=slug, rss_urls=[url], lang=lang)


# Top-stories / national feeds across outlets so the same big events co-occur.
REAL_FEEDS: list[Source] = [
    _feed("the-hindu", "https://www.thehindu.com/news/national/feeder/default.rss", "en"),
    _feed("indian-express", "https://indianexpress.com/section/india/feed/", "en"),
    _feed("ndtv", "https://feeds.feedburner.com/ndtvnews-top-stories", "en"),
    _feed("toi", "https://timesofindia.indiatimes.com/rssfeedstopstories.cms", "en"),
    _feed("hindustan-times",
          "https://www.hindustantimes.com/feeds/rss/india-news/rssfeed.xml", "en"),
    _feed("mint", "https://www.livemint.com/rss/news", "en"),
    _feed("the-print", "https://theprint.in/feed/", "en"),
    _feed("news18", "https://www.news18.com/rss/india.xml", "en"),
    _feed("bbc-hindi", "https://feeds.bbci.co.uk/hindi/rss.xml", "hi"),
    _feed("aaj-tak", "https://www.aajtak.in/rssfeeds/?id=home", "hi"),
    _feed("dainik-bhaskar", "https://www.bhaskar.com/rss-v1--category-1061.xml", "hi"),
    _feed("dainik-jagran", "https://www.jagran.com/rss/news/national.xml", "hi"),
]


def build(per_feed: int, out: str) -> int:
    articles: list = []
    for src in REAL_FEEDS:
        got = dedupe(fetch_all([src]))[:per_feed]
        articles.extend(got)
    articles = dedupe(articles)

    rows = [
        {"id": f"r{i:03d}", "story": "", "lang": a.lang, "outlet": a.source_slug, "title": a.title}
        for i, a in enumerate(articles)
    ]
    Path(out).write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8"
    )
    log.info("wrote %d real articles to %s (fill 'story' to label)", len(rows), out)
    return len(rows)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="app.eval.build_realset")
    p.add_argument("--per-feed", type=int, default=12, help="max articles kept per feed")
    p.add_argument("--out", default="realset_raw.jsonl", help="output labelling template")
    args = p.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    build(args.per_feed, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
