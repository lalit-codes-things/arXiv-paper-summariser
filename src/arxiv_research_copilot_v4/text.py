"""Small deterministic NLP helpers used when no LLM backend is configured."""

from __future__ import annotations

import math
import re
from collections import Counter

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into", "is",
    "it", "of", "on", "or", "that", "the", "their", "this", "to", "we", "with", "using", "via",
    "our", "show", "shows", "paper", "propose", "present", "new", "based", "model", "models",
}


def sentences(text: str) -> list[str]:
    """Split text into readable sentences without external dependencies."""

    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def tokens(text: str) -> list[str]:
    """Return normalized word tokens."""

    return [token.lower() for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]+", text)]


def keywords(text: str, *, limit: int = 10) -> list[str]:
    """Extract keyword-like tokens by frequency."""

    counts = Counter(token for token in tokens(text) if token not in STOPWORDS and len(token) > 2)
    return [word for word, _ in counts.most_common(limit)]


def keyphrases(text: str, *, ngram_range: tuple[int, int] = (2, 3), limit: int = 10) -> list[tuple[str, int]]:
    """Extract frequent n-grams suitable for trend and topic detection."""

    words = [token for token in tokens(text) if token not in STOPWORDS and len(token) > 2]
    counts: Counter[str] = Counter()
    for n in range(ngram_range[0], ngram_range[1] + 1):
        for index in range(0, max(0, len(words) - n + 1)):
            phrase = " ".join(words[index : index + n])
            counts[phrase] += 1
    return counts.most_common(limit)


def centroid_summary(text: str, *, max_sentences: int = 3) -> str:
    """Create a concise extractive summary."""

    parts = sentences(text)
    if len(parts) <= max_sentences:
        return " ".join(parts)
    word_counts = Counter(token for token in tokens(text) if token not in STOPWORDS)
    scored: list[tuple[float, int, str]] = []
    for index, sentence in enumerate(parts):
        sentence_tokens = [token for token in tokens(sentence) if token not in STOPWORDS]
        if not sentence_tokens:
            continue
        score = sum(word_counts[token] for token in sentence_tokens) / math.sqrt(len(sentence_tokens))
        scored.append((score, index, sentence))
    chosen = sorted(scored, reverse=True)[:max_sentences]
    return " ".join(sentence for _, _, sentence in sorted(chosen, key=lambda item: item[1]))


def contains_any(text: str, markers: set[str]) -> bool:
    """Return true when any marker appears in text."""

    lowered = text.lower()
    return any(marker in lowered for marker in markers)
