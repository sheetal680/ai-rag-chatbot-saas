# CLAUDE.md — Backend

This file gives Claude Code context specific to the backend directory.

## Language and Framework

Python 3.11 · FastAPI · Pydantic v2 · asyncpg (Supabase / PostgreSQL) · ChromaDB · Groq / Gemini / sentence-transformers · LangChain 0.3.x · structlog

## Layer Rules (STRICT)

```
api/v1/routes/   → HTTP only. Validate input, call one service method, return response.
                   Never put business logic here. Never import from services/ directly
                   inside another service (services don't call each other — they call db/ and rag/).

services/        → Business logic. Orchestrate db + rag + external APIs.
                   One service per domain: chat_service, document_service.

rag/             → Pure RAG logic only. No HTTP, no DB calls, no service imports.
                   Entry points: ingest_document(), query_rag().

ingestion/       → Ingestion coordination. Wraps parsers/ + rag/ pipeline.
                   Use when orchestrating multi-source or batch ingestion.

parsers/         → Text extraction only. Input: bytes or URL. Output: plain string.
                   No chunking, no embedding, no DB calls.

db/              → Client singletons. No business logic. Return db handles only.

core/            → Config (Pydantic Settings), logging setup, security utils.
                   config.py must stay the single source of truth for all settings.

models/          → Pydantic schemas for request/response validation.
middleware/      → Starlette middlewares. Register in main.py.
utils/           → Pure functions. No FastAPI, no DB, no OpenAI imports.
schemas/         → Generic response shapes (PaginatedResponse, ErrorResponse, etc.)
```

## Multi-Tenancy

Every PostgreSQL row and every ChromaDB collection MUST include a `client_id`.
`get_collection(client_id)` in `db/chromadb.py` namespaces ChromaDB automatically.
`sanitize_client_id()` in `utils/validators.py` must be called before using client_id as a collection name.

## Adding a New Route

1. Create route handler in `api/v1/routes/your_domain.py` — HTTP logic only.
2. Add service function in `services/your_service.py` — business logic.
3. Add Pydantic models in `models/your_model.py`.
4. Register router in `api/v1/__init__.py`.
5. Write unit test in `tests/unit/test_your_service.py`.

## System Prompt

Lives in `prompts/system/base_system.txt` at the project root (NOT inside backend/).
`chat_service.py` reads it lazily via `_load_system_prompt()` (cached after first read).
The `{context}` placeholder is filled with retrieved RAG chunks at runtime.

## Error Responses

Always raise `HTTPException(status_code=..., detail="message")`.
FastAPI serialises this as `{"detail": "message"}` — never return a different error shape.

## Testing

```bash
# Unit tests — fast, no real DB or network
pytest tests/unit -v

# Integration tests — need .env with real credentials
pytest tests/integration -v
```

`tests/conftest.py` provides a `client` fixture with the PostgreSQL pool mocked out.
Integration tests that need real services must use a separate fixture with a real `.env`.

## Running Locally

```bash
uvicorn main:app --reload --port 8000
# Swagger: http://localhost:8000/docs
```

## What Is Not in MVP

- Multi-tenant isolation fully enforced (client_id scaffolded everywhere, not enforced in auth middleware)
- Rate limiting
- Background task queue (Celery / ARQ)
- Billing / Stripe
