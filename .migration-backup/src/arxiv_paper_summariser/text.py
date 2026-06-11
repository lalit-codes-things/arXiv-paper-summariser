"""Small deterministic text-analysis helpers for offline review generation."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Iterable

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "using",
    "we",
    "with",
    "our",
    "paper",
    "study",
    "results",
}

TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def tokenize(text: str) -> list[str]:
    """Normalize free text into content-bearing tokens."""

    return [
        token.lower()
        for token in TOKEN_RE.findall(text)
        if token.lower() not in STOPWORDS and not token.isdigit()
    ]


def top_terms(texts: Iterable[str], limit: int = 8) -> tuple[str, ...]:
    """Return high-signal terms across a set of texts."""

    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(tokenize(text))
    return tuple(term for term, _ in counter.most_common(limit))


def sentences(text: str) -> list[str]:
    """Split text into compact sentences for extractive synthesis."""

    return [sentence.strip() for sentence in SENTENCE_RE.split(text.strip()) if sentence.strip()]


def jaccard(left: set[str], right: set[str]) -> float:
    """Compute Jaccard similarity between two token sets."""

    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def tfidf_keywords(documents: dict[str, str], limit: int = 8) -> dict[str, tuple[str, ...]]:
    """Compute lightweight TF-IDF keywords without external dependencies."""

    tokenized = {doc_id: tokenize(text) for doc_id, text in documents.items()}
    doc_frequency: defaultdict[str, int] = defaultdict(int)
    for tokens in tokenized.values():
        for token in set(tokens):
            doc_frequency[token] += 1

    total_docs = max(len(documents), 1)
    result: dict[str, tuple[str, ...]] = {}
    for doc_id, tokens in tokenized.items():
        counts = Counter(tokens)
        scored = []
        for token, count in counts.items():
            idf = math.log((1 + total_docs) / (1 + doc_frequency[token])) + 1
            scored.append((token, count * idf))
        scored.sort(key=lambda item: (-item[1], item[0]))
        result[doc_id] = tuple(token for token, _ in scored[:limit])
    return result


def first_sentence(text: str, fallback: str) -> str:
    """Return a short representative sentence."""

    parts = sentences(text)
    return parts[0] if parts else fallback
