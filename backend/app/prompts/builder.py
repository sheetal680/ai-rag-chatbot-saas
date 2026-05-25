"""Prompt assembly — combines templates with runtime data."""
from app.prompts.templates import (
    RAG_SYSTEM,
    NO_CONTEXT_RESPONSE,
    CHUNK_SEPARATOR,
    CHUNK_WITH_SOURCE,
)
from app.retrieval.semantic import RetrievedChunk

__all__ = ["build_rag_messages", "NO_CONTEXT_RESPONSE"]

# Maximum number of past conversation turns included for context continuity.
_MAX_HISTORY_TURNS = 6  # = 3 user + 3 assistant messages


def _format_chunks(chunks: list[RetrievedChunk]) -> str:
    """Render retrieved chunks into a single context block."""
    parts: list[str] = []
    for chunk in chunks:
        source = (
            chunk.metadata.get("filename")
            or chunk.metadata.get("source_url")
            or chunk.metadata.get("source", "document")
        )
        parts.append(CHUNK_WITH_SOURCE.format(source=source, text=chunk.text))
    return CHUNK_SEPARATOR.join(parts)


def build_rag_messages(
    question: str,
    chunks: list[RetrievedChunk],
    history: list[dict] | None = None,
) -> list[dict]:
    """Assemble the full message list for the LLM.

    Returns:
        [
            {"role": "system", "content": "<rag system prompt with context>"},
            {"role": "user",   "content": "..."},     # history (trimmed)
            {"role": "assistant", "content": "..."},  # history
            ...
            {"role": "user",   "content": question},  # current turn
        ]
    """
    context_block = _format_chunks(chunks)
    system_content = RAG_SYSTEM.format(context=context_block)

    messages: list[dict] = [{"role": "system", "content": system_content}]

    if history:
        messages.extend(history[-_MAX_HISTORY_TURNS:])

    messages.append({"role": "user", "content": question})
    return messages
