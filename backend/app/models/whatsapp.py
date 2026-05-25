from __future__ import annotations
from dataclasses import dataclass


@dataclass
class WhatsAppInbound:
    """Fields extracted from a Meta Cloud API webhook message entry."""

    from_number: str       # sender's phone (digits only, e.g. "15551234567")
    body: str              # message text
    profile_name: str = ""
    phone_number_id: str = ""  # Meta phone number ID — maps to tenant client_id
    message_id: str = ""   # wamid — can be used for deduplication
