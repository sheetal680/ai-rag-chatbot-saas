"""Authentication service — user registration and login logic."""
from __future__ import annotations

from datetime import UTC, datetime

import structlog

from app.core.security import create_access_token, hash_password, verify_password
from app.db.postgres import get_pool
from app.models.user import TokenResponse, UserCreate, UserResponse
from app.utils.id_generator import new_id

logger = structlog.get_logger()


async def register_user(data: UserCreate) -> TokenResponse:
    """Create a new user account and return a signed token.

    Raises ValueError if the email is already registered.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", data.email)
        if existing:
            raise ValueError("An account with this email already exists.")

        user_id = new_id()
        client_id = user_id  # MVP: each user is their own tenant
        now = datetime.now(UTC)

        await conn.execute(
            """
            INSERT INTO users (id, name, email, hashed_password, role, client_id, is_active, created_at)
            VALUES ($1, $2, $3, $4, 'admin', $5, TRUE, $6)
            """,
            user_id, data.name, data.email, hash_password(data.password), client_id, now,
        )

    logger.info("auth_service.register", user_id=user_id)
    return _build_token_response({
        "id": user_id,
        "name": data.name,
        "email": data.email,
        "role": "admin",
        "client_id": client_id,
    })


async def login_user(email: str, password: str) -> TokenResponse:
    """Verify credentials and return a signed token.

    Raises ValueError if credentials are invalid.
    """
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, email, hashed_password, role, client_id, is_active FROM users WHERE email = $1",
            email,
        )

    if not row or not verify_password(password, row["hashed_password"]):
        raise ValueError("Invalid email or password.")
    if not row["is_active"]:
        raise ValueError("Account is deactivated.")

    logger.info("auth_service.login", user_id=row["id"])
    return _build_token_response(dict(row))


async def get_user_by_id(user_id: str) -> UserResponse | None:
    """Fetch user details from the database by ID."""
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT id, name, email, role, client_id FROM users WHERE id = $1",
            user_id,
        )
    if not row:
        return None
    return UserResponse(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        role=row["role"],
        client_id=row["client_id"],
    )


# ── helpers ───────────────────────────────────────────────────────────────────

def _build_token_response(doc: dict) -> TokenResponse:
    user = UserResponse(
        id=doc["id"],
        name=doc["name"],
        email=doc["email"],
        role=doc["role"],
        client_id=doc["client_id"],
    )
    token = create_access_token(
        subject=doc["id"],
        extra_claims={
            "email": doc["email"],
            "role": doc["role"],
            "client_id": doc["client_id"],
        },
    )
    return TokenResponse(access_token=token, user=user)
