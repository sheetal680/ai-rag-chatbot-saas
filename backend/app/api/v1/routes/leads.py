from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.security import get_current_user
from app.db.postgres import get_pool
from app.models.lead import LeadCreate, LeadResponse
from app.utils.id_generator import new_id

router = APIRouter()


@router.post("/", response_model=LeadResponse, status_code=201, summary="Capture a lead")
async def capture_lead(lead: LeadCreate) -> LeadResponse:
    """Public endpoint — used by the embedded chat widget. client_id comes from the widget config."""
    lead_id = new_id()
    now = datetime.now(UTC)
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO leads
                (id, client_id, name, email, phone, session_id, message, status, source, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, 'new', 'web_widget', $8)
            """,
            lead_id, lead.client_id, lead.name, lead.email,
            lead.phone, lead.session_id, lead.message, now,
        )
    return LeadResponse(id=lead_id, name=lead.name, email=lead.email, created_at=now)


@router.get("/", summary="List leads for the current user")
async def list_leads(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT id, name, email, phone, status, session_id, created_at
            FROM leads
            WHERE client_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """,
            current_user["client_id"], limit, skip,
        )
    result = []
    for row in rows:
        d = dict(row)
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
        result.append(d)
    return result


@router.patch("/{lead_id}/status", summary="Update lead status")
async def update_lead_status(
    lead_id: str,
    status: str,
    current_user: dict = Depends(get_current_user),
) -> dict:
    allowed = {"new", "contacted", "qualified", "closed"}
    if status not in allowed:
        raise HTTPException(status_code=422, detail=f"status must be one of {sorted(allowed)}")
    pool = get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "UPDATE leads SET status = $1 WHERE id = $2 AND client_id = $3",
            status, lead_id, current_user["client_id"],
        )
    if result == "UPDATE 0":
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"lead_id": lead_id, "status": status}
