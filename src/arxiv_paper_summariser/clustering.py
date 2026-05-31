"""Topic clustering pipeline for paper collections."""

from __future__ import annotations

from collections import defaultdict

from .models import Paper, TopicCluster
from .text import first_sentence, jaccard, tfidf_keywords, tokenize, top_terms


class ClusteringPipeline:
    """Cluster papers into human-readable research themes.

    The pipeline is deterministic and dependency-free: it uses TF-IDF keywords
    and token-set similarity to build small thematic clusters that can be
    inspected, tested, and used in offline workflows.
    """

    def __init__(self, similarity_threshold: float = 0.12) -> None:
        self.similarity_threshold = similarity_threshold

    def run(self, papers: list[Paper], max_keywords: int = 6, min_cluster_size: int = 1) -> tuple[TopicCluster, ...]:
        """Return topic clusters for a paper collection."""

        if not papers:
            return ()
        documents = {paper.id: paper.narrative for paper in papers}
        keywords_by_id = tfidf_keywords(documents, limit=max_keywords)
        paper_by_id = {paper.id: paper for paper in papers}
        unassigned = set(paper_by_id)
        clusters: list[list[str]] = []

        while unassigned:
            seed_id = sorted(unassigned)[0]
            seed_tokens = set(keywords_by_id[seed_id]) or set(tokenize(documents[seed_id]))
            cluster = [seed_id]
            unassigned.remove(seed_id)
            for candidate_id in sorted(list(unassigned)):
                candidate_tokens = set(keywords_by_id[candidate_id]) or set(tokenize(documents[candidate_id]))
                if jaccard(seed_tokens, candidate_tokens) >= self.similarity_threshold:
                    cluster.append(candidate_id)
                    unassigned.remove(candidate_id)
            clusters.append(cluster)

        merged = self._merge_small_clusters(clusters, keywords_by_id, min_cluster_size)
        return tuple(
            self._to_topic_cluster(index, paper_ids, paper_by_id, max_keywords)
            for index, paper_ids in enumerate(merged, start=1)
        )

    def _merge_small_clusters(
        self,
        clusters: list[list[str]],
        keywords_by_id: dict[str, tuple[str, ...]],
        min_cluster_size: int,
    ) -> list[list[str]]:
        if min_cluster_size <= 1:
            return clusters
        large = [cluster for cluster in clusters if len(cluster) >= min_cluster_size]
        small = [cluster for cluster in clusters if len(cluster) < min_cluster_size]
        if not large:
            return clusters
        for cluster in small:
            cluster_terms = set().union(*(set(keywords_by_id[paper_id]) for paper_id in cluster))
            best_index = max(
                range(len(large)),
                key=lambda index: jaccard(
                    cluster_terms,
                    set().union(*(set(keywords_by_id[paper_id]) for paper_id in large[index])),
                ),
            )
            large[best_index].extend(cluster)
        return large

    def _to_topic_cluster(
        self,
        index: int,
        paper_ids: list[str],
        paper_by_id: dict[str, Paper],
        max_keywords: int,
    ) -> TopicCluster:
        papers = [paper_by_id[paper_id] for paper_id in paper_ids]
        keywords = top_terms((paper.narrative for paper in papers), limit=max_keywords)
        label = " / ".join(term.title() for term in keywords[:3]) or f"Theme {index}"
        representative = first_sentence(papers[0].summary or papers[0].abstract, papers[0].title)
        summary = f"{label} groups {len(papers)} paper(s). Representative focus: {representative}"
        return TopicCluster(
            id=f"T{index}",
            label=label,
            paper_ids=tuple(sorted(paper_ids)),
            keywords=keywords,
            summary=summary,
        )


def group_by_theme(clusters: tuple[TopicCluster, ...]) -> dict[str, tuple[str, ...]]:
    """Return a compact theme-to-paper-id mapping."""

    grouped: defaultdict[str, list[str]] = defaultdict(list)
    for cluster in clusters:
        grouped[cluster.label].extend(cluster.paper_ids)
    return {theme: tuple(ids) for theme, ids in grouped.items()}
