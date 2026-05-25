"""Integration tests for the RAG pipeline.

These tests run the full ingest → query cycle using ChromaDB in-memory
(no persistent disk write) and a mocked LLM so no API key is required.

Run with:
  pytest tests/integration/test_rag_pipeline.py -v
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


SAMPLE_TEXT = """
Luminary Homes Refund Policy

Customers who cancel their booking within 48 hours of purchase are entitled
to a full refund, no questions asked. Cancellations made between 48 hours
and 7 days before the booking date qualify for a 50% refund. After 7 days,
no refund is available unless the booking is cancelled due to an emergency
verified by our support team.

For emergency refund requests, contact support@luminaryhomes.com with
relevant documentation.
""".strip()


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def chroma_client():
    """In-memory ChromaDB client so nothing is persisted to disk."""
    import chromadb
    return chromadb.EphemeralClient()


@pytest.fixture(scope="module")
def real_embedder():
    """Actual LocalEmbedder backed by a mocked SentenceTransformer.

    We stub _encode_sync to return deterministic 384-dim vectors derived
    from the text hash — no model download required, but the flow is real.
    """
    import hashlib
    import numpy as np
    from app.embeddings.local_embedder import LocalEmbedder

    with patch("app.embeddings.local_embedder.SentenceTransformer") as MockST:
        mock_model = MagicMock()

        def fake_encode(texts, **kwargs):
            vectors = []
            for t in texts:
                seed = int(hashlib.md5(t.encode()).hexdigest(), 16) % (2**31)
                rng = np.random.default_rng(seed)
                v = rng.random(384).astype(np.float32)
                v /= np.linalg.norm(v)   # normalize
                vectors.append(v)
            return np.array(vectors)

        mock_model.encode.side_effect = fake_encode
        MockST.return_value = mock_model
        embedder = LocalEmbedder()

    return embedder


# ── Ingest → Query cycle ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ingest_and_retrieve_chunks(chroma_client, real_embedder):
    """Ingest a document, then verify retrieval returns chunks."""
    import app.embeddings as emb_pkg
    import app.db.chromadb as chroma_db

    client_id = "integration_tenant"
    doc_id = "integ-doc-001"

    # Override singletons
    emb_pkg._embedder = real_embedder
    original_client = chroma_db._client
    chroma_db._client = chroma_client

    try:
        from app.rag.pipeline import ingest_document, query_rag

        chunk_count = await ingest_document(
            text=SAMPLE_TEXT,
            doc_id=doc_id,
            client_id=client_id,
            metadata={"filename": "refund_policy.txt"},
        )
        assert chunk_count >= 1, "Expected at least one chunk to be stored"

        results = await query_rag(
            question="What is the refund policy?",
            client_id=client_id,
        )
        assert isinstance(results, list)
        # With deterministic (but non-semantic) embeddings, we may not find
        # relevant results by score — just verify the shape is correct.
        for r in results:
            assert "text" in r
            assert "score" in r
            assert "metadata" in r
    finally:
        chroma_db._client = original_client
        emb_pkg._embedder = None


@pytest.mark.asyncio
async def test_ingest_stores_expected_metadata(chroma_client, real_embedder):
    """Verify chunk metadata contains doc_id and filename after ingestion."""
    import app.embeddings as emb_pkg
    import app.db.chromadb as chroma_db
    from app.vectorstore.chroma_store import ChromaVectorStore

    client_id = "meta_tenant"
    doc_id = "meta-doc-001"

    emb_pkg._embedder = real_embedder
    original_client = chroma_db._client
    chroma_db._client = chroma_client

    try:
        from app.rag.pipeline import ingest_document

        await ingest_document(
            text="Short document for metadata test.",
            doc_id=doc_id,
            client_id=client_id,
            metadata={"filename": "meta_test.txt"},
        )

        store = ChromaVectorStore(client_id)
        assert store.count() >= 1

        raw = store._collection.get(include=["metadatas"])
        for meta in raw["metadatas"]:
            assert meta["doc_id"] == doc_id
            assert meta["filename"] == "meta_test.txt"
            assert "chunk_index" in meta
            assert "total_chunks" in meta
    finally:
        chroma_db._client = original_client
        emb_pkg._embedder = None


@pytest.mark.asyncio
async def test_delete_removes_all_chunks(chroma_client, real_embedder):
    """After delete_by_doc_id, the store should have no chunks for that doc."""
    import app.embeddings as emb_pkg
    import app.db.chromadb as chroma_db
    from app.vectorstore.chroma_store import ChromaVectorStore

    client_id = "delete_tenant"
    doc_id = "delete-doc-001"

    emb_pkg._embedder = real_embedder
    original_client = chroma_db._client
    chroma_db._client = chroma_client

    try:
        from app.rag.pipeline import ingest_document

        await ingest_document(
            text="Document that will be deleted " * 10,
            doc_id=doc_id,
            client_id=client_id,
        )

        store = ChromaVectorStore(client_id)
        before = store.count()
        assert before >= 1

        deleted = store.delete_by_doc_id(doc_id)
        assert deleted >= 1
        assert store.count() == before - deleted
    finally:
        chroma_db._client = original_client
        emb_pkg._embedder = None


@pytest.mark.asyncio
async def test_query_rag_empty_store_returns_empty(chroma_client, real_embedder):
    """Querying an empty (per-client) collection returns an empty list."""
    import app.embeddings as emb_pkg
    import app.db.chromadb as chroma_db

    emb_pkg._embedder = real_embedder
    original_client = chroma_db._client
    chroma_db._client = chroma_client

    try:
        from app.rag.pipeline import query_rag

        results = await query_rag(
            question="Who are you?",
            client_id="empty_tenant_xyz_999",
        )
        assert results == []
    finally:
        chroma_db._client = original_client
        emb_pkg._embedder = None


# ── Document API endpoints (via TestClient) ───────────────────────────────────

@pytest.mark.asyncio
async def test_upload_document_api_stores_chunks(chroma_client, real_embedder):
    """POST /api/v1/documents/upload ingests the file and returns chunk_count."""
    import app.embeddings as emb_pkg
    import app.db.chromadb as chroma_db
    from app.db.postgres import get_pool

    emb_pkg._embedder = real_embedder
    original_client = chroma_db._client
    chroma_db._client = chroma_client

    # Mock the PostgreSQL pool — we don't need real DB for this test
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    mock_conn.execute = AsyncMock()
    mock_pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)

    try:
        with (
            patch("app.db.postgres.connect_db", new_callable=AsyncMock),
            patch("app.db.postgres.disconnect_db", new_callable=AsyncMock),
            patch("app.db.postgres.ensure_tables", new_callable=AsyncMock),
            patch("app.db.postgres.get_pool", return_value=mock_pool),
            patch("app.services.document_service.get_pool", return_value=mock_pool),
        ):
            from fastapi.testclient import TestClient
            from main import app

            txt_content = SAMPLE_TEXT.encode("utf-8")
            with TestClient(app, raise_server_exceptions=True) as client:
                # Bypass auth for the test — must include client_id so the route
                # can namespace the ChromaDB collection correctly.
                with patch(
                    "app.core.security.get_current_user",
                    return_value={"sub": "test", "client_id": "api_test_tenant"},
                ):
                    resp = client.post(
                        "/api/v1/documents/upload",
                        files={"file": ("policy.txt", txt_content, "text/plain")},
                    )

            assert resp.status_code == 200
            data = resp.json()
            assert "doc_id" in data
            assert data["chunk_count"] >= 1
    finally:
        chroma_db._client = original_client
        emb_pkg._embedder = None
