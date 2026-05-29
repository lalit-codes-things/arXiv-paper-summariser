"""Daily digest rendering helpers."""

from __future__ import annotations

from .models import DailyDigest


class DigestRenderer:
    """Render AI research digests for markdown, Notion, or email."""

    def to_markdown(self, digest: DailyDigest) -> str:
        """Render a digest as Markdown."""

        lines = [f"# Daily AI Research Digest — {digest.date.date().isoformat()}", ""]
        lines.append("## Top papers")
        for index, paper in enumerate(digest.top_papers, start=1):
            score = digest.rankings.get(paper.paper_id, 0)
            summary = digest.summaries.get(paper.paper_id)
            lines.append(f"{index}. **{paper.title}** ({score:.1f}) — {paper.url or paper.paper_id}")
            if summary:
                lines.append(f"   - {summary.findings.get('tldr', summary.summary)}")
        lines.extend(["", "## Trends"])
        for trend in digest.trends:
            lines.append(f"- **{trend.name}** ({trend.category}, {trend.score:.1f}): {trend.rationale}")
        lines.extend(["", "## Graph stats"])
        for key, value in digest.graph_stats.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
