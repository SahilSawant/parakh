import feedparser

from app.pipeline.normalize import (
    SNIPPET_MAX,
    build_raw_article,
    clean_snippet,
    extract_image,
    parse_published,
    strip_html,
)
from tests.conftest import FIXTURE


def test_strip_html_unescapes_and_collapses():
    assert strip_html("<p>a &amp; b\n  c</p>") == "a & b c"
    assert strip_html(None) == ""


def test_clean_snippet_truncates_at_word_boundary():
    long = "word " * 100  # 500 chars
    out = clean_snippet(long)
    assert len(out) <= SNIPPET_MAX
    assert out.endswith("…")
    assert "  " not in out  # collapsed, and no mid-word cut leaving a partial token
    assert not out[:-1].endswith(" ")


def test_clean_snippet_short_passthrough():
    assert clean_snippet("<b>short</b>") == "short"


def _entries():
    return feedparser.parse(FIXTURE.read_bytes()).entries


def test_extract_image_from_media_content():
    e = _entries()[0]
    assert extract_image(e) == "https://example.org/img/data-rules.jpg"


def test_extract_image_absent():
    e = _entries()[1]
    assert extract_image(e) is None


def test_parse_published_iso():
    e = _entries()[0]
    iso = parse_published(e)
    assert iso is not None and iso.startswith("2026-07-04T09:30:00")


def test_build_raw_article_english():
    e = _entries()[0]
    art = build_raw_article(e, "demo", "en")
    assert art is not None
    assert art.title == "Centre notifies data protection rules & seeks industry input"
    assert art.url.startswith("https://example.org/story/data-rules")
    assert len(art.snippet) <= SNIPPET_MAX
    assert art.image_url is not None
    assert art.lang == "en"


def test_build_raw_article_hindi_lang():
    e = _entries()[1]
    art = build_raw_article(e, "demo", "hi")
    assert art is not None
    assert art.lang == "hi"


def test_build_raw_article_no_link_dropped():
    e = _entries()[3]
    assert build_raw_article(e, "demo", "en") is None
