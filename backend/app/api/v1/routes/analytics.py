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

router = APIRouter()


@router.get("/summary", summary="Overview stats for the current user")
async def summary(current_user: dict = Depends(get_current_user)) -> dict:
    return await get_summary(current_user["client_id"])


@router.get("/conversations", summary="List chat sessions newest-first")
async def conversations(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
) -> list[dict]:
    return await list_conversations(current_user["client_id"], skip=skip, limit=limit)


@router.get("/conversations/{session_id}", summary="All messages for one session")
async def conversation_detail(
    session_id: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    result = await get_conversation(current_user["client_id"], session_id)
    if not result["messages"]:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.get("/volume", summary="Daily message + session counts (last N days)")
async def volume(
    current_user: dict = Depends(get_current_user),
    days: int = Query(30, ge=1, le=90),
) -> list[dict]:
    return await get_volume(current_user["client_id"], days=days)


@router.get("/top-questions", summary="Most frequently asked user questions")
async def top_questions(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50),
) -> list[dict]:
    return await get_top_questions(current_user["client_id"], limit=limit)


@router.get("/unanswered", summary="User questions that triggered the no-context fallback")
async def unanswered(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50),
) -> list[dict]:
    return await get_unanswered(current_user["client_id"], limit=limit)
