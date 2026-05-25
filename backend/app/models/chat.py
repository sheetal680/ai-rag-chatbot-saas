from typing import Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str
    client_id: str
    history: list[ChatMessage] = []


class ChatResponse(BaseModel):
    """Kept for backward compatibility and OpenAPI docs. Not used at runtime."""
    answer: str
    session_id: str


class ChatStreamEvent(BaseModel):
    """Describes one SSE event from POST /chat — for OpenAPI documentation only."""
    token: Optional[str] = None          # present on token events
    done: Optional[bool] = None          # present on the final event
    session_id: Optional[str] = None     # present on done event
    lead_captured: Optional[bool] = None  # present on done event if lead saved
    error: Optional[str] = None          # present on terminal error events
