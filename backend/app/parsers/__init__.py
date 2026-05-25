"""Parser dispatcher — routes a file to the correct text-extraction function."""
from app.parsers.pdf_parser import parse_pdf
from app.parsers.docx_parser import parse_docx
from app.parsers.txt_parser import parse_txt

# content_type → parser callable
_CONTENT_TYPE_MAP: dict[str, callable] = {
    "application/pdf": parse_pdf,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": parse_docx,
    "text/plain": parse_txt,
    "text/markdown": parse_txt,
    "text/x-markdown": parse_txt,
}

# file extension → parser callable (fallback when content_type is ambiguous)
_EXTENSION_MAP: dict[str, callable] = {
    "pdf": parse_pdf,
    "docx": parse_docx,
    "txt": parse_txt,
    "md": parse_txt,
    "markdown": parse_txt,
}

SUPPORTED_EXTENSIONS = set(_EXTENSION_MAP.keys())
SUPPORTED_CONTENT_TYPES = set(_CONTENT_TYPE_MAP.keys())


def get_parser(content_type: str | None, filename: str | None) -> callable:
    """Return the correct parse function for a file.

    Resolution order:
    1. Exact content_type match
    2. File extension match
    3. Raise ValueError
    """
    if content_type and content_type in _CONTENT_TYPE_MAP:
        return _CONTENT_TYPE_MAP[content_type]

    if filename:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext in _EXTENSION_MAP:
            return _EXTENSION_MAP[ext]

    raise ValueError(
        f"Unsupported file type: content_type={content_type!r}, filename={filename!r}. "
        f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )


def parse_file(file_bytes: bytes, content_type: str | None, filename: str | None) -> str:
    """Convenience wrapper: dispatch → parse → return text."""
    parser = get_parser(content_type, filename)
    return parser(file_bytes)
