"""PDF text extraction using PyMuPDF (fitz).

Extracts text page-by-page, inserting page-number markers so that
downstream chunking can preserve page context in metadata.
"""
import io

import fitz  # PyMuPDF


def parse_pdf(file_bytes: bytes) -> str:
    """Extract plain text from a PDF file.

    Each page is prefixed with "--- Page N ---".
    Blank/image-only pages are silently skipped.
    Returns all pages joined with double newlines.
    """
    doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
    pages: list[str] = []
    try:
        for page_num, page in enumerate(doc, start=1):
            # "text" layout mode preserves reading order across columns
            text = page.get_text("text").strip()
            if text:
                pages.append(f"--- Page {page_num} ---\n{text}")
    finally:
        doc.close()
    return "\n\n".join(pages)
