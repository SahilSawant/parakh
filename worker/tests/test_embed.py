import math

from app.pipeline.dedupe import hamming, simhash64
from app.pipeline.embed import EMBED_DIM, HashEmbedder, embed, get_embedder, text_for_embedding
from app.pipeline.types import RawArticle


def test_hash_embedder_deterministic_and_unit_norm():
    e = HashEmbedder(dim=64)
    a = e.embed(["hello world"])[0]
    b = e.embed(["hello world"])[0]
    c = e.embed(["different"])[0]
    assert a == b            # deterministic
    assert a != c            # distinct text -> distinct vector
    assert len(a) == 64
    assert math.isclose(math.sqrt(sum(x * x for x in a)), 1.0, rel_tol=1e-9)


def test_get_embedder_hash_selector():
    assert isinstance(get_embedder("hash"), HashEmbedder)


def test_text_for_embedding_joins_title_and_snippet():
    art = RawArticle(source_slug="s", url="u", title="Title", snippet="Snippet")
    assert text_for_embedding(art) == "Title. Snippet"
    bare = RawArticle(source_slug="s", url="u", title="Title", snippet="")
    assert text_for_embedding(bare) == "Title"


def test_embed_fills_vector_and_simhash():
    arts = [
        RawArticle(source_slug="s", url="u1", title="Data rules notified today"),
        RawArticle(source_slug="s", url="u2", title="Cricket series won in Chennai"),
    ]
    out = embed(arts, embedder=HashEmbedder(dim=EMBED_DIM))
    assert len(out) == 2
    assert all(len(o.embedding) == EMBED_DIM for o in out)
    assert all(o.simhash is not None for o in out)


def test_simhash_fits_signed_bigint_and_hamming():
    lo, hi = -(2**63), 2**63 - 1
    h1 = simhash64("the government notified data protection rules today")
    h2 = simhash64("the government notified data protection rules today")
    h3 = simhash64("india win the cricket test series against australia")
    assert lo <= h1 <= hi
    assert hamming(h1, h2) == 0            # identical text
    assert hamming(h1, h3) > 0            # unrelated text differs
