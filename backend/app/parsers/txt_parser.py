def parse_txt(file_bytes: bytes) -> str:
    """Decode a plain-text or Markdown file to a Python string.

    Tries UTF-8 (with or without BOM) first, then falls back to latin-1.
    Strips leading/trailing whitespace.
    """
    try:
        text = file_bytes.decode("utf-8-sig")  # utf-8-sig strips UTF-8 BOM automatically
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1")
    return text.strip()
