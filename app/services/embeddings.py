import asyncio
import hashlib
import math
from collections.abc import Sequence

from app.core.config import Settings


class EmbeddingService:
    """Async wrapper around sentence-transformers with a deterministic local fallback."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.settings.embedding_model_name)
        return self._model

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            model = await asyncio.to_thread(self._load_model)
            vectors = await asyncio.to_thread(
                model.encode,
                list(texts),
                batch_size=self.settings.embedding_batch_size,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return [vector.tolist() for vector in vectors]
        except Exception:
            return [self._hash_embedding(text) for text in texts]

    async def embed_query(self, query: str) -> list[float]:
        return (await self.embed_texts([query]))[0]

    def _hash_embedding(self, text: str) -> list[float]:
        dimension = self.settings.embedding_dimension
        vector = [0.0] * dimension
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
