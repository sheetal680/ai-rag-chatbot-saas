"""Unit tests for ChromaVectorStore.

ChromaDB is mocked — no persistent client or disk I/O needed.
"""
from unittest.mock import MagicMock, patch

import pytest

from app.vectorstore.chroma_store import ChromaVectorStore, VectorSearchResult


def _mock_collection():
    col = MagicMock()
    col.count.return_value = 10
    return col


def _store(client_id: str = "tenant_a") -> tuple[ChromaVectorStore, MagicMock]:
    col = _mock_collection()
    with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
        store = ChromaVectorStore(client_id)
    store._get_col = lambda: col   # cache the mock for assertions
    return store, col


# ── VectorSearchResult ────────────────────────────────────────────────────────

class TestVectorSearchResult:
    def test_doc_id_extracted_from_metadata(self):
        r = VectorSearchResult(text="hi", score=0.8, metadata={"doc_id": "d1"})
        assert r.doc_id == "d1"

    def test_doc_id_none_when_missing(self):
        r = VectorSearchResult(text="hi", score=0.8, metadata={})
        assert r.doc_id is None

    def test_score_preserved(self):
        r = VectorSearchResult(text="content", score=0.95, metadata={})
        assert r.score == 0.95


# ── upsert_chunks ─────────────────────────────────────────────────────────────

class TestUpsertChunks:
    def test_calls_collection_upsert(self):
        store, col = _store()
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            store.upsert_chunks(
                ids=["id1", "id2"],
                embeddings=[[0.1] * 384, [0.2] * 384],
                documents=["chunk a", "chunk b"],
                metadatas=[{"doc_id": "d1"}, {"doc_id": "d1"}],
            )
        col.upsert.assert_called_once()
        call_kwargs = col.upsert.call_args[1]
        assert call_kwargs["ids"] == ["id1", "id2"]
        assert len(call_kwargs["embeddings"]) == 2

    def test_upsert_single_chunk(self):
        store, col = _store()
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            store.upsert_chunks(["only"], [[0.1] * 384], ["text"], [{"doc_id": "x"}])
        col.upsert.assert_called_once()


# ── query ─────────────────────────────────────────────────────────────────────

class TestQuery:
    def _make_raw_response(self, n: int = 2):
        texts = [f"chunk {i}" for i in range(n)]
        metas = [{"doc_id": f"doc{i}"} for i in range(n)]
        dists = [0.1 * (i + 1) for i in range(n)]   # distances, not similarities
        return {"documents": [texts], "metadatas": [metas], "distances": [dists]}

    def test_returns_list_of_results(self):
        store, col = _store()
        col.query.return_value = self._make_raw_response(3)
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            results = store.query([0.1] * 384, top_k=3)
        assert len(results) == 3
        assert all(isinstance(r, VectorSearchResult) for r in results)

    def test_score_is_1_minus_distance(self):
        store, col = _store()
        col.query.return_value = {"documents": [["text"]], "metadatas": [
            [{"doc_id": "d"}]], "distances": [[0.2]]}
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            results = store.query([0.0] * 384, top_k=1)
        assert results[0].score == pytest.approx(0.8, abs=1e-4)

    def test_empty_collection_returns_empty(self):
        store, col = _store()
        col.count.return_value = 0
        col.query.return_value = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            results = store.query([0.0] * 384, top_k=5)
        assert results == []

    def test_query_exception_returns_empty(self):
        store, col = _store()
        col.query.side_effect = RuntimeError("chroma error")
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            results = store.query([0.0] * 384, top_k=5)
        assert results == []


# ── delete_by_doc_id ──────────────────────────────────────────────────────────

class TestDeleteByDocId:
    def test_deletes_found_ids(self):
        store, col = _store()
        col.get.return_value = {"ids": ["id1", "id2"]}
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            deleted = store.delete_by_doc_id("doc1")
        assert deleted == 2
        col.delete.assert_called_once_with(ids=["id1", "id2"])

    def test_delete_returns_zero_when_not_found(self):
        store, col = _store()
        col.get.return_value = {"ids": []}
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            deleted = store.delete_by_doc_id("ghost")
        assert deleted == 0
        col.delete.assert_not_called()


# ── list_doc_ids / count ──────────────────────────────────────────────────────

class TestListAndCount:
    def test_list_doc_ids_deduplicates(self):
        store, col = _store()
        col.get.return_value = {
            "metadatas": [
                {"doc_id": "a"},
                {"doc_id": "a"},
                {"doc_id": "b"},
                {},   # missing doc_id — should be skipped
            ]
        }
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            ids = store.list_doc_ids()
        assert set(ids) == {"a", "b"}

    def test_count_delegates_to_collection(self):
        store, col = _store()
        col.count.return_value = 42
        with patch("app.vectorstore.chroma_store.get_collection", return_value=col):
            assert store.count() == 42
