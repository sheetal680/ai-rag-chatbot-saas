from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from app.core.security import get_current_user
from app.parsers import SUPPORTED_CONTENT_TYPES, SUPPORTED_EXTENSIONS
from app.services.document_service import (
    delete_document,
    ingest_document_file,
    ingest_url,
    list_documents,
)

router = APIRouter(dependencies=[Depends(get_current_user)])

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# ── Upload any supported document ────────────────────────────────────────────

@router.post("/upload", summary="Upload a document (PDF, DOCX, TXT, MD)")
async def upload_document(
    file: UploadFile = File(...),
    client_id: str = Form(...),
) -> dict:
    """Ingest a file into the vector store.

    Supported formats: PDF, DOCX, TXT, Markdown.
    Max file size: 20 MB.
    """
    ext = (file.filename or "").rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else ""
    if file.content_type not in SUPPORTED_CONTENT_TYPES and ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type '{file.content_type}'. "
                   f"Accepted: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 20 MB limit.")

    try:
        return await ingest_document_file(
            file_bytes=contents,
            filename=file.filename or "upload",
            content_type=file.content_type,
            client_id=client_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


# ── Kept for backward compat ──────────────────────────────────────────────────

@router.post("/upload-pdf", summary="Upload a PDF (legacy endpoint)")
async def upload_pdf(
    file: UploadFile = File(...),
    client_id: str = Form(...),
) -> dict:
    if (file.content_type or "") != "application/pdf" and not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are accepted.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File exceeds 20 MB limit.")

    try:
        return await ingest_document_file(
            file_bytes=contents,
            filename=file.filename or "upload.pdf",
            content_type="application/pdf",
            client_id=client_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))


# ── URL ingestion ─────────────────────────────────────────────────────────────

@router.post("/ingest-url", summary="Ingest a public web URL")
async def ingest_url_endpoint(url: str, client_id: str) -> dict:
    try:
        return await ingest_url(url=url, client_id=client_id)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("/", summary="List ingested documents for a client")
async def list_docs(
    client_id: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    return await list_documents(client_id=client_id, skip=skip, limit=limit)


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{doc_id}", summary="Delete a document and its vectors")
async def delete_doc(
    doc_id: str,
    client_id: str = Query(...),
) -> dict:
    return await delete_document(doc_id=doc_id, client_id=client_id)
