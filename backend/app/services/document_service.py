"""Document service — orchestrates ingestion + PostgreSQL record-keeping."""
from datetime import UTC, datetime

import structlog

from app.db.postgres import get_pool
from app.ingestion.orchestrator import ingest_file, ingest_web_url
from app.utils.id_generator import new_id
from app.vectorstore.chroma_store import ChromaVectorStore

logger = structlog.get_logger()


async def ingest_document_file(
    file_bytes: bytes,
    filename: str,
    content_type: str | None,
    client_id: str,
) -> dict:
    """Ingest a document file (PDF / DOCX / TXT / MD).

    1. Parse + chunk + embed + store in ChromaDB.
    2. Write a metadata record to PostgreSQL.
    Returns {"doc_id": str, "chunk_count": int}.
    """
    doc_id = new_id()
    log = logger.bind(doc_id=doc_id, client_id=client_id, filename=filename)

    chunk_count = await ingest_file(
        file_bytes=file_bytes,
        doc_id=doc_id,
        client_id=client_id,
        filename=filename,
        content_type=content_type,
    )

    source_type = filename.rsplit(".", 1)[-1].lower() if "." in filename else "file"
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO documents (id, client_id, filename, chunk_count, type, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            doc_id, client_id, filename, chunk_count, source_type, datetime.now(UTC),
        )

    log.info("document_service.ingest.done", chunk_count=chunk_count)
    return {"doc_id": doc_id, "chunk_count": chunk_count}


async def ingest_pdf(file_bytes: bytes, filename: str, client_id: str) -> dict:
    """Convenience wrapper kept for backward compatibility."""
    return await ingest_document_file(file_bytes, filename, "application/pdf", client_id)


async def ingest_url(url: str, client_id: str) -> dict:
    """Ingest a public web URL."""
    doc_id = new_id()
    log = logger.bind(doc_id=doc_id, client_id=client_id, url=url)

    chunk_count = await ingest_web_url(url=url, doc_id=doc_id, client_id=client_id)

    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO documents (id, client_id, source_url, chunk_count, type, created_at)
            VALUES ($1, $2, $3, $4, 'url', $5)
            """,
            doc_id, client_id, url, chunk_count, datetime.now(UTC),
        )

    log.info("document_service.url.done", chunk_count=chunk_count)
    return {"doc_id": doc_id, "chunk_count": chunk_count}


async def list_documents(client_id: str, skip: int = 0, limit: int = 50) -> list[dict]:
    """Return document records for *client_id*, newest first."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id AS doc_id, filename, source_url, chunk_count, type, created_at
            FROM documents
            WHERE client_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """,
            client_id, limit, skip,
        )
    result = []
    for row in rows:
        d = dict(row)
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
        result.append(d)
    return result


async def delete_document(doc_id: str, client_id: str) -> dict:
    """Delete a document from ChromaDB and PostgreSQL.

    Returns {"deleted": True, "doc_id": doc_id, "chunks_removed": int}.
    """
    log = logger.bind(doc_id=doc_id, client_id=client_id)

    # 1. Remove vectors from ChromaDB
    store = ChromaVectorStore(client_id)
    chunks_removed = store.delete_by_doc_id(doc_id)

    # 2. Remove metadata record from PostgreSQL
    pool = get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM documents WHERE id = $1 AND client_id = $2",
            doc_id, client_id,
        )
    # asyncpg returns "DELETE N" as a string
    if result == "DELETE 0":
        log.warning("document_service.delete.not_found")

    log.info("document_service.delete.done", chunks_removed=chunks_removed)
    return {"deleted": True, "doc_id": doc_id, "chunks_removed": chunks_removed}
