"""High-level ingestion coordinator.

Accepts raw bytes (or a URL) plus metadata, and drives the full pipeline:
  parse → chunk → embed → store in ChromaDB

Callers (services/document_service.py) never touch parsers or rag/ directly.
"""
import structlog

from app.parsers import parse_file, get_parser
from app.parsers.web_parser import parse_url
from app.rag.pipeline import ingest_document

logger = structlog.get_logger()


async def ingest_file(
    file_bytes: bytes,
    doc_id: str,
    client_id: str,
    filename: str,
    content_type: str | None = None,
) -> int:
    """Parse any supported document type → chunk → embed → store.

    Supported: PDF, DOCX, TXT, Markdown.
    Returns the number of chunks stored.
    """
    log = logger.bind(doc_id=doc_id, client_id=client_id, filename=filename)
    log.info("ingestion.file.start", content_type=content_type)

    # 1. Parse to plain text
    text = parse_file(file_bytes, content_type=content_type, filename=filename)
    log.info("ingestion.parsed", text_length=len(text))

    if not text.strip():
        log.warning("ingestion.empty_document")
        raise ValueError(f"No text could be extracted from '{filename}'.")

    # 2. Detect file type label for metadata
    source_type = _detect_type(content_type, filename)

    # 3. Ingest into vector store
    chunk_count = await ingest_document(
        text=text,
        doc_id=doc_id,
        client_id=client_id,
        metadata={"filename": filename, "source": source_type},
    )
    log.info("ingestion.file.done", chunk_count=chunk_count)
    return chunk_count


async def ingest_web_url(
    url: str,
    doc_id: str,
    client_id: str,
) -> int:
    """Fetch a URL → parse → chunk → embed → store.

    Returns the number of chunks stored.
    """
    log = logger.bind(doc_id=doc_id, client_id=client_id, url=url)
    log.info("ingestion.url.start")

    text = await parse_url(url)
    log.info("ingestion.url.parsed", text_length=len(text))

    if not text.strip():
        log.warning("ingestion.url.empty")
        raise ValueError(f"No text could be extracted from URL: {url}")

    chunk_count = await ingest_document(
        text=text,
        doc_id=doc_id,
        client_id=client_id,
        metadata={"source_url": url, "source": "url"},
    )
    log.info("ingestion.url.done", chunk_count=chunk_count)
    return chunk_count


def _detect_type(content_type: str | None, filename: str | None) -> str:
    ext_map = {"pdf": "pdf", "docx": "docx", "txt": "txt", "md": "markdown"}
    if filename and "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        return ext_map.get(ext, "file")
    return "file"
