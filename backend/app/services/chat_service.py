"""Chat service — RAG pipeline orchestration for web and WhatsApp channels.

Public surface:
  stream_answer()   — async generator, yields SSE strings (web chat endpoint)
  answer_question() — awaitable, returns full string (WhatsApp + internal use)
"""
from __future__ import annotations

import json
import re
from datetime import UTC, datetime

import structlog

from app.chains.rag_chain import get_rag_chain
from app.db.postgres import get_pool
from app.utils.id_generator import new_id

logger = structlog.get_logger()

# ── Lead-detection patterns ────────────────────────────────────────────────────

_EMAIL_RE = re.compile(r"[\w.+\-]+@[\w\-]+\.[a-zA-Z]{2,}")

# Phrases that precede a name (stripped before extracting the name token)
_PREAMBLE_RE = re.compile(
    r"\b(my name is|i am|i'm|i'm|hello|hi|hey|please|email|contact|"
    r"reach me at|you can|name is|call me|this is)\b",
    re.IGNORECASE,
)

_NAME_STOP = frozenset(
    {
        "hi", "hello", "hey", "my", "name", "is", "i", "am", "email",
        "contact", "please", "me", "at", "the", "a", "an", "and", "or",
        "to", "for", "with", "in", "on", "it", "be", "can", "you",
    }
)


# ── Streaming entry point (web chat) ──────────────────────────────────────────

async def stream_answer(
    question: str,
    client_id: str,
    session_id: str,
    history: list[dict] | None = None,
):
    """Async generator — yields SSE ``data:`` strings for the chat endpoint.

    Event shapes:
    - ``{"token": "…"}``                             one LLM token
    - ``{"done": true, "session_id": "…"}``          stream done, exchange saved
    - ``{"done": true, …, "lead_captured": true}``   done + lead saved
    - ``{"error": "…"}``                             terminal error (stream stops)
    """
    log = logger.bind(client_id=client_id, session_id=session_id)
    log.info("chat.stream.start")
    tokens: list[str] = []

    # ── Stream tokens from the RAG chain ────────────────────────────────────
    try:
        async for token in get_rag_chain().astream(
            question, client_id, session_id, history
        ):
            tokens.append(token)
            yield f"data: {json.dumps({'token': token})}\n\n"
    except Exception as exc:
        log.error("chat.stream.failed", error=str(exc))
        yield f"data: {json.dumps({'error': 'Something went wrong. Please try again.'})}\n\n"
        return

    answer = "".join(tokens)

    # ── Persist exchange to Supabase ─────────────────────────────────────────
    try:
        await _persist_exchange(client_id, session_id, question, answer)
    except Exception as exc:
        log.error("chat.stream.persist_failed", error=str(exc))

    # ── Passive lead capture ─────────────────────────────────────────────────
    lead_captured = False
    try:
        lead_captured = await _maybe_capture_lead(question, client_id, session_id)
    except Exception as exc:
        log.error("chat.stream.lead_failed", error=str(exc))

    # ── Done event ───────────────────────────────────────────────────────────
    done: dict = {"done": True, "session_id": session_id}
    if lead_captured:
        done["lead_captured"] = True
    log.info("chat.stream.done", lead_captured=lead_captured)
    yield f"data: {json.dumps(done)}\n\n"


# ── Non-streaming entry point (WhatsApp / internal) ───────────────────────────

async def answer_question(
    question: str,
    client_id: str,
    session_id: str,
    history: list[dict] | None = None,
) -> str:
    """Run the RAG pipeline, persist the exchange, and return the full answer.

    Used by the WhatsApp webhook handler and scripts.
    """
    log = logger.bind(client_id=client_id, session_id=session_id)
    log.info("chat.answer.start")

    answer = await get_rag_chain().run(
        question=question,
        client_id=client_id,
        session_id=session_id,
        history=history,
    )

    await _persist_exchange(client_id, session_id, question, answer)
    log.info("chat.answer.done")
    return answer


# ── Lead detection ─────────────────────────────────────────────────────────────

async def _maybe_capture_lead(
    question: str, client_id: str, session_id: str
) -> bool:
    """Detect a name + email in the user's message and save a lead record.

    Rules:
    - The message must contain a valid email address.
    - A plausible personal name must appear before OR after the email.
    - Only one lead is captured per chat session (deduplication by session_id).

    Returns True when a new lead row was inserted.
    """
    email_match = _EMAIL_RE.search(question)
    if not email_match:
        return False

    email = email_match.group()
    before = question[: email_match.start()]
    after = question[email_match.end() :]

    name = _extract_name(before) or _extract_name(after)
    if not name:
        return False

    pool = get_pool()
    async with pool.acquire() as conn:
        # One lead per session — skip if already captured
        existing = await conn.fetchval(
            "SELECT id FROM leads WHERE session_id = $1 AND source = 'chat_widget' LIMIT 1",
            session_id,
        )
        if existing:
            return False

        await conn.execute(
            """
            INSERT INTO leads
                (id, client_id, name, email, session_id, status, source, message, created_at)
            VALUES ($1, $2, $3, $4, $5, 'new', 'chat_widget', $6, $7)
            """,
            new_id(),
            client_id,
            name,
            email,
            session_id,
            question[:500],
            datetime.now(UTC),
        )

    logger.info("chat.lead_captured", session_id=session_id, email=email, name=name)
    return True


def _extract_name(fragment: str) -> str:
    """Extract a plausible personal name from a text fragment near an email.

    Strips common preamble phrases ("my name is", "hi", etc.) then returns
    up to three consecutive non-stopword words.  Returns "" when nothing
    name-like is found.
    """
    if not fragment:
        return ""
    cleaned = _PREAMBLE_RE.sub(" ", fragment).strip().rstrip(",:;")
    words = [w.strip(".,;:!?\"'()-@") for w in cleaned.split()]
    meaningful = [
        w
        for w in words
        if len(w) >= 2
        and w.lower() not in _NAME_STOP
        and not w.isdigit()
        and "@" not in w
    ]
    return " ".join(meaningful[:3]).strip()


# ── Shared persistence helper ──────────────────────────────────────────────────

async def _persist_exchange(
    client_id: str, session_id: str, question: str, answer: str
) -> None:
    """Upsert the session row and append both messages atomically."""
    pool = get_pool()
    now = datetime.now(UTC)

    async with pool.acquire() as conn:
        # First message creates the session; subsequent messages increment count.
        await conn.execute(
            """
            INSERT INTO sessions
                (id, client_id, preview, message_count, created_at, last_message_at)
            VALUES ($1, $2, $3, 2, $4, $4)
            ON CONFLICT (id) DO UPDATE SET
                last_message_at = EXCLUDED.last_message_at,
                message_count   = sessions.message_count + 2
            """,
            session_id,
            client_id,
            question[:80],
            now,
        )

        await conn.executemany(
            """
            INSERT INTO messages (id, session_id, client_id, role, content, created_at)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            [
                (new_id(), session_id, client_id, "user", question, now),
                (new_id(), session_id, client_id, "assistant", answer, now),
            ],
        )
