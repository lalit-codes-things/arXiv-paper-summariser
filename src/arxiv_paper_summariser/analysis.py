"""Analysis primitives for V8 literature synthesis."""

from __future__ import annotations

from collections import defaultdict

from .models import CitationLink, Contradiction, Paper, TopicCluster, TrendPoint
from .text import tokenize, top_terms

POSITIVE_TERMS = {"improve", "improves", "improved", "effective", "robust", "outperform", "outperforms", "increase"}
NEGATIVE_TERMS = {"fails", "failed", "limited", "limitation", "decrease", "worse", "harm", "unstable", "ineffective"}
GAP_HINTS = {"future", "limitation", "limited", "open", "unexplored", "lack", "missing", "challenge"}


def build_citation_graph(papers: list[Paper]) -> tuple[CitationLink, ...]:
    """Build citation edges and mark whether targets are in the collection."""

    known_ids = {paper.id for paper in papers}
    links = [
        CitationLink(source_id=paper.id, target_id=target, target_in_collection=target in known_ids)
        for paper in papers
        for target in paper.citations
    ]
    return tuple(sorted(links, key=lambda link: (link.source_id, link.target_id)))


def analyze_chronology(papers: list[Paper], clusters: tuple[TopicCluster, ...]) -> tuple[TrendPoint, ...]:
    """Create chronological trend points for each theme and publication year."""

    paper_by_id = {paper.id: paper for paper in papers}
    points: list[TrendPoint] = []
    for cluster in clusters:
        by_year: defaultdict[int, list[str]] = defaultdict(list)
        for paper_id in cluster.paper_ids:
            by_year[paper_by_id[paper_id].year].append(paper_id)
        for year, paper_ids in sorted(by_year.items()):
            titles = "; ".join(paper_by_id[paper_id].title for paper_id in paper_ids[:3])
            points.append(
                TrendPoint(
                    year=year,
                    theme=cluster.label,
                    paper_ids=tuple(sorted(paper_ids)),
                    description=f"{year}: {cluster.label} appears in {len(paper_ids)} paper(s), including {titles}.",
                )
            )
    return tuple(points)


def detect_contradictions(papers: list[Paper]) -> tuple[Contradiction, ...]:
    """Detect likely contradictions from shared terms and opposing polarity."""

    contradictions: list[Contradiction] = []
    for left_index, left in enumerate(papers):
        left_terms = set(tokenize(" ".join((*left.claims, *left.findings, left.summary, left.abstract))))
        left_polarity = _polarity(left_terms)
        if left_polarity == 0:
            continue
        for right in papers[left_index + 1 :]:
            right_terms = set(tokenize(" ".join((*right.claims, *right.findings, right.summary, right.abstract))))
            right_polarity = _polarity(right_terms)
            shared = (left_terms & right_terms) - POSITIVE_TERMS - NEGATIVE_TERMS
            if right_polarity and left_polarity != right_polarity and shared:
                theme = ", ".join(sorted(shared)[:3])
                confidence = min(0.95, 0.55 + (len(shared) / 20))
                contradictions.append(
                    Contradiction(
                        paper_ids=(left.id, right.id),
                        theme=theme,
                        description=(
                            f"{left.title} and {right.title} discuss {theme} with opposing reported outcomes."
                        ),
                        confidence=round(confidence, 2),
                    )
                )
    return tuple(contradictions)


def analyze_gaps(papers: list[Paper], clusters: tuple[TopicCluster, ...]) -> tuple[str, ...]:
    """Generate gap-analysis statements from limitations and sparse themes."""

    gaps: list[str] = []
    for cluster in clusters:
        if len(cluster.paper_ids) == 1:
            gaps.append(f"The theme '{cluster.label}' is represented by a single paper, suggesting a sparse evidence base.")
    for paper in papers:
        limitation_text = " ".join((*paper.limitations, paper.summary, paper.abstract)).lower()
        if any(hint in limitation_text for hint in GAP_HINTS):
            source = paper.limitations[0] if paper.limitations else f"{paper.title} flags unresolved constraints."
            gaps.append(f"{paper.title}: {source}")
    if not gaps:
        themes = ", ".join(cluster.label for cluster in clusters[:3]) or "the collection"
        gaps.append(f"Future work should validate how findings across {themes} transfer to broader datasets and settings.")
    return tuple(dict.fromkeys(gaps))


def _polarity(tokens: set[str]) -> int:
    positive = len(tokens & POSITIVE_TERMS)
    negative = len(tokens & NEGATIVE_TERMS)
    if positive == negative:
        return 0
    return 1 if positive > negative else -1


def trend_evolution_summary(points: tuple[TrendPoint, ...]) -> str:
    """Summarize how themes evolve over time."""

    if not points:
        return "No chronological evidence was available."
    first_year = min(point.year for point in points)
    last_year = max(point.year for point in points)
    themes = top_terms((point.theme for point in points), limit=5)
    return (
        f"The collection spans {first_year}-{last_year}. Earlier work establishes "
        f"{', '.join(themes[:2]) or 'the core themes'}, while later papers broaden the discussion "
        f"toward {', '.join(themes[2:5]) or 'evaluation, deployment, and open challenges'}."
    )
