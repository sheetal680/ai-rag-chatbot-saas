from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DocumentRecord(BaseModel):
    """Represents a document record as stored in PostgreSQL."""

    doc_id: str
    client_id: str
    filename: Optional[str] = None
    source_url: Optional[str] = None
    chunk_count: int
    type: str  # pdf | docx | txt | markdown | url | file
    created_at: datetime


class DocumentResponse(BaseModel):
    """API response for a single document."""

    doc_id: str
    filename: Optional[str] = None
    source_url: Optional[str] = None
    chunk_count: int
    type: str  # pdf | docx | txt | markdown | url | file
    created_at: datetime


class IngestResponse(BaseModel):
    """Returned after a successful ingestion."""

    doc_id: str
    chunk_count: int
