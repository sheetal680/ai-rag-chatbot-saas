"""Unit tests for the streaming chat service and lead-detection helpers.

All external I/O (RAG chain, DB pool) is mocked — no API keys or DB needed.
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# ── Helpers ────────────────────────────────────────────────────────────────────

async def collect_sse(gen) -> list[dict]:
    """Drain an SSE async generator and return parsed JSON events."""
    events: list[dict] = []
    async for line in gen:
        if line.startswith("data: "):
            events.append(json.loads(line[6:]))
    return events


def make_mock_chain(*tokens: str):
    """Return a mock RAGChain whose astream() yields *tokens* in order."""
    chain = MagicMock()

    async def _astream(*args, **kwargs):
        for token in tokens:
            yield token

    chain.astream = _astream
    return chain


def make_failing_chain(exc: Exception = RuntimeError("LLM exploded")):
    """Return a mock RAGChain whose astream() raises *exc* immediately."""
    chain = MagicMock()

    async def _astream(*args, **kwargs):
        raise exc
        yield  # pragma: no cover — makes it an async generator

    chain.astream = _astream
    return chain


# ── stream_answer — token events ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_stream_yields_one_event_per_token():
    with (
        patch("app.services.chat_service.get_rag_chain", return_value=make_mock_chain("Hello", " world", "!")),
        patch("app.services.chat_service._persist_exchange", new_callable=AsyncMock),
        patch("app.services.chat_service._maybe_capture_lead", new_callable=AsyncMock, return_value=False),
    ):
        from app.services.chat_service import stream_answer
        events = await collect_sse(stream_answer("q", "c1", "s1"))

    token_events = [e for e in events if "token" in e]
    assert [e["token"] for e in token_events] == ["Hello", " world", "!"]


@pytest.mark.asyncio
async def test_stream_final_event_is_done():
    with (
        patch("app.services.chat_service.get_rag_chain", return_value=make_mock_chain("ok")),
        patch("app.services.chat_service._persist_exchange", new_callable=AsyncMock),
        patch("app.services.chat_service._maybe_capture_lead", new_callable=AsyncMock, return_value=False),
    ):
        from app.services.chat_service import stream_answer
        events = await collect_sse(stream_answer("q", "client1", "sess1"))

    done_events = [e for e in events if e.get("done")]
    assert len(done_events) == 1
    assert done_events[0]["session_id"] == "sess1"
    assert "lead_captured" not in done_events[0]


@pytest.mark.asyncio
async def test_stream_done_event_includes_lead_captured_flag():
    with (
        patch("app.services.chat_service.get_rag_chain", return_value=make_mock_chain("ok")),
        patch("app.services.chat_service._persist_exchange", new_callable=AsyncMock),
        patch("app.services.chat_service._maybe_capture_lead", new_callable=AsyncMock, return_value=True),
    ):
        from app.services.chat_service import stream_answer
        events = await collect_sse(stream_answer("John Doe john@example.com", "c1", "s1"))

    done = next(e for e in events if e.get("done"))
    assert done.get("lead_captured") is True


# ── stream_answer — persistence ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_stream_persists_concatenated_tokens():
    persist_mock = AsyncMock()
    with (
        patch("app.services.chat_service.get_rag_chain", return_value=make_mock_chain("tok1", "tok2")),
        patch("app.services.chat_service._persist_exchange", persist_mock),
        patch("app.services.chat_service._maybe_capture_lead", new_callable=AsyncMock, return_value=False),
    ):
        from app.services.chat_service import stream_answer
        await collect_sse(stream_answer("question", "client", "session"))

    persist_mock.assert_awaited_once()
    # 4th positional arg is `answer`
    assert persist_mock.call_args.args[3] == "tok1tok2"


@pytest.mark.asyncio
async def test_stream_calls_persist_with_correct_session():
    persist_mock = AsyncMock()
    with (
        patch("app.services.chat_service.get_rag_chain", return_value=make_mock_chain("x")),
        patch("app.services.chat_service._persist_exchange", persist_mock),
        patch("app.services.chat_service._maybe_capture_lead", new_callable=AsyncMock, return_value=False),
    ):
        from app.services.chat_service import stream_answer
        await collect_sse(stream_answer("hi", "my_client", "my_session"))

    args = persist_mock.call_args.args
    assert args[0] == "my_client"
    assert args[1] == "my_session"
    assert args[2] == "hi"


# ── stream_answer — error handling ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_stream_yields_error_event_on_rag_failure():
    with (
        patch("app.services.chat_service.get_rag_chain", return_value=make_failing_chain()),
        patch("app.services.chat_service._persist_exchange", new_callable=AsyncMock),
    ):
        from app.services.chat_service import stream_answer
        events = await collect_sse(stream_answer("q", "c1", "s1"))

    error_events = [e for e in events if "error" in e]
    assert len(error_events) == 1
    assert "try again" in error_events[0]["error"].lower()


@pytest.mark.asyncio
async def test_stream_no_done_event_after_error():
    with (
        patch("app.services.chat_service.get_rag_chain", return_value=make_failing_chain()),
        patch("app.services.chat_service._persist_exchange", new_callable=AsyncMock),
    ):
        from app.services.chat_service import stream_answer
        events = await collect_sse(stream_answer("q", "c1", "s1"))

    assert not any(e.get("done") for e in events)


@pytest.mark.asyncio
async def test_stream_continues_if_db_persist_fails():
    """DB failure must not surface as an error event — stream still sends done."""
    with (
        patch("app.services.chat_service.get_rag_chain", return_value=make_mock_chain("ok")),
        patch("app.services.chat_service._persist_exchange", AsyncMock(side_effect=RuntimeError("DB down"))),
        patch("app.services.chat_service._maybe_capture_lead", new_callable=AsyncMock, return_value=False),
    ):
        from app.services.chat_service import stream_answer
        events = await collect_sse(stream_answer("q", "c1", "s1"))

    assert any(e.get("done") for e in events)
    assert not any("error" in e for e in events)


# ── RAGChain.astream ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_rag_chain_astream_yields_tokens():
    from app.retrieval.semantic import RetrievedChunk

    chunks = [RetrievedChunk(text="Paris is the capital of France.", score=0.9)]

    async def _fake_astream(messages):
        for word in ["Paris", " is", " the", " capital."]:
            chunk = MagicMock()
            chunk.content = word
            yield chunk

    with (
        patch("app.chains.rag_chain._build_llms") as mock_build,
        patch("app.chains.rag_chain.retrieve", new_callable=AsyncMock, return_value=chunks),
    ):
        mock_llm = MagicMock()
        mock_llm.astream = _fake_astream
        mock_build.return_value = (mock_llm, None)

        from app.chains.rag_chain import RAGChain
        chain = RAGChain()
        tokens = []
        async for token in chain.astream("What is the capital?", "c1", "s1"):
            tokens.append(token)

    assert tokens == ["Paris", " is", " the", " capital."]


@pytest.mark.asyncio
async def test_rag_chain_astream_yields_no_context_when_empty():
    from app.prompts.templates import NO_CONTEXT_RESPONSE

    with (
        patch("app.chains.rag_chain._build_llms") as mock_build,
        patch("app.chains.rag_chain.retrieve", new_callable=AsyncMock, return_value=[]),
    ):
        mock_llm = MagicMock()
        mock_build.return_value = (mock_llm, None)

        from app.chains.rag_chain import RAGChain
        chain = RAGChain()
        tokens = []
        async for token in chain.astream("random question", "c1", "s1"):
            tokens.append(token)

    assert tokens == [NO_CONTEXT_RESPONSE]
    # LLM must not be called when there are no chunks
    mock_llm.astream.assert_not_called()


@pytest.mark.asyncio
async def test_rag_chain_astream_falls_back_to_gemini_on_groq_rate_limit():
    from app.retrieval.semantic import RetrievedChunk

    chunks = [RetrievedChunk(text="Some context.", score=0.85)]
    fallback_answer = "Answer from Gemini."

    async def _failing_astream(messages):
        raise RuntimeError("429 Rate limit")
        yield  # pragma: no cover

    with (
        patch("app.chains.rag_chain._build_llms") as mock_build,
        patch("app.chains.rag_chain.retrieve", new_callable=AsyncMock, return_value=chunks),
    ):
        mock_primary = MagicMock()
        mock_primary.astream = _failing_astream

        mock_fallback = AsyncMock()
        mock_fallback.ainvoke = AsyncMock(
            return_value=MagicMock(content=fallback_answer)
        )

        mock_build.return_value = (mock_primary, mock_fallback)

        from app.chains.rag_chain import RAGChain
        chain = RAGChain()
        tokens = []
        async for token in chain.astream("question", "c1", "s1"):
            tokens.append(token)

    assert "".join(tokens) == fallback_answer
    mock_fallback.ainvoke.assert_awaited_once()


@pytest.mark.asyncio
async def test_rag_chain_astream_raises_when_no_fallback():
    from app.retrieval.semantic import RetrievedChunk

    chunks = [RetrievedChunk(text="ctx", score=0.9)]

    async def _failing_astream(messages):
        raise RuntimeError("fatal")
        yield  # pragma: no cover

    with (
        patch("app.chains.rag_chain._build_llms") as mock_build,
        patch("app.chains.rag_chain.retrieve", new_callable=AsyncMock, return_value=chunks),
    ):
        mock_primary = MagicMock()
        mock_primary.astream = _failing_astream
        mock_build.return_value = (mock_primary, None)

        from app.chains.rag_chain import RAGChain
        chain = RAGChain()

        with pytest.raises(RuntimeError, match="fatal"):
            async for _ in chain.astream("q", "c1", "s1"):
                pass


# ── _extract_name ──────────────────────────────────────────────────────────────

def test_extract_name_from_plain_name_before_email():
    from app.services.chat_service import _extract_name
    assert _extract_name("John Smith ") == "John Smith"


def test_extract_name_strips_preamble_phrases():
    from app.services.chat_service import _extract_name
    result = _extract_name("my name is Jane Doe,")
    assert "Jane" in result
    assert "Doe" in result


def test_extract_name_single_word_name():
    from app.services.chat_service import _extract_name
    result = _extract_name("Bob,")
    assert result == "Bob"


def test_extract_name_empty_input():
    from app.services.chat_service import _extract_name
    assert _extract_name("") == ""


def test_extract_name_only_stopwords():
    from app.services.chat_service import _extract_name
    assert _extract_name("please contact me at") == ""


def test_extract_name_strips_punctuation():
    from app.services.chat_service import _extract_name
    result = _extract_name("Alice Walker,")
    assert result == "Alice Walker"


# ── _maybe_capture_lead ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_capture_lead_saves_when_name_and_email_present():
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=None)
    mock_conn.execute = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_pool = MagicMock()
    mock_pool.acquire.return_value = mock_conn

    with patch("app.services.chat_service.get_pool", return_value=mock_pool):
        from app.services.chat_service import _maybe_capture_lead
        result = await _maybe_capture_lead(
            "John Smith john@example.com", "client1", "session1"
        )

    assert result is True
    mock_conn.execute.assert_awaited_once()
    insert_sql = mock_conn.execute.call_args.args[0]
    assert "INSERT INTO leads" in insert_sql


@pytest.mark.asyncio
async def test_capture_lead_skips_when_no_email():
    with patch("app.services.chat_service.get_pool") as mock_pool:
        from app.services.chat_service import _maybe_capture_lead
        result = await _maybe_capture_lead("Just chatting", "c1", "s1")

    assert result is False
    mock_pool.assert_not_called()


@pytest.mark.asyncio
async def test_capture_lead_skips_when_no_extractable_name():
    with patch("app.services.chat_service.get_pool") as mock_pool:
        from app.services.chat_service import _maybe_capture_lead
        # "my email is" → all stopwords after preamble strip → no name
        result = await _maybe_capture_lead("my email is user@example.com", "c1", "s1")

    assert result is False
    mock_pool.assert_not_called()


@pytest.mark.asyncio
async def test_capture_lead_skips_duplicate_session():
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value="existing-lead-id")
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_pool = MagicMock()
    mock_pool.acquire.return_value = mock_conn

    with patch("app.services.chat_service.get_pool", return_value=mock_pool):
        from app.services.chat_service import _maybe_capture_lead
        result = await _maybe_capture_lead("Jane jane@example.com", "c1", "session1")

    assert result is False
    mock_conn.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_capture_lead_detects_name_after_email():
    """Name that appears after the email address should still be captured."""
    mock_conn = AsyncMock()
    mock_conn.fetchval = AsyncMock(return_value=None)
    mock_conn.execute = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_pool = MagicMock()
    mock_pool.acquire.return_value = mock_conn

    with patch("app.services.chat_service.get_pool", return_value=mock_pool):
        from app.services.chat_service import _maybe_capture_lead
        result = await _maybe_capture_lead(
            "Contact me: bob@example.com, Bob Johnson", "c1", "s2"
        )

    assert result is True
