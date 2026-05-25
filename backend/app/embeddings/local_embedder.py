"""Local sentence-transformers embedder — no API key required.

Uses all-MiniLM-L6-v2 (384-dim, ~80 MB) by default.
The model is downloaded once on first use and cached by the library.
`encode()` is CPU-bound and synchronous; we offload it to a thread pool
via asyncio.to_thread() to keep the FastAPI event loop unblocked.
"""
import asyncio

import structlog
from sentence_transformers import SentenceTransformer

from app.core.config import settings

logger = structlog.get_logger()


class LocalEmbedder:
    """Thread-safe local embedder backed by sentence-transformers."""

    def __init__(self) -> None:
        logger.info("embedder.loading", model=settings.EMBEDDING_MODEL)
        self._model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self._model_name = settings.EMBEDDING_MODEL
        logger.info("embedder.ready", model=self._model_name)

    def _encode_sync(self, texts: list[str]) -> list[list[float]]:
        vectors = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [v.tolist() for v in vectors]

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        result = await asyncio.to_thread(self._encode_sync, texts)
        logger.debug("embedder.embed_texts", count=len(texts), model=self._model_name)
        return result

    async def embed_query(self, query: str) -> list[float]:
        vectors = await self.embed_texts([query])
        return vectors[0]
