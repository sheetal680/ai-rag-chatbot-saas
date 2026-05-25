"""Semantic retrieval layer.

Turns a user question into a ranked list of relevant text chunks:
  1. Embed the question
  2. Vector search (ChromaDB cosine similarity)
  3. Filter chunks below the score threshold
  4. Optionally de-duplicate by doc_id (MMR-lite)

Nothing here knows about HTTP or databases — only embeddings + vectorstore.
"""
from dataclasses import dataclass, field

import structlog

from app.embeddings import get_embedder
from app.vectorstore.chroma_store import ChromaVectorStore, VectorSearchResult

logger = structlog.get_logger()

# all-MiniLM-L6-v2 produces lower absolute cosine scores than large cloud
# embedding models. 0.20 is the practical floor for this model — anything
# below is genuinely unrelated. Raise to 0.30 if you start seeing irrelevant
# chunks appear in answers.
DEFAULT_SCORE_THRESHOLD = 0.20

# Maximum chunks returned to the LLM prompt.
DEFAULT_TOP_K = 6


@dataclass
class RetrievedChunk:
    text: str
    score: float
    metadata: dict = field(default_factory=dict)
    doc_id: str | None = None

    @classmethod
    def from_vector_result(cls, vr: VectorSearchResult) -> "RetrievedChunk":
        return cls(
            text=vr.text,
            score=vr.score,
            metadata=vr.metadata,
            doc_id=vr.doc_id,
        )


async def retrieve(
    question: str,
    client_id: str,
    top_k: int = DEFAULT_TOP_K,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    deduplicate: bool = True,
) -> list[RetrievedChunk]:
    """Embed *question* and return the most relevant stored chunks.

    Args:
        question:         Raw user question string.
        client_id:        Tenant identifier — searches only that tenant's collection.
        top_k:            Maximum number of chunks to return after filtering.
        score_threshold:  Minimum cosine similarity to include a chunk [0, 1].
        deduplicate:      When True, keep at most one chunk per source document
                          for the lower-ranked results, preserving diversity.

    Returns:
        List of RetrievedChunk ordered by score (highest first).
        Empty list when no chunk passes the threshold.
    """
    log = logger.bind(client_id=client_id)

    # 1. Embed the query
    embedder = get_embedder()
    query_vec = await embedder.embed_query(question)
    log.debug("retrieval.embedded_query")

    # 2. Vector search — fetch extra candidates for threshold filtering
    store = ChromaVectorStore(client_id)
    candidates = store.query(query_vec, top_k=top_k * 2)
    log.debug("retrieval.candidates", count=len(candidates))

    # 3. Threshold filter
    above_threshold = [
        RetrievedChunk.from_vector_result(c)
        for c in candidates
        if c.score >= score_threshold
    ]
    log.info(
        "retrieval.filtered",
        total_candidates=len(candidates),
        above_threshold=len(above_threshold),
        threshold=score_threshold,
    )

    if not above_threshold:
        return []

    # 4. Optional diversity: keep at most 2 chunks per document
    if deduplicate:
        above_threshold = _deduplicate(above_threshold, max_per_doc=2)

    return above_threshold[:top_k]


def _deduplicate(
    chunks: list[RetrievedChunk],
    max_per_doc: int = 2,
) -> list[RetrievedChunk]:
    """Limit chunks from the same document to *max_per_doc* (by score order)."""
    doc_counts: dict[str | None, int] = {}
    result: list[RetrievedChunk] = []
    for chunk in chunks:
        count = doc_counts.get(chunk.doc_id, 0)
        if count < max_per_doc:
            result.append(chunk)
            doc_counts[chunk.doc_id] = count + 1
    return result
