-- ─────────────────────────────────────────────────────────────────────────────
-- AI RAG Chatbot SaaS — Supabase (PostgreSQL) Schema
--
-- How to use:
--   1. Open your Supabase project → SQL Editor
--   2. Paste this entire file and click Run
--   3. All tables and indexes are created idempotently (safe to re-run)
--
-- Note: This project uses its own JWT auth (not Supabase Auth), so Row Level
-- Security is not enabled here. Tenant isolation is enforced at the app layer
-- via client_id filtering in every query.
-- ─────────────────────────────────────────────────────────────────────────────

-- ── Users ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id               TEXT PRIMARY KEY,
    name             TEXT NOT NULL,
    email            TEXT UNIQUE NOT NULL,
    hashed_password  TEXT NOT NULL,
    role             TEXT NOT NULL DEFAULT 'admin'
                     CHECK (role IN ('admin', 'viewer')),
    client_id        TEXT NOT NULL,
    is_active        BOOLEAN NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS users_email_idx  ON users (email);
CREATE INDEX IF NOT EXISTS users_client_idx ON users (client_id);

-- ── Sessions ──────────────────────────────────────────────────────────────────
-- One row per chat session. message_count is incremented atomically on each
-- exchange (user message + assistant reply = +2).
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

-- ── Messages ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,
    session_id  TEXT NOT NULL,
    client_id   TEXT NOT NULL,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS messages_session_time_idx
    ON messages (session_id, created_at ASC);
CREATE INDEX IF NOT EXISTS messages_client_time_idx
    ON messages (client_id, created_at ASC);

-- ── Documents ─────────────────────────────────────────────────────────────────
-- Metadata record for each ingested document. The actual vectors live in
-- ChromaDB (namespaced by client_id). filename XOR source_url is populated
-- depending on whether the document came from a file upload or a URL ingest.
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

-- ── Leads ─────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS leads (
    id          TEXT PRIMARY KEY,
    client_id   TEXT NOT NULL,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL,
    phone       TEXT,
    session_id  TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'new'
                CHECK (status IN ('new', 'contacted', 'qualified', 'closed')),
    source      TEXT NOT NULL DEFAULT 'web_widget',
    message     TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS leads_client_time_idx
    ON leads (client_id, created_at DESC);

-- ── WhatsApp Sessions ─────────────────────────────────────────────────────────
-- Tracks per-user WhatsApp conversation state between turns.
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
