from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from app.core.security import get_current_user
from app.parsers import SUPPORTED_CONTENT_TYPES, SUPPORTED_EXTENSIONS
from app.services.document_service import (
    delete_document,
    ingest_document_file,
    ingest_url,
    list_documents,
)

router = APIRouter()

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


@router.post("/upload", summary="Upload a document (PDF, DOCX, TXT, MD)")
async def upload_document(
    current_user: dict = Depends(get_current_user),
    file: UploadFile = File(...),
) -> dict:
    client_id = current_user["client_id"]

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


@router.post("/upload-pdf", summary="Upload a PDF (legacy endpoint)")
async def upload_pdf(
    current_user: dict = Depends(get_current_user),
    file: UploadFile = File(...),
) -> dict:
    client_id = current_user["client_id"]

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


@router.post("/ingest-url", summary="Ingest a public web URL")
async def ingest_url_endpoint(
    url: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    client_id = current_user["client_id"]
    try:
        return await ingest_url(url=url, client_id=client_id)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))


@router.get("/", summary="List ingested documents for the current user")
async def list_docs(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    return await list_documents(client_id=current_user["client_id"], skip=skip, limit=limit)


@router.delete("/{doc_id}", summary="Delete a document and its vectors")
async def delete_doc(
    doc_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    return await delete_document(doc_id=doc_id, client_id=current_user["client_id"])
