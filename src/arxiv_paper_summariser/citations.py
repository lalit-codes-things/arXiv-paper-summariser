"""Citation formatting and bibliography utilities."""

from __future__ import annotations

from .models import CitationStyle, Paper


class CitationFormatter:
    """Format in-text citations and bibliographies for review artifacts."""

    def __init__(self, style: CitationStyle | str = CitationStyle.APA) -> None:
        self.style = CitationStyle(style)

    def in_text(self, paper: Paper, index: int | None = None) -> str:
        """Return an in-text citation for a paper."""

        if self.style is CitationStyle.IEEE:
            return f"[{index}]" if index is not None else f"[{paper.id}]"
        if self.style is CitationStyle.MLA:
            return f"({paper.lead_author})"
        return f"({paper.lead_author}, {paper.year})"

    def bibliography_entry(self, paper: Paper, index: int | None = None) -> str:
        """Return a bibliography entry for a paper."""

        author_text = self._authors(paper)
        venue = f" {paper.venue}." if paper.venue else ""
        doi = f" doi:{paper.doi}." if paper.doi else ""
        url = f" {paper.url}" if paper.url else ""
        if self.style is CitationStyle.IEEE:
            prefix = f"[{index}] " if index is not None else ""
            return f"{prefix}{author_text}, \"{paper.title},\" {paper.year}.{venue}{doi}{url}".strip()
        if self.style is CitationStyle.MLA:
            return f"{author_text}. \"{paper.title}.\" {venue.strip()} {paper.year}.{doi}{url}".strip()
        return f"{author_text} ({paper.year}). {paper.title}.{venue}{doi}{url}".strip()

    def bibliography(self, papers: list[Paper]) -> tuple[str, ...]:
        """Return sorted bibliography entries."""

        sorted_papers = sorted(papers, key=lambda paper: (paper.lead_author, paper.year, paper.title))
        return tuple(
            self.bibliography_entry(paper, index=index)
            for index, paper in enumerate(sorted_papers, start=1)
        )

    @staticmethod
    def _authors(paper: Paper) -> str:
        if not paper.authors:
            return "Anonymous"
        if len(paper.authors) == 1:
            return paper.authors[0]
        if len(paper.authors) == 2:
            return f"{paper.authors[0]} & {paper.authors[1]}"
        return f"{paper.authors[0]} et al."
