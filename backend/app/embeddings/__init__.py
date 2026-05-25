from __future__ import annotations

_embedder = None


def get_embedder():
    """Return the process-level embedder singleton (lazy — loads on first call)."""
    global _embedder
    if _embedder is None:
        from app.embeddings.local_embedder import LocalEmbedder
        _embedder = LocalEmbedder()
    return _embedder
