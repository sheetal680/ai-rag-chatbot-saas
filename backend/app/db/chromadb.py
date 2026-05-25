from __future__ import annotations

import chromadb
from chromadb import Collection

from app.core.config import settings

_client: chromadb.PersistentClient | None = None


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


def get_collection(client_id: str) -> Collection:
    """Each tenant gets their own ChromaDB collection, namespaced by client_id."""
    chroma = get_chroma_client()
    collection_name = f"{settings.CHROMA_COLLECTION_NAME}_{client_id}"
    return chroma.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},
    )
