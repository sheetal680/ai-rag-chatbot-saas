"""Unit tests for the local sentence-transformers embedder.

sentence_transformers is mocked at the sys.modules level so no installation
or model download is needed when running unit tests.
"""
import sys
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

# ── Stub sentence_transformers before any app module imports it ───────────────
_st_stub = MagicMock()
sys.modules.setdefault("sentence_transformers", _st_stub)


# ── Helper ────────────────────────────────────────────────────────────────────

def _make_embedder():
    """Return a LocalEmbedder whose SentenceTransformer model is a MagicMock."""
    mock_model = MagicMock()
    _st_stub.SentenceTransformer.return_value = mock_model

    # Force a fresh import of the module now that the stub is in sys.modules
    if "app.embeddings.local_embedder" in sys.modules:
        del sys.modules["app.embeddings.local_embedder"]

    from app.embeddings.local_embedder import LocalEmbedder
    embedder = LocalEmbedder()
    return embedder, mock_model


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestLocalEmbedder:
    def test_embed_texts_returns_list_of_vectors(self):
        embedder, mock_model = _make_embedder()
        mock_model.encode.return_value = np.array([[0.1] * 384, [0.2] * 384])

        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            embedder.embed_texts(["hello", "world"])
        )

        assert len(result) == 2
        assert len(result[0]) == 384
        assert isinstance(result[0][0], float)

    def test_embed_texts_empty_returns_empty(self):
        embedder, mock_model = _make_embedder()

        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            embedder.embed_texts([])
        )

        assert result == []
        mock_model.encode.assert_not_called()

    def test_embed_query_returns_single_vector(self):
        embedder, mock_model = _make_embedder()
        mock_model.encode.return_value = np.array([[0.5] * 384])

        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            embedder.embed_query("What is the refund policy?")
        )

        assert len(result) == 384
        assert isinstance(result[0], float)

    def test_embed_texts_calls_encode_with_normalize(self):
        embedder, mock_model = _make_embedder()
        mock_model.encode.return_value = np.array([[0.1] * 384])

        import asyncio
        asyncio.get_event_loop().run_until_complete(
            embedder.embed_texts(["test"])
        )

        call_kwargs = mock_model.encode.call_args[1]
        assert call_kwargs["normalize_embeddings"] is True

    def test_embed_texts_vectors_are_lists_not_numpy(self):
        embedder, mock_model = _make_embedder()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])

        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            embedder.embed_texts(["single"])
        )

        assert isinstance(result[0], list)
        assert isinstance(result[0][0], float)


@pytest.mark.asyncio
async def test_embedder_singleton_is_reused():
    """get_embedder() returns the same instance on repeated calls."""
    import app.embeddings as emb_pkg

    # Reset singleton so we get a clean slate
    emb_pkg._embedder = None
    if "app.embeddings.local_embedder" in sys.modules:
        del sys.modules["app.embeddings.local_embedder"]

    try:
        e1 = emb_pkg.get_embedder()
        e2 = emb_pkg.get_embedder()
        assert e1 is e2
    finally:
        emb_pkg._embedder = None
