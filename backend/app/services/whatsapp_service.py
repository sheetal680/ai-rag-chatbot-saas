"""WhatsApp service — routes inbound Meta Cloud API messages through the RAG pipeline."""
from __future__ import annotations

import re
from datetime import UTC, datetime

import httpx
import structlog

from app.core.config import settings
from app.db.postgres import get_pool
from app.services.chat_service import answer_question
from app.utils.id_generator import new_id

logger = structlog.get_logger()

# Appended to the RAG answer after the 3rd user exchange to trigger lead capture
_LEAD_PROMPT = (
    "\n\n📧 Want us to follow up with you? Reply with your "
    "name and email (e.g. Jane Smith, jane@example.com) "
    "and we'll be in touch!"
)

_EMAIL_RE = re.compile(r"[\w.+\-]+@[\w\-]+\.[a-zA-Z]{2,}")


# ─── Public entry point ───────────────────────────────────────────────────────

async def process_inbound(
    from_number: str,
    body: str,
    profile_name: str = "",
    phone_number_id: str = "",
) -> str:
    """Full inbound-message pipeline.

    Args:
        from_number:     Sender's phone number (digits only, e.g. "15551234567").
        body:            Message text.
        profile_name:    Display name from the contact profile.
        phone_number_id: Meta phone number ID — used to derive the tenant client_id.

    Returns:
        The answer string to send back to the user.
    """
    # Meta provides digits-only numbers; strip any stray "+" to normalise
    session_id = "wa_" + re.sub(r"\D", "", from_number)
    client_id = _derive_client_id(phone_number_id)

    log = logger.bind(session_id=session_id, client_id=client_id)
    log.info("whatsapp.inbound", body_len=len(body))

    pool = get_pool()

    # 1. Read current session state
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT user_message_count, awaiting_lead, lead_captured FROM wa_sessions WHERE id = $1",
            session_id,
        )
    user_count: int = row["user_message_count"] if row else 0
    awaiting_lead: bool = row["awaiting_lead"] if row else False
    lead_captured: bool = row["lead_captured"] if row else False

    # 2. Try to capture lead if we're expecting name + email
    if awaiting_lead and not lead_captured:
        captured = await _try_capture_lead(session_id, client_id, from_number, body, profile_name)
        if captured:
            return captured

    # 3. Fetch recent history and run RAG
    history_rows = await _get_history(session_id)
    history = [{"role": r["role"], "content": r["content"]} for r in history_rows[-10:]]

    answer = await answer_question(
        question=body,
        client_id=client_id,
        session_id=session_id,
        history=history,
    )

    # 4. Upsert session and get the new message count atomically
    now = datetime.now(UTC)
    async with pool.acquire() as conn:
        result = await conn.fetchrow(
            """
            INSERT INTO wa_sessions
                (id, from_number, profile_name, client_id, user_message_count, last_message_at, created_at)
            VALUES ($1, $2, $3, $4, 1, $5, $5)
            ON CONFLICT (id) DO UPDATE SET
                user_message_count = wa_sessions.user_message_count + 1,
                last_message_at    = EXCLUDED.last_message_at
            RETURNING user_message_count
            """,
            session_id, from_number, profile_name, client_id, now,
        )
        new_count = result["user_message_count"]

    # 5. Trigger lead-capture prompt after the 3rd message
    if new_count == 3 and not lead_captured:
        async with pool.acquire() as conn:
            await conn.execute(
                "UPDATE wa_sessions SET awaiting_lead = TRUE WHERE id = $1",
                session_id,
            )
        answer += _LEAD_PROMPT

    return answer


async def send_whatsapp_message(to: str, text: str) -> None:
    """Send a text message via the Meta Cloud API.

    Does nothing (logs a warning) if Meta credentials are not configured.
    """
    if not settings.META_WHATSAPP_TOKEN or not settings.META_PHONE_NUMBER_ID:
        logger.warning(
            "whatsapp.send_skipped",
            reason="META_WHATSAPP_TOKEN or META_PHONE_NUMBER_ID not configured",
        )
        return

    url = (
        f"https://graph.facebook.com/{settings.META_API_VERSION}"
        f"/{settings.META_PHONE_NUMBER_ID}/messages"
    )
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {settings.META_WHATSAPP_TOKEN}"},
        )

    if resp.status_code != 200:
        logger.error("whatsapp.send_failed", status=resp.status_code, response=resp.text[:200])
    else:
        logger.info("whatsapp.sent", to=to, chars=len(text))


# ─── Private helpers ──────────────────────────────────────────────────────────

def _derive_client_id(phone_number_id: str) -> str:
    """Map a Meta phone_number_id to a tenant client_id.

    MVP: all numbers map to "default".
    Future: look up the phone_number_id in a client-config table.
    """
    _ = phone_number_id
    return "default"


async def _get_history(session_id: str) -> list[dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT role, content, created_at
            FROM messages
            WHERE session_id = $1
            ORDER BY created_at ASC
            LIMIT 20
            """,
            session_id,
        )
    return [dict(row) for row in rows]


async def _try_capture_lead(
    session_id: str,
    client_id: str,
    from_number: str,
    body: str,
    profile_name: str,
) -> str | None:
    """Parse name + email from the user's message and save a lead record.

    Returns a confirmation string on success, None to fall through to RAG.
    """
    match = _EMAIL_RE.search(body)
    if not match:
        return None

    email = match.group()
    before = body[: match.start()].strip().rstrip(",").strip()
    name = before if before else (profile_name or "WhatsApp User")

    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO leads (id, client_id, name, email, phone, session_id, status, source, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, 'new', 'whatsapp', $7)
            """,
            new_id(), client_id, name, email, from_number, session_id, datetime.now(UTC),
        )
        await conn.execute(
            "UPDATE wa_sessions SET awaiting_lead = FALSE, lead_captured = TRUE WHERE id = $1",
            session_id,
        )

    logger.info("whatsapp.lead_captured", session_id=session_id, email=email)
    return (
        f"✅ Thanks, {name}! We've saved your details and will follow up at {email}. "
        "Is there anything else I can help you with?"
    )
