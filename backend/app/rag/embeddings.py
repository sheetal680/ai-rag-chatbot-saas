"""Backward-compatibility shim.

New code should import from app.embeddings directly.
This module is kept so any code that already imports
embed_texts / embed_query from here continues to work.
"""
from app.embeddings import get_embedder as _get


async def embed_texts(texts: list[str]) -> list[list[float]]:
    return await _get().embed_texts(texts)


async def embed_query(query: str) -> list[float]:
    return await _get().embed_query(query)
