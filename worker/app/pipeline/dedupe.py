from __future__ import annotations

import hashlib

from .types import RawArticle


def canonicalize_url(url: str) -> str:
    """Strip tracking params / fragments so the same article dedupes across feeds."""
    # M1: drop query + fragment. (utm_*, gclid, fbclid all live in the query.)
    return url.split("#", 1)[0].split("?", 1)[0].rstrip("/")


def dedupe(articles: list[RawArticle]) -> list[RawArticle]:
    """URL canonicalization now; SimHash near-dup (below) is used at cluster time."""
    seen: set[str] = set()
    out: list[RawArticle] = []
    for a in articles:
        key = canonicalize_url(a.url)
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out


def simhash64(text: str) -> int:
    """
    64-bit SimHash over whitespace tokens, returned as a *signed* int so it fits
    Postgres BIGINT. Near-duplicate titles have small Hamming distance. Used as a
    cheap pre-filter before the vector step; stored on `articles.simhash`.
    """
    tokens = text.lower().split()
    if not tokens:
        return 0
    bits = [0] * 64
    for tok in tokens:
        h = int.from_bytes(hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest(), "big")
        for i in range(64):
            bits[i] += 1 if (h >> i) & 1 else -1
    value = 0
    for i in range(64):
        if bits[i] > 0:
            value |= 1 << i
    # Reinterpret as signed 64-bit (two's complement) to fit BIGINT; bit pattern
    # is preserved, so Hamming distance is unchanged.
    return value - (1 << 64) if value >= (1 << 63) else value


def hamming(a: int, b: int) -> int:
    """Hamming distance between two SimHashes (bit count of XOR, masked to 64 bits)."""
    return bin((a ^ b) & ((1 << 64) - 1)).count("1")
