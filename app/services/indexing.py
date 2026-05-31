import uuid

from app.models.paper import Paper
from app.repositories.papers import PaperRepository
from app.services.embeddings import EmbeddingService
from app.services.vector_store import VectorPoint, VectorStore


class IndexingService:
    """Builds text chunks, embeddings, and vector index records for papers."""

    def __init__(self, papers: PaperRepository, embeddings: EmbeddingService, vector_store: VectorStore):
        self.papers = papers
        self.embeddings = embeddings
        self.vector_store = vector_store

    async def index_paper(self, paper: Paper) -> int:
        chunks = self._extract_chunks(paper)
        vectors = await self.embeddings.embed_texts([content for _, content in chunks])
        points: list[VectorPoint] = []
        saved_chunks: list[tuple[str, str, str]] = []
        await self.vector_store.delete_by_paper(paper.id)
        for (chunk_type, content), vector in zip(chunks, vectors, strict=True):
            embedding_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{paper.id}:{chunk_type}:{content[:128]}"))
            payload = {
                "paper_id": paper.id,
                "arxiv_id": paper.arxiv_id,
                "title": paper.title,
                "chunk_type": chunk_type,
                "text": content,
                "topics": paper.topics,
            }
            points.append(VectorPoint(id=embedding_id, vector=vector, payload=payload))
            saved_chunks.append((chunk_type, content, embedding_id))
        await self.vector_store.upsert(points)
        await self.papers.save_chunks(paper.id, saved_chunks)
        return len(points)

    def _extract_chunks(self, paper: Paper) -> list[tuple[str, str]]:
        chunks = [
            ("title", paper.title),
            ("abstract", paper.abstract),
        ]
        if paper.summary:
            chunks.append(("summary", paper.summary))
        if paper.methodology:
            chunks.append(("methodology", paper.methodology))
        for index, contribution in enumerate(paper.contributions):
            chunks.append((f"contribution_{index}", contribution))
        for topic in paper.topics:
            chunks.append(("topic", topic))
        return [(chunk_type, content.strip()) for chunk_type, content in chunks if content and content.strip()]
