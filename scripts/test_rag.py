"""Smoke-test the RAG pipeline end-to-end without starting the API server.

Tests two things independently:
  1. Retrieval — embed the question, query ChromaDB, print top chunks
  2. Generation — run the full RAGChain (Groq/Gemini) and print the answer
     (requires GROQ_API_KEY or GEMINI_API_KEY)

Usage:
  python scripts/test_rag.py --client-id demo --question "What is your refund policy?"
  python scripts/test_rag.py --client-id demo --question "..." --retrieval-only
"""

import argparse
import asyncio
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(_ROOT / "backend"))

import os  # noqa: E402

os.environ.setdefault("SECRET_KEY", "dev-only-not-for-production")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/ragdb",
)

from app.rag.pipeline import query_rag  # noqa: E402


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Smoke-test RAG retrieval and/or generation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--client-id", default="demo", help="Tenant client ID")
    parser.add_argument("--question", required=True, help="Question to ask")
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Only retrieve chunks; skip LLM generation step",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of chunks to retrieve (default: 5)",
    )
    args = parser.parse_args()

    # ── Step 1: Retrieve ──────────────────────────────────────────────────────
    print(f"\nQuestion : {args.question!r}")
    print(f"Client ID: {args.client_id}")
    print(f"Top-K    : {args.top_k}\n")
    print("─" * 60)
    print("Retrieving chunks…")

    chunks = await query_rag(
        question=args.question,
        client_id=args.client_id,
        top_k=args.top_k,
    )

    if not chunks:
        print("No chunks found above the similarity threshold.")
        print("Make sure you have ingested documents for this client_id first.")
        print("  python scripts/ingest_documents.py --path <file> --client-id <id>")
        return

    print(f"Retrieved {len(chunks)} chunk(s):\n")
    for i, chunk in enumerate(chunks, start=1):
        source = (
            chunk["metadata"].get("filename")
            or chunk["metadata"].get("source_url")
            or "unknown"
        )
        print(f"  [{i}] score={chunk['score']:.3f} | source={source}")
        print(f"      {chunk['text'][:120].strip()}…")
        print()

    if args.retrieval_only:
        return

    # ── Step 2: Generate ──────────────────────────────────────────────────────
    print("─" * 60)
    print("Generating answer (requires GROQ_API_KEY or GEMINI_API_KEY)…\n")

    from app.chains.rag_chain import get_rag_chain  # noqa: E402 — lazy import

    chain = get_rag_chain()
    answer = await chain.run(
        question=args.question,
        client_id=args.client_id,
        session_id="smoke-test",
    )

    print("Answer:\n")
    print(answer)
    print()


if __name__ == "__main__":
    asyncio.run(main())
