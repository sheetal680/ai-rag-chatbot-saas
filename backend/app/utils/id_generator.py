import uuid


def new_id() -> str:
    """Generate a new UUID4 string. Use for all document and record IDs."""
    return str(uuid.uuid4())


def short_id(length: int = 8) -> str:
    """Generate a short random hex ID for display purposes."""
    return uuid.uuid4().hex[:length]
