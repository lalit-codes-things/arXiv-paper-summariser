from app.core.config import Settings
from app.repositories.papers import PaperRepository
from app.schemas.paper import PaperRead, SearchResponse, SearchResult
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorStore


class SearchService:
    def __init__(
        self,
        settings: Settings,
        papers: PaperRepository,
        embeddings: EmbeddingService,
        vector_store: VectorStore,
    ):
        self.settings = settings
        self.papers = papers
        self.embeddings = embeddings
        self.vector_store = vector_store

    async def semantic_search(self, query: str, *, limit: int | None = None) -> SearchResponse:
        limit = min(limit or self.settings.max_search_results, self.settings.max_search_results)
        query_vector = await self.embeddings.embed_query(query)
        hits = await self.vector_store.search(query_vector, limit=limit)
        results: list[SearchResult] = []
        seen: set[str] = set()
        for hit in hits:
            paper_id = hit.payload.get("paper_id")
            if not paper_id or paper_id in seen:
                continue
            paper = await self.papers.get(paper_id)
            if paper is None:
                continue
            await self.papers.increment_metric(paper.id, "searches")
            seen.add(paper_id)
            results.append(
                SearchResult(
                    paper=PaperRead.model_validate(paper),
                    score=hit.score,
                    matched_chunk=hit.payload.get("text"),
                    match_type="semantic",
                )
            )
        if len(results) < limit:
            for paper in await self.papers.keyword_search(query, limit=limit - len(results)):
                if paper.id in seen:
                    continue
                results.append(
                    SearchResult(
                        paper=PaperRead.model_validate(paper),
                        score=0.5,
                        matched_chunk=paper.abstract,
                        match_type="keyword",
                    )
                )
        return SearchResponse(query=query, results=results)

    async def related(self, paper_id: str, *, limit: int = 10) -> list[SearchResult]:
        paper = await self.papers.get(paper_id)
        if paper is None:
            return []
        query = " ".join([paper.title, paper.abstract, paper.summary or ""])
        response = await self.semantic_search(query, limit=limit + 1)
        return [result for result in response.results if result.paper.id != paper_id][:limit]
