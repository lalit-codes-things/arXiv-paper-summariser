import math
from dataclasses import dataclass, field
from typing import Protocol

from app.core.config import Settings


@dataclass(slots=True)
class VectorPoint:
    id: str
    vector: list[float]
    payload: dict = field(default_factory=dict)


@dataclass(slots=True)
class VectorHit:
    id: str
    score: float
    payload: dict = field(default_factory=dict)


class VectorStore(Protocol):
    async def upsert(self, points: list[VectorPoint]) -> None: ...

    async def search(self, vector: list[float], *, limit: int, filters: dict | None = None) -> list[VectorHit]: ...

    async def delete_by_paper(self, paper_id: str) -> None: ...


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._points: dict[str, VectorPoint] = {}

    async def upsert(self, points: list[VectorPoint]) -> None:
        for point in points:
            self._points[point.id] = point

    async def search(self, vector: list[float], *, limit: int, filters: dict | None = None) -> list[VectorHit]:
        hits: list[VectorHit] = []
        for point in self._points.values():
            if filters and any(point.payload.get(key) != value for key, value in filters.items()):
                continue
            hits.append(VectorHit(id=point.id, score=_cosine(vector, point.vector), payload=point.payload))
        return sorted(hits, key=lambda hit: hit.score, reverse=True)[:limit]

    async def delete_by_paper(self, paper_id: str) -> None:
        self._points = {
            point_id: point
            for point_id, point in self._points.items()
            if point.payload.get("paper_id") != paper_id
        }


class QdrantVectorStore:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None

    def _get_client(self):
        if self._client is None:
            from qdrant_client import AsyncQdrantClient

            self._client = AsyncQdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
            )
        return self._client

    async def _ensure_collection(self) -> None:
        from qdrant_client.http import models

        client = self._get_client()
        collections = await client.get_collections()
        names = {collection.name for collection in collections.collections}
        if self.settings.qdrant_collection not in names:
            await client.create_collection(
                collection_name=self.settings.qdrant_collection,
                vectors_config=models.VectorParams(
                    size=self.settings.embedding_dimension,
                    distance=models.Distance.COSINE,
                ),
            )

    async def upsert(self, points: list[VectorPoint]) -> None:
        if not points:
            return
        from qdrant_client.http import models

        await self._ensure_collection()
        await self._get_client().upsert(
            collection_name=self.settings.qdrant_collection,
            points=[
                models.PointStruct(id=point.id, vector=point.vector, payload=point.payload)
                for point in points
            ],
        )

    async def search(self, vector: list[float], *, limit: int, filters: dict | None = None) -> list[VectorHit]:
        from qdrant_client.http import models

        await self._ensure_collection()
        qdrant_filter = None
        if filters:
            qdrant_filter = models.Filter(
                must=[
                    models.FieldCondition(key=key, match=models.MatchValue(value=value))
                    for key, value in filters.items()
                ]
            )
        results = await self._get_client().search(
            collection_name=self.settings.qdrant_collection,
            query_vector=vector,
            query_filter=qdrant_filter,
            limit=limit,
        )
        return [VectorHit(id=str(hit.id), score=float(hit.score), payload=hit.payload or {}) for hit in results]

    async def delete_by_paper(self, paper_id: str) -> None:
        from qdrant_client.http import models

        await self._ensure_collection()
        await self._get_client().delete(
            collection_name=self.settings.qdrant_collection,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[models.FieldCondition(key="paper_id", match=models.MatchValue(value=paper_id))]
                )
            ),
        )


def create_vector_store(settings: Settings) -> VectorStore:
    if settings.vector_backend == "qdrant":
        return QdrantVectorStore(settings)
    return InMemoryVectorStore()


def _cosine(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    dot = sum(left[i] * right[i] for i in range(size))
    left_norm = math.sqrt(sum(value * value for value in left[:size])) or 1.0
    right_norm = math.sqrt(sum(value * value for value in right[:size])) or 1.0
    return dot / (left_norm * right_norm)
