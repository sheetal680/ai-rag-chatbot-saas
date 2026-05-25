"""RAG pipeline entry points.

Two public functions used by the rest of the app:
  - ingest_document(text, doc_id, client_id, metadata) -> int
  - query_rag(question, client_id, top_k)             -> list[dict]

Both delegate to the new app/embeddings/, app/vectorstore/, and
app/retrieval/ modules. The functions here exist as stable interfaces
so services/ and tests/ don't need to know about the internal modules.
"""
import structlog

from app.embeddings import get_embedder
from app.rag.chunker import chunk_text
from app.retrieval.semantic import retrieve, RetrievedChunk
from app.vectorstore.chroma_store import ChromaVectorStore

logger = structlog.get_logger()


async def ingest_document(
    text: str,
    doc_id: str,
    client_id: str,
    metadata: dict | None = None,
) -> int:
    """Chunk → embed → store in ChromaDB. Returns number of chunks stored."""
    log = logger.bind(doc_id=doc_id, client_id=client_id)
    log.info("pipeline.ingest.start", text_length=len(text))

    # 1. Chunk
    base_meta = {**(metadata or {}), "doc_id": doc_id, "client_id": client_id}
    chunks = chunk_text(text, metadata=base_meta)
    log.info("pipeline.chunked", chunk_count=len(chunks))

    if not chunks:
        log.warning("pipeline.ingest.empty_text")
        return 0

    # 2. Embed
    embedder = get_embedder()
    texts = [c.page_content for c in chunks]
    vectors = await embedder.embed_texts(texts)
    log.info("pipeline.embedded")

    # 3. Store
    chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [c.metadata for c in chunks]
    store = ChromaVectorStore(client_id)
    store.upsert_chunks(
        ids=chunk_ids,
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas,
    )
    log.info("pipeline.ingest.done", stored=len(chunks))
    return len(chunks)


async def query_rag(
    question: str,
    client_id: str,
    top_k: int = 5,
) -> list[dict]:
    """Embed query → retrieve top-k chunks.

    Returns a list of dicts with keys: text, metadata, score.
    Preserved for backward compatibility with chat_service.py.
    """
    chunks: list[RetrievedChunk] = await retrieve(
        question=question,
        client_id=client_id,
        top_k=top_k,
    )
    return [{"text": c.text, "metadata": c.metadata, "score": c.score} for c in chunks]
