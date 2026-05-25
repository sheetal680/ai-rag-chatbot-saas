"""Unit tests for RAGChain.

LLM calls (Groq, Gemini) and the retrieval layer are fully mocked.
No API keys or network access required.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.retrieval.semantic import RetrievedChunk


def _fake_chunks(n: int = 3) -> list[RetrievedChunk]:
    return [
        RetrievedChunk(
            text=f"Context chunk {i}.",
            score=0.9 - i * 0.1,
            metadata={"doc_id": f"doc{i}", "filename": "test.pdf"},
        )
        for i in range(n)
    ]


def _mock_llm_response(text: str) -> MagicMock:
    msg = MagicMock()
    msg.content = text
    return msg


# ── RAGChain.run ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rag_chain_returns_answer_when_chunks_found():
    chunks = _fake_chunks(2)
    fake_answer = "The refund window is 30 days."

    with (
        patch("app.chains.rag_chain._build_llms") as mock_build,
        patch("app.chains.rag_chain.retrieve", new_callable=AsyncMock) as mock_retrieve,
    ):
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(return_value=_mock_llm_response(fake_answer))
        mock_build.return_value = (mock_llm, None)
        mock_retrieve.return_value = chunks

        from app.chains.rag_chain import RAGChain
        chain = RAGChain()
        answer = await chain.run(
            question="What is the refund policy?",
            client_id="tenant_a",
            session_id="sess1",
        )

    assert answer == fake_answer
    mock_retrieve.assert_called_once()
    mock_llm.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_rag_chain_returns_no_context_response_when_no_chunks():
    from app.prompts.templates import NO_CONTEXT_RESPONSE

    with (
        patch("app.chains.rag_chain._build_llms") as mock_build,
        patch("app.chains.rag_chain.retrieve", new_callable=AsyncMock) as mock_retrieve,
    ):
        mock_llm = AsyncMock()
        mock_build.return_value = (mock_llm, None)
        mock_retrieve.return_value = []  # nothing retrieved

        from app.chains.rag_chain import RAGChain
        chain = RAGChain()
        answer = await chain.run(
            question="What is the secret of life?",
            client_id="tenant_b",
            session_id="sess2",
        )

    assert answer == NO_CONTEXT_RESPONSE
    mock_llm.ainvoke.assert_not_called()


@pytest.mark.asyncio
async def test_rag_chain_falls_back_to_gemini_on_groq_failure():
    chunks = _fake_chunks(1)
    fallback_answer = "Answer from Gemini."

    with (
        patch("app.chains.rag_chain._build_llms") as mock_build,
        patch("app.chains.rag_chain.retrieve", new_callable=AsyncMock) as mock_retrieve,
    ):
        mock_primary = AsyncMock()
        mock_primary.ainvoke = AsyncMock(side_effect=RuntimeError("Groq timeout"))

        mock_fallback = AsyncMock()
        mock_fallback.ainvoke = AsyncMock(
            return_value=_mock_llm_response(fallback_answer)
        )

        mock_build.return_value = (mock_primary, mock_fallback)
        mock_retrieve.return_value = chunks

        from app.chains.rag_chain import RAGChain
        chain = RAGChain()
        answer = await chain.run(
            question="hello",
            client_id="tenant_c",
            session_id="sess3",
        )

    assert answer == fallback_answer
    mock_fallback.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_rag_chain_raises_when_primary_fails_and_no_fallback():
    chunks = _fake_chunks(1)

    with (
        patch("app.chains.rag_chain._build_llms") as mock_build,
        patch("app.chains.rag_chain.retrieve", new_callable=AsyncMock) as mock_retrieve,
    ):
        mock_primary = AsyncMock()
        mock_primary.ainvoke = AsyncMock(side_effect=RuntimeError("fatal error"))
        mock_build.return_value = (mock_primary, None)   # no fallback
        mock_retrieve.return_value = chunks

        from app.chains.rag_chain import RAGChain
        chain = RAGChain()

        with pytest.raises(RuntimeError, match="fatal error"):
            await chain.run(
                question="hello",
                client_id="tenant_d",
                session_id="sess4",
            )


@pytest.mark.asyncio
async def test_rag_chain_passes_history_to_prompt():
    chunks = _fake_chunks(1)
    history = [
        {"role": "user", "content": "prev question"},
        {"role": "assistant", "content": "prev answer"},
    ]
    captured_messages: list = []

    async def capture_ainvoke(messages):
        captured_messages.extend(messages)
        return _mock_llm_response("ok")

    with (
        patch("app.chains.rag_chain._build_llms") as mock_build,
        patch("app.chains.rag_chain.retrieve", new_callable=AsyncMock) as mock_retrieve,
    ):
        mock_llm = AsyncMock()
        mock_llm.ainvoke = capture_ainvoke
        mock_build.return_value = (mock_llm, None)
        mock_retrieve.return_value = chunks

        from app.chains.rag_chain import RAGChain
        chain = RAGChain()
        await chain.run(
            question="new question",
            client_id="t",
            session_id="s",
            history=history,
        )

    # system + 2 history messages + 1 current question = 4 messages
    assert len(captured_messages) == 4


# ── _build_llms provider selection ───────────────────────────────────────────

def test_build_llms_groq_provider_returns_no_fallback():
    """With LLM_PROVIDER='groq', fallback must be None."""
    import sys

    # ChatGroq is imported lazily inside _groq() — stub at sys.modules level
    mock_groq_module = MagicMock()
    mock_groq_module.ChatGroq.return_value = MagicMock()
    sys.modules["langchain_groq"] = mock_groq_module

    with patch("app.chains.rag_chain.settings") as mock_settings:
        mock_settings.LLM_PROVIDER = "groq"
        mock_settings.GROQ_API_KEY = "gsk_fake"
        mock_settings.GROQ_MODEL = "llama-3.1-70b-versatile"

        from app.chains.rag_chain import _build_llms
        primary, fallback = _build_llms()

    assert fallback is None
