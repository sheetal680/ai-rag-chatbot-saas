"""ChromaDB vector store wrapper.

Provides a clean interface for the rest of the app to:
  - Store embedded chunks  (upsert_chunks)
  - Search by vector       (query)
  - Delete a document      (delete_by_doc_id)
  - List indexed doc IDs   (list_doc_ids)
  - Count chunks           (count)

The underlying ChromaDB client lives in app/db/chromadb.py.
Each client_id gets its own collection, namespaced automatically.
"""
from dataclasses import dataclass, field

import structlog

from app.db.chromadb import get_collection
from app.utils.validators import sanitize_client_id

logger = structlog.get_logger()


@dataclass
class VectorSearchResult:
    text: str
    score: float          # cosine similarity in [0, 1]; higher = more relevant
    metadata: dict = field(default_factory=dict)
    doc_id: str | None = None

    def __post_init__(self) -> None:
        self.doc_id = self.metadata.get("doc_id")


class ChromaVectorStore:
    """Thread-safe, per-client ChromaDB wrapper."""

    def __init__(self, client_id: str) -> None:
        self._client_id = sanitize_client_id(client_id)
        self._log = logger.bind(client_id=self._client_id)

    @property
    def _collection(self):
        return get_collection(self._client_id)

    # ── Write ────────────────────────────────────────────────────────────────

    def upsert_chunks(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        """Upsert (insert-or-update) chunks into the collection."""
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        self._log.info("vectorstore.upsert", count=len(ids))

    def delete_by_doc_id(self, doc_id: str) -> int:
        """Delete all chunks belonging to *doc_id*.

        Returns the number of chunks deleted.
        """
        existing = self._collection.get(where={"doc_id": doc_id}, include=[])
        ids_to_delete = existing["ids"]
        if ids_to_delete:
            self._collection.delete(ids=ids_to_delete)
        self._log.info("vectorstore.delete", doc_id=doc_id, deleted=len(ids_to_delete))
        return len(ids_to_delete)

    # ── Read ─────────────────────────────────────────────────────────────────

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[VectorSearchResult]:
        """Return top-k results ordered by cosine similarity (descending)."""
        try:
            raw = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self.count() or top_k),
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            self._log.warning("vectorstore.query.error", error=str(exc))
            return []

        results: list[VectorSearchResult] = []
        for text, meta, dist in zip(
            raw["documents"][0],
            raw["metadatas"][0],
            raw["distances"][0],
        ):
            # ChromaDB cosine distance is in [0, 2]; similarity = 1 - distance
            score = round(max(0.0, 1.0 - dist), 4)
            results.append(VectorSearchResult(text=text, score=score, metadata=meta))

        return results

    def list_doc_ids(self) -> list[str]:
        """Return unique document IDs that have at least one chunk in the store."""
        result = self._collection.get(include=["metadatas"])
        return list({
            m["doc_id"]
            for m in result["metadatas"]
            if isinstance(m, dict) and "doc_id" in m
        })

    def count(self) -> int:
        """Total number of chunks stored for this client."""
        return self._collection.count()
