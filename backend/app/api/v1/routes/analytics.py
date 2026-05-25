from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user
from app.services.analytics_service import (
    get_conversation,
    get_summary,
    get_top_questions,
    get_unanswered,
    get_volume,
    list_conversations,
)

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/summary", summary="Overview stats for a client")
async def summary(client_id: str = Query(...)) -> dict:
    return await get_summary(client_id)


@router.get("/conversations", summary="List chat sessions newest-first")
async def conversations(
    client_id: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
) -> list[dict]:
    return await list_conversations(client_id, skip=skip, limit=limit)


@router.get("/conversations/{session_id}", summary="All messages for one session")
async def conversation_detail(
    session_id: str,
    client_id: str = Query(...),
) -> dict:
    result = await get_conversation(client_id, session_id)
    if not result["messages"]:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.get("/volume", summary="Daily message + session counts (last N days)")
async def volume(
    client_id: str = Query(...),
    days: int = Query(30, ge=1, le=90),
) -> list[dict]:
    return await get_volume(client_id, days=days)


@router.get("/top-questions", summary="Most frequently asked user questions")
async def top_questions(
    client_id: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
) -> list[dict]:
    return await get_top_questions(client_id, limit=limit)


@router.get("/unanswered", summary="User questions that triggered the no-context fallback")
async def unanswered(
    client_id: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
) -> list[dict]:
    return await get_unanswered(client_id, limit=limit)
