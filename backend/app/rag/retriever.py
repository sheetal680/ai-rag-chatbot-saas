"""Backward-compatibility shim.

New code should use app.vectorstore.ChromaVectorStore directly.
"""
from app.vectorstore.chroma_store import ChromaVectorStore


def store_chunks(
    client_id: str,
    ids: list[str],
    embeddings: list[list[float]],
    texts: list[str],
    metadatas: list[dict],
) -> None:
    ChromaVectorStore(client_id).upsert_chunks(ids, embeddings, texts, metadatas)


def retrieve_chunks(
    client_id: str,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[dict]:
    results = ChromaVectorStore(client_id).query(query_embedding, top_k)
    return [{"text": r.text, "metadata": r.metadata, "score": r.score} for r in results]
