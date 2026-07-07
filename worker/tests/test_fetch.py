import httpx

from app.pipeline.dedupe import canonicalize_url, dedupe
from app.pipeline.fetch import fetch_feed
from app.pipeline.types import Source
from tests.conftest import FIXTURE


def _mock_client(body: bytes, status: int = 200) -> httpx.Client:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, content=body)

    return httpx.Client(transport=httpx.MockTransport(handler))


def test_fetch_feed_parses_and_normalizes():
    src = Source(id=None, slug="demo", name="Demo", rss_urls=["https://x/feed"], lang="en")
    with _mock_client(FIXTURE.read_bytes()) as client:
        arts = fetch_feed("https://x/feed", src, client)

    # 3 items have links (one has none and is dropped).
    assert len(arts) == 3
    assert all(a.source_slug == "demo" for a in arts)
    assert all(a.title for a in arts)


def test_fetch_feed_http_error_returns_empty():
    src = Source(id=None, slug="demo", name="Demo", rss_urls=["https://x/feed"], lang="en")
    with _mock_client(b"nope", status=500) as client:
        assert fetch_feed("https://x/feed", src, client) == []


def test_canonicalize_strips_tracking():
    a = canonicalize_url("https://example.org/story/data-rules?utm_source=rss&utm_medium=feed")
    b = canonicalize_url("https://example.org/story/data-rules?utm_source=partner")
    assert a == b == "https://example.org/story/data-rules"


def test_dedupe_collapses_syndicated_copies():
    src = Source(id=None, slug="demo", name="Demo", rss_urls=["https://x/feed"], lang="en")
    with _mock_client(FIXTURE.read_bytes()) as client:
        arts = fetch_feed("https://x/feed", src, client)
    deduped = dedupe(arts)
    # The English original and its syndicated copy share a canonical URL -> one survives.
    assert len(deduped) == 2
