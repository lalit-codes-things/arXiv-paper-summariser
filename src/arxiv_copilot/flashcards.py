"""Flashcard helpers."""

from __future__ import annotations

from arxiv_copilot.schemas import Flashcard, StructuredSummary


def flashcards_from_summary(summary: StructuredSummary) -> list[Flashcard]:
    """Return LLM-generated cards plus deterministic concept and implementation cards."""

    cards = list(summary.flashcards)
    for contribution in summary.contributions[:3]:
        cards.append(Flashcard(question="What contribution does the paper claim?", answer=contribution, kind="concept"))
    for method in summary.methodology[:3]:
        cards.append(Flashcard(question="How is the method implemented or evaluated?", answer=method, kind="implementation"))
    return _dedupe(cards)


def _dedupe(cards: list[Flashcard]) -> list[Flashcard]:
    seen: set[tuple[str, str]] = set()
    unique: list[Flashcard] = []
    for card in cards:
        key = (card.question.lower().strip(), card.answer.lower().strip())
        if key in seen:
            continue
        seen.add(key)
        unique.append(card)
    return unique
