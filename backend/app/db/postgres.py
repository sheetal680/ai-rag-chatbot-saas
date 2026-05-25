"""PostgreSQL connection pool via asyncpg.

Call connect_db() on startup, disconnect_db() on shutdown.
Use get_pool() anywhere in the service layer to acquire a connection.

asyncpg is imported lazily so this module can be imported (and mocked)
in unit tests without asyncpg being installed.
"""
from __future__ import annotations

import structlog

from app.core.config import settings

logger = structlog.get_logger()

_pool = None  # asyncpg.Pool at runtime


async def connect_db() -> None:
    url = settings.DATABASE_URL
    if not url or not url.startswith(("postgresql", "postgres")):
        logger.warning(
            "db.skipped",
            reason="DATABASE_URL is empty or not a PostgreSQL URL — running without DB",
        )
        return
    import asyncpg
    global _pool
    logger.info("db.connecting")
    _pool = await asyncpg.create_pool(
        dsn=url,
        min_size=2,
        max_size=10,
        command_timeout=30,
    )
    logger.info("db.connected")


async def disconnect_db() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("db.disconnected")


def get_pool():
    """Return the active connection pool. Raises if no DB is configured."""
    if _pool is None:
        raise RuntimeError(
            "No database connection. Set DATABASE_URL to a PostgreSQL URI in .env."
        )
    return _pool


async def ensure_tables() -> None:
    """Create all tables and indexes if they don't already exist. Idempotent."""
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute(_SCHEMA_SQL)
    logger.info("db.tables_ready")


# ── DDL ───────────────────────────────────────────────────────────────────────

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id               TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    email            TEXT UNIQUE NOT NULL,
    hashed_password  TEXT NOT NULL,
    role             TEXT NOT NULL DEFAULT 'admin',
    client_id        TEXT NOT NULL,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS users_email_idx  ON users (email);
CREATE INDEX IF NOT EXISTS users_client_idx ON users (client_id);

CREATE TABLE IF NOT EXISTS sessions (
    id              TEXT PRIMARY KEY,
    client_id       TEXT NOT NULL,
    preview         TEXT NOT NULL DEFAULT '',
    message_count   INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS sessions_client_time_idx
    ON sessions (client_id, last_message_at DESC);

CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL,
    client_id   TEXT NOT NULL,
    role        TEXT NOT NULL,
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS messages_session_time_idx
    ON messages (session_id, created_at ASC);
CREATE INDEX IF NOT EXISTS messages_client_time_idx
    ON messages (client_id, created_at ASC);

CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    client_id   TEXT NOT NULL,
    filename    TEXT,
    source_url  TEXT,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    type        TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS documents_client_time_idx
    ON documents (client_id, created_at DESC);

CREATE TABLE IF NOT EXISTS leads (
    id          TEXT PRIMARY KEY,
    client_id   TEXT NOT NULL,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    phone       TEXT,
    session_id  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'new',
    source      TEXT NOT NULL DEFAULT 'web_widget',
    message     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS leads_client_time_idx
    ON leads (client_id, created_at DESC);

CREATE TABLE IF NOT EXISTS wa_sessions (
    id                  TEXT PRIMARY KEY,
    from_number         TEXT NOT NULL,
    profile_name        TEXT NOT NULL DEFAULT '',
    client_id           TEXT NOT NULL,
    user_message_count  INTEGER NOT NULL DEFAULT 0,
    awaiting_lead       BOOLEAN NOT NULL DEFAULT FALSE,
    lead_captured       BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_message_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""
