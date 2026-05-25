"""RAG package public API.

Stable entry points consumed by services/ and scripts/:
  - ingest_document(text, doc_id, client_id, metadata) -> int
  - query_rag(question, client_id, top_k)              -> list[dict]
"""
from app.rag.pipeline import ingest_document, query_rag

__all__ = ["ingest_document", "query_rag"]
