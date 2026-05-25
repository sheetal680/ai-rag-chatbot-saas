"""Unit tests for the parser layer.

All parsers are pure functions — no mocking needed.
"""
import io
import struct

import pytest

from app.parsers.txt_parser import parse_txt
from app.parsers import get_parser, parse_file, SUPPORTED_EXTENSIONS
from app.parsers.pdf_parser import parse_pdf


# ── TXT parser ────────────────────────────────────────────────────────────────

def test_parse_txt_utf8():
    assert parse_txt("Hello, world!".encode("utf-8")) == "Hello, world!"


def test_parse_txt_strips_bom():
    bom_content = b"\xef\xbb\xbfHello BOM"
    assert parse_txt(bom_content) == "Hello BOM"


def test_parse_txt_latin1_fallback():
    latin1_bytes = "Héllo".encode("latin-1")
    result = parse_txt(latin1_bytes)
    assert "H" in result  # at minimum the ASCII part survives


def test_parse_txt_strips_whitespace():
    assert parse_txt(b"  hello  \n") == "hello"


def test_parse_txt_empty():
    assert parse_txt(b"") == ""


# ── Parser dispatcher ─────────────────────────────────────────────────────────

def test_get_parser_by_pdf_content_type():
    from app.parsers.pdf_parser import parse_pdf as _pdf
    assert get_parser("application/pdf", "doc.pdf") is _pdf


def test_get_parser_by_docx_content_type():
    from app.parsers.docx_parser import parse_docx as _docx
    ct = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert get_parser(ct, "doc.docx") is _docx


def test_get_parser_by_txt_extension():
    from app.parsers.txt_parser import parse_txt as _txt
    assert get_parser(None, "readme.txt") is _txt


def test_get_parser_by_md_extension():
    from app.parsers.txt_parser import parse_txt as _txt
    assert get_parser(None, "README.md") is _txt


def test_get_parser_unsupported_raises():
    with pytest.raises(ValueError):
        get_parser("image/png", "photo.png")


def test_parse_file_txt():
    result = parse_file(b"hello world", "text/plain", "notes.txt")
    assert result == "hello world"


def test_supported_extensions_includes_expected():
    for ext in ("pdf", "docx", "txt", "md"):
        assert ext in SUPPORTED_EXTENSIONS


# ── Chunker ───────────────────────────────────────────────────────────────────

def test_chunker_attaches_metadata():
    from app.rag.chunker import chunk_text
    chunks = chunk_text("word " * 200, metadata={"doc_id": "d1", "source": "pdf"})
    for chunk in chunks:
        assert chunk.metadata["doc_id"] == "d1"
        assert "chunk_index" in chunk.metadata
        assert "total_chunks" in chunk.metadata


def test_chunker_total_chunks_consistent():
    from app.rag.chunker import chunk_text
    chunks = chunk_text("sentence. " * 100)
    total = chunks[0].metadata["total_chunks"]
    assert all(c.metadata["total_chunks"] == total for c in chunks)
    assert total == len(chunks)
