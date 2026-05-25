# CLAUDE.md — AI RAG Chatbot SaaS

This file gives Claude Code the context needed to assist effectively in this project.

## Tech Stack (100% Free Tier)

| Layer | Technology | Cost |
|---|---|---|
| Frontend | Next.js 16 · TypeScript · Tailwind CSS 3 · Zustand | Free |
| Backend | Python 3.11 · FastAPI 0.115 · asyncpg 0.29 | Free |
| LLM (primary) | Groq API — `llama-3.3-70b-versatile` | Free tier |
| LLM (fallback) | Google Gemini 1.5 Flash | Free tier |
| LLM (local dev) | Ollama `llama3.1` — offline, no key | Free |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` — runs locally | Free |
| Vector DB | ChromaDB 0.5.18 — runs in Railway container | Free |
| Primary DB | Supabase (PostgreSQL) — free tier (500 MB) | Free |
| Frontend hosting | Vercel Hobby | Free |
| Backend hosting | Railway Hobby | ~$5/mo |
| WhatsApp | Meta Cloud API — 1,000 conversations/month | Free tier |

**Estimated monthly cost: ~$5** (Railway compute only; all other services use free tiers.)

## Project Overview

Multi-client AI chatbot SaaS. Each client (tenant) uploads their documents (PDF, DOCX, TXT, URLs). The RAG pipeline retrieves relevant chunks and passes them to Groq/Gemini to answer customer questions in real time. An admin dashboard lets clients manage documents, view conversations, and track leads. An embeddable widget and WhatsApp integration extend reach to any channel.

## Architecture in One Sentence

Next.js frontend → FastAPI backend → RAG pipeline (ChromaDB retrieval + Groq/Gemini generation) + Supabase (PostgreSQL) for structured data.

## Repository Layout

```
frontend/   Next.js 16 App Router. Chat UI, admin dashboard, embed widget.
backend/    FastAPI. RAG pipeline, ingestion, chat, analytics, WhatsApp webhook.
docs/       Architecture, API reference, deployment runbooks, client guides.
prompts/    System prompts — version-controlled, never hardcoded.
scripts/    Operational scripts: seed_demo.py, ingest_documents.py, test_rag.py.
schema.sql  PostgreSQL DDL for Supabase — run once in the SQL Editor.
```

## Backend Layer Rules

```
backend/app/
  api/v1/routes/   HTTP handlers only — validate input, call service, return response.
  services/        Business logic. Orchestrates db + rag + external APIs.
  rag/             Pure RAG logic: chunking, embedding, retrieval, generation.
  db/              Client singletons: postgres.py (asyncpg pool), chromadb.py.
  chains/          LLM chain — Groq primary, Gemini fallback, Ollama local.
  embeddings/      LocalEmbedder (sentence-transformers, asyncio.to_thread).
  retrieval/       Semantic retrieval — embeds query, queries ChromaDB, filters.
  models/          Pydantic request/response schemas.
  parsers/         Document parsing only (PDF, HTML, text). No chunking or DB calls.
  core/            Config (pydantic-settings), security (JWT/bcrypt), logging.
```

Never put business logic in route handlers. Never import from `api/` inside `services/`.

## Frontend Layer Rules

```
frontend/src/
  app/             Next.js pages and API routes (App Router).
  components/      Reusable UI — grouped by domain (dashboard/, ui/, widget/).
  lib/             API client, utility functions, constants.
  hooks/           Custom React hooks (useToast, etc.).
  store/           Global state — Zustand (authStore, toastStore).
  types/           Shared TypeScript types.
```

## Key Conventions

- Backend: `snake_case` everywhere (Python convention).
- Frontend: `camelCase` for variables, `PascalCase` for components.
- API versioning: all endpoints under `/api/v1/`.
- Multi-tenancy: every PostgreSQL row and ChromaDB collection includes a `client_id`.
- Secrets: never hardcode. Use environment variables. `.env.example` documents required vars.
- Error responses: always `{ "detail": "message" }` (FastAPI default).
- asyncpg: use `$1`/`$2` positional params; `pool.acquire()` as async context manager.
- asyncpg: `Record` objects don't have `.get()` — use `dict(row)` first or `row["col"]` directly.

## RAG Pipeline Flow

```
Ingest:  Parse doc → chunk (RecursiveCharacterTextSplitter, 500/50)
              → embed locally (all-MiniLM-L6-v2, 384-dim, normalised)
              → store in ChromaDB (per-client collection)
              → write metadata record to Supabase (documents table)

Query:   Embed user question (local) → cosine search ChromaDB (threshold 0.30, top-5)
              → build system+user prompt → call Groq (primary) or Gemini (fallback)
              → stream answer → persist session + messages to Supabase
```

## Database — Supabase (PostgreSQL via asyncpg)

Tables: `users`, `sessions`, `messages`, `documents`, `leads`, `wa_sessions`

Connection pool: min 2, max 10 connections. Managed by `app/db/postgres.py`.
Schema: `backend/schema.sql` — run once in the Supabase SQL Editor, or let
`ensure_tables()` (called on startup) create them automatically.

## WhatsApp — Meta Cloud API

Webhook: `GET /api/v1/whatsapp/webhook` — verify challenge  
         `POST /api/v1/whatsapp/webhook` — inbound JSON, ack 200 immediately,
         process in BackgroundTask, reply via Graph API (`send_whatsapp_message()`).

Signature validation: HMAC-SHA256 of raw body against `META_APP_SECRET`.

## Running Locally

```bash
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env            # fill in GROQ_API_KEY and DATABASE_URL at minimum
uvicorn main:app --reload       # http://localhost:8000/docs

# Frontend
cd frontend
npm install
cp .env.local.example .env.local
npm run dev                     # http://localhost:3000
```

Minimum required env vars to run locally:
- `SECRET_KEY` — any 32-char random string
- `DATABASE_URL` — Supabase direct connection URI (or local Postgres)
- `GROQ_API_KEY` — from console.groq.com (free, no billing required)

## What Is Implemented

- Multi-tenant RAG: per-client document upload, chunking, embedding, retrieval
- PDF, DOCX, TXT, Markdown file ingestion + web URL ingestion
- Chat API with session history and lead capture
- Admin dashboard: documents, conversations, leads, analytics, settings
- JWT authentication (bcrypt, 7-day token, protected routes)
- Embeddable chat widget (vanilla JS IIFE, iframe CSS isolation)
- WhatsApp integration (Meta Cloud API, background task reply)
- Toast notifications, skeleton loaders, marketing landing page
- Demo seed script (`scripts/seed_demo.py`) — Luminary Homes property agency

## What Is NOT Implemented (Post-MVP)

- Billing / Stripe
- SSO / OAuth
- Multi-tenant isolation fully enforced at the DB layer (client_id scaffolded everywhere but not JWT-enforced)
- Rate limiting
- Background task queue (Celery / ARQ)
- CSV export for leads
- Multi-language support

## Testing

```bash
cd backend
pytest tests/unit -v             # fast, no real DB
pytest tests/integration -v      # requires .env with real credentials
```

## Deployment

- Frontend → Vercel (auto-deploy on push to `main`, root dir: `frontend`)
- Backend → Railway (Dockerfile in `backend/`, persistent volume for ChromaDB)
- Database → Supabase (run `schema.sql` once in the SQL Editor)

See `docs/deployment.md` for the full step-by-step guide.
