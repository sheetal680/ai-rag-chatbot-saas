"""WhatsApp webhook — Meta Cloud API (WhatsApp Business API).

Flow:
  GET  /webhook  → Meta calls this to verify ownership during setup.
                   Respond with hub.challenge to confirm.

  POST /webhook  → Meta sends inbound messages as JSON.
                   Respond 200 immediately, process in background, reply via Graph API.

Why background task: Meta expects a <5s response. The LLM call can take 2-8 seconds,
so we ack the webhook, then do the RAG + reply in a background task.
"""
from __future__ import annotations

import hashlib
import hmac

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from app.core.config import settings
from app.services.whatsapp_service import process_inbound, send_whatsapp_message

router = APIRouter()
logger = structlog.get_logger()


# ─── Webhook verification (GET) ───────────────────────────────────────────────

@router.get("/webhook", summary="Meta webhook verification challenge")
async def verify_webhook(
    hub_mode: str = Query(default="", alias="hub.mode"),
    hub_challenge: str = Query(default="", alias="hub.challenge"),
    hub_verify_token: str = Query(default="", alias="hub.verify_token"),
) -> PlainTextResponse:
    """
    Meta calls this endpoint once when you register the webhook URL in the
    Meta App dashboard. Confirm by echoing the challenge string.
    """
    if (
        hub_mode == "subscribe"
        and settings.META_WEBHOOK_VERIFY_TOKEN
        and hub_verify_token == settings.META_WEBHOOK_VERIFY_TOKEN
    ):
        logger.info("whatsapp.webhook_verified")
        return PlainTextResponse(content=hub_challenge, status_code=200)

    logger.warning("whatsapp.verify_failed", mode=hub_mode)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


# ─── Inbound messages (POST) ──────────────────────────────────────────────────

@router.post("/webhook", summary="Meta inbound message webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks) -> dict:
    """
    Meta POSTs inbound messages as a JSON payload. We validate the HMAC-SHA256
    signature, ack with 200 immediately, then process and reply in the background.
    """
    raw_body = await request.body()

    # ── Signature validation ──────────────────────────────────────────────────
    if settings.META_APP_SECRET:
        signature = request.headers.get("x-hub-signature-256", "")
        if not _verify_signature(raw_body, signature):
            logger.warning("whatsapp.invalid_signature")
            raise HTTPException(status_code=403, detail="Invalid signature")

    # ── Parse JSON ────────────────────────────────────────────────────────────
    try:
        payload = await request.json()
    except Exception:
        return {"status": "ok"}

    if payload.get("object") != "whatsapp_business_account":
        return {"status": "ok"}

    # ── Extract messages from the nested Meta payload ─────────────────────────
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "messages":
                continue

            value = change.get("value", {})
            messages = value.get("messages", [])
            contacts = value.get("contacts", [])
            phone_number_id = value.get("metadata", {}).get("phone_number_id", "")

            for msg in messages:
                # Only handle plain text messages; skip reactions, images, etc.
                if msg.get("type") != "text":
                    continue

                from_number = msg.get("from", "").strip()
                body = msg.get("text", {}).get("body", "").strip()
                if not from_number or not body:
                    continue

                profile_name = contacts[0].get("profile", {}).get("name", "") if contacts else ""

                logger.info("whatsapp.received", from_number=from_number, body_len=len(body))

                # Offload LLM + reply so Meta gets its 200 before the LLM finishes
                background_tasks.add_task(
                    _handle_message,
                    from_number=from_number,
                    body=body,
                    profile_name=profile_name,
                    phone_number_id=phone_number_id,
                )

    return {"status": "ok"}


# ─── Background task ──────────────────────────────────────────────────────────

async def _handle_message(
    from_number: str,
    body: str,
    profile_name: str,
    phone_number_id: str,
) -> None:
    """Run the RAG pipeline and send the reply via the Meta Graph API."""
    try:
        answer = await process_inbound(
            from_number=from_number,
            body=body,
            profile_name=profile_name,
            phone_number_id=phone_number_id,
        )
        await send_whatsapp_message(to=from_number, text=answer)
    except Exception as exc:
        logger.error("whatsapp.handler_error", error=str(exc))
        try:
            await send_whatsapp_message(
                to=from_number,
                text="Sorry, something went wrong on our end. Please try again in a moment. 🙏",
            )
        except Exception:
            pass


# ─── Signature validation helper ──────────────────────────────────────────────

def _verify_signature(body: bytes, header: str) -> bool:
    """Return True if X-Hub-Signature-256 matches HMAC-SHA256(body, app_secret)."""
    if not header.startswith("sha256="):
        return False
    received = header[len("sha256="):]
    expected = hmac.new(
        settings.META_APP_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(received, expected)
