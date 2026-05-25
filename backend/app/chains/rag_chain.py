"""RAG chain — the main intelligence pipeline.

Ties together:
  retrieval/ → prompts/ → LLM → answer

This is the ONLY place in the codebase that calls the LLM directly.
Everything else builds toward or consumes this module.

LLM selection (controlled by LLM_PROVIDER in settings):
  "auto"   → Groq if GROQ_API_KEY set, else Gemini if GEMINI_API_KEY set, else Ollama
  "groq"   → Groq unconditionally
  "gemini" → Gemini unconditionally
  "ollama" → Ollama unconditionally (local dev)

When the primary LLM raises an exception, the chain falls back to
_fallback_llm automatically (Gemini when primary is Groq + key present).
"""
from __future__ import annotations

import structlog
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings
from app.prompts import build_rag_messages, NO_CONTEXT_RESPONSE
from app.retrieval import retrieve
from app.retrieval.semantic import DEFAULT_SCORE_THRESHOLD, DEFAULT_TOP_K

logger = structlog.get_logger()


def _build_llms() -> tuple[BaseChatModel, BaseChatModel | None]:
    """Return (primary_llm, fallback_llm | None) based on settings."""
    provider = settings.LLM_PROVIDER.lower()

    def _groq() -> BaseChatModel:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=0.2,
            max_tokens=1024,
            api_key=settings.GROQ_API_KEY,
        )

    def _gemini() -> BaseChatModel:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            temperature=0.2,
            max_output_tokens=1024,
            google_api_key=settings.GEMINI_API_KEY,
        )

    def _ollama() -> BaseChatModel:
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.2,
            num_predict=1024,
        )

    if provider == "groq":
        return _groq(), None

    if provider == "gemini":
        return _gemini(), None

    if provider == "ollama":
        return _ollama(), None

    # "auto" — pick based on which API keys are present
    if settings.GROQ_API_KEY:
        primary = _groq()
        fallback = _gemini() if settings.GEMINI_API_KEY else None
        return primary, fallback

    if settings.GEMINI_API_KEY:
        return _gemini(), None

    # Neither cloud key — fall back to local Ollama
    logger.warning(
        "rag_chain.no_cloud_key",
        detail="GROQ_API_KEY and GEMINI_API_KEY are both unset — using Ollama",
    )
    return _ollama(), None


class RAGChain:
    """Stateless RAG chain — create once, call `.run()` many times."""

    def __init__(self) -> None:
        self._llm, self._fallback_llm = _build_llms()
        logger.info(
            "rag_chain.init",
            primary=type(self._llm).__name__,
            fallback=type(self._fallback_llm).__name__ if self._fallback_llm else None,
        )

    async def run(
        self,
        question: str,
        client_id: str,
        session_id: str,
        history: list[dict] | None = None,
        top_k: int = DEFAULT_TOP_K,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    ) -> str:
        """Full RAG pipeline: retrieve → check → prompt → generate → return."""
        log = logger.bind(client_id=client_id, session_id=session_id)

        # ── Step 1: Retrieve ─────────────────────────────────────────────────
        log.info("rag.retrieve.start", question_preview=question[:80])
        chunks = await retrieve(
            question=question,
            client_id=client_id,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        log.info("rag.retrieve.done", chunks_found=len(chunks))

        # ── Step 2: Fallback when nothing is relevant ────────────────────────
        if not chunks:
            log.warning("rag.no_context", question_preview=question[:80])
            return NO_CONTEXT_RESPONSE

        # ── Step 3: Build prompt ─────────────────────────────────────────────
        messages_dicts = build_rag_messages(question, chunks, history)

        lc_messages = []
        for m in messages_dicts:
            if m["role"] == "system":
                lc_messages.append(SystemMessage(content=m["content"]))
            elif m["role"] == "user":
                lc_messages.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                lc_messages.append(AIMessage(content=m["content"]))

        # ── Step 4: Generate (with fallback) ─────────────────────────────────
        log.info("rag.generate.start", llm=type(self._llm).__name__)
        try:
            response = await self._llm.ainvoke(lc_messages)
        except Exception as primary_exc:
            if self._fallback_llm is None:
                raise
            log.warning(
                "rag.primary_llm_failed",
                error=str(primary_exc),
                fallback=type(self._fallback_llm).__name__,
            )
            response = await self._fallback_llm.ainvoke(lc_messages)

        answer = response.content
        log.info("rag.generate.done", answer_length=len(answer))
        return answer

    async def astream(
        self,
        question: str,
        client_id: str,
        session_id: str,
        history: list[dict] | None = None,
        top_k: int = DEFAULT_TOP_K,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    ):
        """Stream the RAG answer as raw string tokens (async generator).

        Yields one string per LLM token, or the entire no-context message as
        a single yield when retrieval finds nothing relevant.

        On primary-LLM failure (e.g. Groq rate-limit) before any token is
        emitted, falls back to the secondary LLM and yields its full response
        as one token so the caller still gets a complete reply.
        """
        log = logger.bind(client_id=client_id, session_id=session_id)

        # ── 1. Retrieve ──────────────────────────────────────────────────────
        log.info("rag.stream.retrieve.start", question_preview=question[:80])
        chunks = await retrieve(
            question=question,
            client_id=client_id,
            top_k=top_k,
            score_threshold=score_threshold,
        )
        log.info("rag.stream.retrieve.done", chunks_found=len(chunks))

        # ── 2. No-context fast path ──────────────────────────────────────────
        if not chunks:
            log.warning("rag.stream.no_context", question_preview=question[:80])
            yield NO_CONTEXT_RESPONSE
            return

        # ── 3. Build prompt ──────────────────────────────────────────────────
        messages_dicts = build_rag_messages(question, chunks, history)
        lc_messages = []
        for m in messages_dicts:
            role, content = m["role"], m["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))

        # ── 4. Stream tokens (primary → fallback on error) ───────────────────
        log.info("rag.stream.generate.start", llm=type(self._llm).__name__)
        try:
            async for chunk in self._llm.astream(lc_messages):
                if chunk.content:
                    yield chunk.content
        except Exception as primary_exc:
            if self._fallback_llm is None:
                log.error("rag.stream.no_fallback", error=str(primary_exc))
                raise
            log.warning(
                "rag.stream.primary_failed",
                error=str(primary_exc),
                fallback=type(self._fallback_llm).__name__,
            )
            # Primary failed before emitting — fall back via full ainvoke so
            # the caller receives a complete (non-streaming) reply.
            response = await self._fallback_llm.ainvoke(lc_messages)
            yield response.content

        log.info("rag.stream.generate.done")


# ── Process-level singleton ───────────────────────────────────────────────────

_chain: RAGChain | None = None


def get_rag_chain() -> RAGChain:
    global _chain
    if _chain is None:
        _chain = RAGChain()
    return _chain
