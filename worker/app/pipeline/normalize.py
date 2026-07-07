"""Pure normalization helpers — no I/O, so they unit-test without the network."""

from __future__ import annotations

import html
import re
from datetime import datetime, timezone
from time import struct_time

from .langdetect import detect_language
from .types import RawArticle

SNIPPET_MAX = 200  # legal constraint (§3.2): headline + <=200-char snippet only

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def strip_html(text: str | None) -> str:
    """Remove tags, unescape entities, collapse whitespace."""
    if not text:
        return ""
    no_tags = _TAG_RE.sub(" ", text)
    unescaped = html.unescape(no_tags)
    return _WS_RE.sub(" ", unescaped).strip()


def clean_snippet(text: str | None, max_len: int = SNIPPET_MAX) -> str:
    """Plain-text snippet truncated at a word boundary with an ellipsis."""
    plain = strip_html(text)
    if len(plain) <= max_len:
        return plain
    # Reserve one char for the ellipsis; cut at the last space before the limit.
    cut = plain[: max_len - 1]
    if " " in cut:
        cut = cut[: cut.rfind(" ")]
    return cut.rstrip() + "…"


def parse_published(entry: dict) -> str | None:
    """feedparser exposes *_parsed struct_time (UTC). Return ISO 8601, else None."""
    for key in ("published_parsed", "updated_parsed"):
        st = entry.get(key)
        if isinstance(st, struct_time):
            return datetime(*st[:6], tzinfo=timezone.utc).isoformat()
    return None


def extract_image(entry: dict) -> str | None:
    """Best-effort lead image from media:content / media:thumbnail / enclosure."""
    for item in entry.get("media_content", []) or []:
        url = item.get("url")
        if url:
            return url
    for item in entry.get("media_thumbnail", []) or []:
        url = item.get("url")
        if url:
            return url
    for enc in entry.get("enclosures", []) or []:
        t = (enc.get("type") or "")
        if t.startswith("image") and enc.get("href"):
            return enc["href"]
    return None


def build_raw_article(entry: dict, source_slug: str, source_lang: str) -> RawArticle | None:
    """Map a feedparser entry to a normalized RawArticle. None if unusable (no link/title)."""
    url = (entry.get("link") or "").strip()
    title = strip_html(entry.get("title"))
    if not url or not title:
        return None

    summary = entry.get("summary") or entry.get("description") or ""
    snippet = clean_snippet(summary)

    # Trust the source's declared language; fall back to detection on the title.
    lang = source_lang or detect_language(title) or "en"

    return RawArticle(
        source_slug=source_slug,
        url=url,
        title=title,
        snippet=snippet,
        image_url=extract_image(entry),
        lang=lang,
        published_at=parse_published(entry),
    )
