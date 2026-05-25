"""Analytics service — all dashboard query logic lives here."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.db.postgres import get_pool


async def get_summary(client_id: str) -> dict:
    """Return total counts for sessions, messages, leads, and documents."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                (SELECT COUNT(*)::INT FROM sessions  WHERE client_id = $1) AS total_sessions,
                (SELECT COUNT(*)::INT FROM messages  WHERE client_id = $1) AS total_messages,
                (SELECT COUNT(*)::INT FROM leads     WHERE client_id = $1) AS total_leads,
                (SELECT COUNT(*)::INT FROM documents WHERE client_id = $1) AS total_documents
            """,
            client_id,
        )
    return dict(row)


async def list_conversations(client_id: str, skip: int = 0, limit: int = 30) -> list[dict]:
    """Return sessions newest-first with preview and message count."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id AS session_id, preview, message_count, created_at, last_message_at
            FROM sessions
            WHERE client_id = $1
            ORDER BY last_message_at DESC
            LIMIT $2 OFFSET $3
            """,
            client_id, limit, skip,
        )
    result = []
    for row in rows:
        d = dict(row)
        d["created_at"] = d["created_at"].isoformat() if d.get("created_at") else ""
        d["last_message_at"] = d["last_message_at"].isoformat() if d.get("last_message_at") else ""
        result.append(d)
    return result


async def get_conversation(client_id: str, session_id: str) -> dict:
    """Return all messages for a single session."""
    pool = get_pool()
    async with pool.acquire() as conn:
        session = await conn.fetchrow(
            "SELECT id FROM sessions WHERE id = $1 AND client_id = $2",
            session_id, client_id,
        )
        if session is None:
            return {"session_id": session_id, "messages": []}

        rows = await conn.fetch(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE session_id = $1 AND client_id = $2
            ORDER BY created_at ASC
            """,
            session_id, client_id,
        )

    messages = [
        {
            "role": row["role"],
            "content": row["content"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else "",
        }
        for row in rows
    ]
    return {"session_id": session_id, "messages": messages}


async def get_top_questions(client_id: str, limit: int = 10) -> list[dict]:
    """Return the most frequently asked user questions (exact match, newest wins ties)."""
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT content, COUNT(*)::INT AS frequency
            FROM messages
            WHERE client_id = $1 AND role = 'user'
            GROUP BY content
            ORDER BY frequency DESC, MAX(created_at) DESC
            LIMIT $2
            """,
            client_id, limit,
        )
    return [{"content": row["content"], "frequency": row["frequency"]} for row in rows]


async def get_unanswered(client_id: str, limit: int = 10) -> list[dict]:
    """Return user questions that triggered the no-context fallback response.

    Detected by joining user messages with the subsequent assistant message
    when that assistant message begins with the no-context prefix.
    """
    pool = get_pool()
    no_ctx_prefix = "I don't currently have specific information%"
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT m.content, COUNT(*)::INT AS occurrences
            FROM messages m
            JOIN messages bot ON (
                bot.session_id = m.session_id
                AND bot.role    = 'assistant'
                AND bot.created_at > m.created_at
                AND bot.content LIKE $2
            )
            WHERE m.client_id = $1 AND m.role = 'user'
            GROUP BY m.content
            ORDER BY occurrences DESC, MAX(m.created_at) DESC
            LIMIT $3
            """,
            client_id, no_ctx_prefix, limit,
        )
    return [{"content": row["content"], "occurrences": row["occurrences"]} for row in rows]


async def get_volume(client_id: str, days: int = 30) -> list[dict]:
    """Return daily message + session counts for the last *days* days."""
    pool = get_pool()
    since = datetime.now(UTC) - timedelta(days=days)

    async with pool.acquire() as conn:
        msg_rows = await conn.fetch(
            """
            SELECT
                TO_CHAR(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD') AS day,
                COUNT(*)::INT AS cnt
            FROM messages
            WHERE client_id = $1 AND created_at >= $2
            GROUP BY day
            ORDER BY day ASC
            """,
            client_id, since,
        )
        ses_rows = await conn.fetch(
            """
            SELECT
                TO_CHAR(created_at AT TIME ZONE 'UTC', 'YYYY-MM-DD') AS day,
                COUNT(*)::INT AS cnt
            FROM sessions
            WHERE client_id = $1 AND created_at >= $2
            GROUP BY day
            ORDER BY day ASC
            """,
            client_id, since,
        )

    msg_by_day = {row["day"]: row["cnt"] for row in msg_rows}
    ses_by_day = {row["day"]: row["cnt"] for row in ses_rows}

    all_dates = sorted(set(msg_by_day) | set(ses_by_day))
    return [
        {
            "date": d,
            "messages": msg_by_day.get(d, 0),
            "sessions": ses_by_day.get(d, 0),
        }
        for d in all_dates
    ]
