"""Unit tests for the ingestion orchestrator.

All parser calls, HTTP fetches, and pipeline calls are mocked.
"""
from unittest.mock import AsyncMock, patch

import pytest

from app.ingestion.orchestrator import ingest_file, ingest_web_url


# ── ingest_file ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ingest_file_pdf_returns_chunk_count():
    with (
        patch("app.ingestion.orchestrator.parse_file", return_value="PDF text content."),
        patch("app.ingestion.orchestrator.ingest_document", new_callable=AsyncMock, return_value=7),
    ):
        result = await ingest_file(
            file_bytes=b"%PDF fake bytes",
            doc_id="doc-001",
            client_id="tenant1",
            filename="manual.pdf",
            content_type="application/pdf",
        )

    assert result == 7


@pytest.mark.asyncio
async def test_ingest_file_docx_uses_correct_parser():
    parse_called_with = {}

    def capture_parse(file_bytes, content_type, filename):
        parse_called_with.update({"ct": content_type, "fn": filename})
        return "DOCX extracted text"

    with (
        patch("app.ingestion.orchestrator.parse_file", side_effect=capture_parse),
        patch("app.ingestion.orchestrator.ingest_document", new_callable=AsyncMock, return_value=3),
    ):
        await ingest_file(
            file_bytes=b"PK fake docx",
            doc_id="doc-002",
            client_id="tenant1",
            filename="report.docx",
            content_type=(
                "application/vnd.openxmlformats-officedocument"
                ".wordprocessingml.document"
            ),
        )

    assert parse_called_with["fn"] == "report.docx"


@pytest.mark.asyncio
async def test_ingest_file_raises_on_empty_text():
    with (
        patch("app.ingestion.orchestrator.parse_file", return_value="   "),
    ):
        with pytest.raises(ValueError, match="No text"):
            await ingest_file(
                file_bytes=b"garbage",
                doc_id="doc-003",
                client_id="tenant1",
                filename="empty.pdf",
            )


@pytest.mark.asyncio
async def test_ingest_file_passes_metadata_with_filename():
    captured_meta = {}

    async def capture_ingest(text, doc_id, client_id, metadata):
        captured_meta.update(metadata)
        return 5

    with (
        patch("app.ingestion.orchestrator.parse_file", return_value="some text content"),
        patch("app.ingestion.orchestrator.ingest_document", side_effect=capture_ingest),
    ):
        await ingest_file(
            file_bytes=b"bytes",
            doc_id="doc-004",
            client_id="tenant2",
            filename="data.txt",
        )

    assert captured_meta["filename"] == "data.txt"
    assert captured_meta["source"] == "txt"


# ── ingest_web_url ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ingest_web_url_returns_chunk_count():
    with (
        patch(
            "app.ingestion.orchestrator.parse_url",
            new_callable=AsyncMock,
            return_value="Scraped web content with plenty of words.",
        ),
        patch(
            "app.ingestion.orchestrator.ingest_document",
            new_callable=AsyncMock,
            return_value=4,
        ),
    ):
        result = await ingest_web_url(
            url="https://example.com/faq",
            doc_id="doc-005",
            client_id="tenant1",
        )

    assert result == 4


@pytest.mark.asyncio
async def test_ingest_web_url_passes_url_metadata():
    captured_meta = {}

    async def capture_ingest(text, doc_id, client_id, metadata):
        captured_meta.update(metadata)
        return 2

    with (
        patch(
            "app.ingestion.orchestrator.parse_url",
            new_callable=AsyncMock,
            return_value="Page text here.",
        ),
        patch("app.ingestion.orchestrator.ingest_document", side_effect=capture_ingest),
    ):
        await ingest_web_url(
            url="https://docs.example.com",
            doc_id="doc-006",
            client_id="tenant3",
        )

    assert captured_meta["source_url"] == "https://docs.example.com"
    assert captured_meta["source"] == "url"


@pytest.mark.asyncio
async def test_ingest_web_url_raises_on_empty_content():
    with patch(
        "app.ingestion.orchestrator.parse_url",
        new_callable=AsyncMock,
        return_value="",
    ):
        with pytest.raises(ValueError, match="No text"):
            await ingest_web_url(
                url="https://blank.example.com",
                doc_id="doc-007",
                client_id="tenant1",
            )


# ── _detect_type helper ───────────────────────────────────────────────────────

def test_detect_type_from_extension():
    from app.ingestion.orchestrator import _detect_type
    assert _detect_type(None, "doc.pdf") == "pdf"
    assert _detect_type(None, "report.docx") == "docx"
    assert _detect_type(None, "notes.txt") == "txt"
    assert _detect_type(None, "readme.md") == "markdown"


def test_detect_type_unknown_falls_back():
    from app.ingestion.orchestrator import _detect_type
    assert _detect_type(None, "archive.zip") == "file"
    assert _detect_type(None, "no_extension") == "file"
    assert _detect_type(None, None) == "file"
