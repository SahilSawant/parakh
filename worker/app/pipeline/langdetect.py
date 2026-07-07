from __future__ import annotations


def detect_language(text: str) -> str:
    """Return an ISO code. M0 heuristic: Devanagari block -> 'hi', else 'en'.

    M1 swaps in `lingua` / fasttext for robust multilingual detection.
    """
    for ch in text:
        if "ऀ" <= ch <= "ॿ":  # Devanagari
            return "hi"
    return "en"
