"""Ingest documents into the RAG pipeline from the command line.

Usage:
  # Ingest a local file (PDF, DOCX, TXT, or Markdown)
  python scripts/ingest_documents.py --path ./docs/sample.pdf --client-id demo

  # Ingest a web URL
  python scripts/ingest_documents.py --url https://example.com/faq --client-id demo

Run from the project root. The backend/ directory must be on the Python path,
which this script handles automatically via sys.path.insert.
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Make sure `backend/` is importable regardless of CWD
_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT / "backend"))

import os  # noqa: E402 — after sys.path patch

# Provide required env vars so pydantic-settings doesn't abort on import.
# Override in your shell or .env file with real values for actual ingestion.
os.environ.setdefault("SECRET_KEY", "dev-only-not-for-production")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/ragdb",
)

from app.db.postgres import connect_db, disconnect_db  # noqa: E402
from app.services.document_service import (  # noqa: E402
    ingest_document_file,
    ingest_url,
)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest a file or URL into the RAG vector store.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--path", metavar="FILE", help="Path to a local file")
    source.add_argument("--url", metavar="URL", help="Public URL to scrape")
    parser.add_argument(
        "--client-id",
        default="demo",
        help="Tenant client ID (default: demo)",
    )
    args = parser.parse_args()

    await connect_db()
    try:
        if args.path:
            file_path = Path(args.path)
            if not file_path.exists():
                print(f"Error: file not found: {file_path}", file=sys.stderr)
                sys.exit(1)
            file_bytes = file_path.read_bytes()
            result = await ingest_document_file(
                file_bytes=file_bytes,
                filename=file_path.name,
                content_type=None,   # detected from extension
                client_id=args.client_id,
            )
            print(
                f"Ingested '{file_path.name}' → "
                f"doc_id={result['doc_id']}, chunks={result['chunk_count']}"
            )
        else:
            result = await ingest_url(url=args.url, client_id=args.client_id)
            print(
                f"Ingested URL '{args.url}' → "
                f"doc_id={result['doc_id']}, chunks={result['chunk_count']}"
            )
    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(main())
