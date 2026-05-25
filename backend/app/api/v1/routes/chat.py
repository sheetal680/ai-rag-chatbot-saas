"""Chat route — streams the RAG answer as Server-Sent Events (SSE).

SSE event shapes
----------------
Token event (one per LLM token):
    data: {"token": "Hello"}

Done event (stream complete, exchange persisted):
    data: {"done": true, "session_id": "abc123"}

Done + lead captured:
    data: {"done": true, "session_id": "abc123", "lead_captured": true}

Error event (terminal — stream stops after this):
    data: {"error": "Something went wrong. Please try again."}

Frontend consumption example
----------------------------
    const res = await fetch("/api/v1/chat/", { method: "POST", body: JSON.stringify(req) });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    for await (const chunk of reader) {
        for (const line of decoder.decode(chunk).split("\\n")) {
            if (!line.startsWith("data: ")) continue;
            const ev = JSON.parse(line.slice(6));
            if (ev.token)  appendToken(ev.token);
            if (ev.done)   handleDone(ev);
            if (ev.error)  handleError(ev.error);
        }
    }
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.models.chat import ChatRequest
from app.services.chat_service import stream_answer

router = APIRouter()


@router.post(
    "/",
    summary="Chat — stream the AI response via SSE",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "text/event-stream.  Each line: `data: <json>\\n\\n`.",
            "content": {
                "text/event-stream": {
                    "example": (
                        'data: {"token":"Hello"}\n\n'
                        'data: {"token":" world"}\n\n'
                        'data: {"done":true,"session_id":"abc123"}\n\n'
                    )
                }
            },
        }
    },
)
async def chat(request: ChatRequest) -> StreamingResponse:
    """RAG chat with streaming.

    Accepts a `ChatRequest` body and returns a `text/event-stream` response.
    Each SSE event is a JSON object — see module docstring for shapes.

    Lead capture: if the user's message contains a recognisable *Name + email*
    pattern the lead is saved automatically and `"lead_captured": true` is
    included in the final done event.
    """
    history = [m.model_dump() for m in request.history]
    return StreamingResponse(
        stream_answer(
            question=request.question,
            client_id=request.client_id,
            session_id=request.session_id,
            history=history,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # disable Nginx/Railway proxy buffering
            "Connection": "keep-alive",
        },
    )
