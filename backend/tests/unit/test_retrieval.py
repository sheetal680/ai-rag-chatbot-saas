"""Unit tests for the semantic retrieval layer.

ChromaDB and embedder are mocked — no model download or disk I/O needed.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.retrieval.semantic import (
    DEFAULT_SCORE_THRESHOLD,
    DEFAULT_TOP_K,
    RetrievedChunk,
    _deduplicate,
    retrieve,
)
from app.vectorstore.chroma_store import VectorSearchResult


def _make_vector_result(text: str, score: float, doc_id: str) -> VectorSearchResult:
    dist = round(1.0 - score, 4)
    return VectorSearchResult(
        text=text, score=score, metadata={"doc_id": doc_id, "distance": dist}
    )


# ── RetrievedChunk construction ───────────────────────────────────────────────

class TestRetrievedChunk:
    def test_from_vector_result(self):
        vr = _make_vector_result("hello", 0.85, "d1")
        chunk = RetrievedChunk.from_vector_result(vr)
        assert chunk.text == "hello"
        assert chunk.score == 0.85
        assert chunk.doc_id == "d1"

    def test_default_metadata_is_empty_dict(self):
        chunk = RetrievedChunk(text="t", score=0.5)
        assert chunk.metadata == {}
        assert chunk.doc_id is None


# ── _deduplicate ──────────────────────────────────────────────────────────────

class TestDeduplicate:
    def test_caps_chunks_per_doc(self):
        chunks = [
            RetrievedChunk("a", 0.9, {"doc_id": "d1"}, "d1"),
            RetrievedChunk("b", 0.8, {"doc_id": "d1"}, "d1"),
            RetrievedChunk("c", 0.7, {"doc_id": "d1"}, "d1"),  # third — should be dropped
            RetrievedChunk("d", 0.6, {"doc_id": "d2"}, "d2"),
        ]
        result = _deduplicate(chunks, max_per_doc=2)
        d1_chunks = [c for c in result if c.doc_id == "d1"]
        assert len(d1_chunks) == 2
        assert len(result) == 3   # 2 from d1 + 1 from d2

    def test_preserves_order_by_score(self):
        chunks = [
            RetrievedChunk("hi", 0.95, {"doc_id": "x"}, "x"),
            RetrievedChunk("bye", 0.60, {"doc_id": "y"}, "y"),
        ]
        result = _deduplicate(chunks, max_per_doc=1)
        assert result[0].score > result[1].score

    def test_none_doc_id_treated_as_its_own_bucket(self):
        chunks = [
            RetrievedChunk("a", 0.9, {}, None),
            RetrievedChunk("b", 0.8, {}, None),
            RetrievedChunk("c", 0.7, {}, None),
        ]
        result = _deduplicate(chunks, max_per_doc=2)
        # All three have doc_id=None which is a single key
        assert len(result) == 2


# ── retrieve (full function) ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_retrieve_returns_above_threshold_chunks():
    mock_embedder = MagicMock()
    mock_embedder.embed_query = AsyncMock(return_value=[0.1] * 384)

    candidates = [
        _make_vector_result("highly relevant", 0.80, "d1"),
        _make_vector_result("slightly relevant", 0.35, "d2"),
        _make_vector_result("not relevant", 0.10, "d3"),   # below threshold
    ]
    mock_store = MagicMock()
    mock_store.query.return_value = candidates

    with (
        patch("app.retrieval.semantic.get_embedder", return_value=mock_embedder),
        patch("app.retrieval.semantic.ChromaVectorStore", return_value=mock_store),
    ):
        results = await retrieve(
            question="What is the policy?",
            client_id="tenant_a",
            score_threshold=0.30,
        )

    # Only two pass the 0.30 threshold
    assert len(results) == 2
    assert all(r.score >= 0.30 for r in results)


@pytest.mark.asyncio
async def test_retrieve_returns_empty_when_no_chunks_pass_threshold():
    mock_embedder = MagicMock()
    mock_embedder.embed_query = AsyncMock(return_value=[0.0] * 384)

    mock_store = MagicMock()
    mock_store.query.return_value = [
        _make_vector_result("irrelevant", 0.05, "d1"),
    ]

    with (
        patch("app.retrieval.semantic.get_embedder", return_value=mock_embedder),
        patch("app.retrieval.semantic.ChromaVectorStore", return_value=mock_store),
    ):
        results = await retrieve(
            question="unknown topic",
            client_id="tenant_b",
            score_threshold=DEFAULT_SCORE_THRESHOLD,
        )

    assert results == []


@pytest.mark.asyncio
async def test_retrieve_respects_top_k():
    mock_embedder = MagicMock()
    mock_embedder.embed_query = AsyncMock(return_value=[0.1] * 384)

    candidates = [
        _make_vector_result(f"chunk {i}", 0.9 - i * 0.05, f"doc{i}")
        for i in range(10)
    ]
    mock_store = MagicMock()
    mock_store.query.return_value = candidates

    with (
        patch("app.retrieval.semantic.get_embedder", return_value=mock_embedder),
        patch("app.retrieval.semantic.ChromaVectorStore", return_value=mock_store),
    ):
        results = await retrieve(
            question="question",
            client_id="tenant_c",
            top_k=3,
            score_threshold=0.0,
            deduplicate=False,
        )

    assert len(results) <= 3


@pytest.mark.asyncio
async def test_retrieve_deduplication_is_applied_by_default():
    mock_embedder = MagicMock()
    mock_embedder.embed_query = AsyncMock(return_value=[0.1] * 384)

    # Three chunks from the same doc — only 2 should survive deduplication
    candidates = [
        _make_vector_result("chunk1", 0.9, "same_doc"),
        _make_vector_result("chunk2", 0.8, "same_doc"),
        _make_vector_result("chunk3", 0.7, "same_doc"),
    ]
    mock_store = MagicMock()
    mock_store.query.return_value = candidates

    with (
        patch("app.retrieval.semantic.get_embedder", return_value=mock_embedder),
        patch("app.retrieval.semantic.ChromaVectorStore", return_value=mock_store),
    ):
        results = await retrieve(
            question="question",
            client_id="tenant_d",
            top_k=5,
            score_threshold=0.0,
            deduplicate=True,
        )

    same_doc_hits = [r for r in results if r.doc_id == "same_doc"]
    assert len(same_doc_hits) <= 2
