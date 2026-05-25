import re
from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    """Returns True if url has a valid http/https scheme and a non-empty netloc."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


def sanitize_client_id(client_id: str) -> str:
    """Strip anything that isn't alphanumeric, dash, or underscore.
    Prevents collection name injection into ChromaDB."""
    return re.sub(r"[^a-zA-Z0-9_-]", "", client_id)[:64]
