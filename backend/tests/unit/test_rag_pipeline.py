"""Unit tests for the RAG pipeline layer.

All external calls (Groq/Gemini LLM, ChromaDB) are mocked — no API keys required.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.chunker import chunk_text


# ── Chunker ───────────────────────────────────────────────────────────────────

def test_ingest_empty_text_returns_zero_chunks():
    chunks = chunk_text("")
    assert chunks == []


def test_chunk_count_grows_with_text_length():
    short_chunks = chunk_text("word " * 20)
    long_chunks = chunk_text("word " * 500)
    assert len(long_chunks) > len(short_chunks)


# ── Prompt builder ────────────────────────────────────────────────────────────

def test_build_rag_messages_structure():
    from app.prompts.builder import build_rag_messages
    from app.retrieval.semantic import RetrievedChunk

    chunks = [RetrievedChunk(text="Paris is the capital of France.", score=0.9)]
    msgs = build_rag_messages("What is the capital of France?", chunks)

    assert msgs[0]["role"] == "system"
    assert "Paris" in msgs[0]["content"]
    assert msgs[-1]["role"] == "user"
    assert "capital" in msgs[-1]["content"]


def test_build_rag_messages_includes_history():
    from app.prompts.builder import build_rag_messages
    from app.retrieval.semantic import RetrievedChunk

    chunks = [RetrievedChunk(text="Some context.", score=0.8)]
    history = [
        {"role": "user", "content": "previous question"},
        {"role": "assistant", "content": "previous answer"},
    ]
    msgs = build_rag_messages("new question", chunks, history)

    roles = [m["role"] for m in msgs]
    assert "user" in roles
    assert "assistant" in roles


def test_no_context_response_is_non_empty():
    from app.prompts.templates import NO_CONTEXT_RESPONSE
    assert len(NO_CONTEXT_RESPONSE) > 20


# ── Retrieval deduplication ───────────────────────────────────────────────────

def test_deduplication_limits_per_doc():
    from app.retrieval.semantic import _deduplicate, RetrievedChunk

    chunks = [
        RetrievedChunk("a", 0.9, {"doc_id": "doc1"}, "doc1"),
        RetrievedChunk("b", 0.8, {"doc_id": "doc1"}, "doc1"),
        RetrievedChunk("c", 0.7, {"doc_id": "doc1"}, "doc1"),
        RetrievedChunk("d", 0.6, {"doc_id": "doc2"}, "doc2"),
    ]
    result = _deduplicate(chunks, max_per_doc=2)
    doc1_chunks = [c for c in result if c.doc_id == "doc1"]
    assert len(doc1_chunks) == 2  # capped at max_per_doc
    assert any(c.doc_id == "doc2" for c in result)


# ── Ingest pipeline (mocked) ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ingest_document_calls_store():
    mock_embed = AsyncMock(return_value=[[0.1] * 384])
    mock_upsert = MagicMock()

    with (
        patch("app.rag.pipeline.get_embedder") as mock_get_embedder,
        patch("app.rag.pipeline.ChromaVectorStore") as mock_store_cls,
    ):
        embedder = MagicMock()
        embedder.embed_texts = mock_embed
        mock_get_embedder.return_value = embedder

        store_instance = MagicMock()
        store_instance.upsert_chunks = mock_upsert
        mock_store_cls.return_value = store_instance

        from app.rag.pipeline import ingest_document
        count = await ingest_document("Short test text.", "doc123", "client_a")

    assert count >= 1
    assert mock_upsert.called


# ── Vectorstore ───────────────────────────────────────────────────────────────

def test_vector_search_result_extracts_doc_id():
    from app.vectorstore.chroma_store import VectorSearchResult
    r = VectorSearchResult(text="hello", score=0.9, metadata={"doc_id": "d1"})
    assert r.doc_id == "d1"


def test_vector_search_result_missing_doc_id():
    from app.vectorstore.chroma_store import VectorSearchResult
    r = VectorSearchResult(text="hello", score=0.7, metadata={})
    assert r.doc_id is None
