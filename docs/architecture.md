# Architecture Overview

## System Diagram

```
User Browser
     │
     │  HTTPS
     ▼
┌─────────────┐
│  Next.js    │  (Vercel)
│  Frontend   │
└──────┬──────┘
       │  REST  /api/v1/*
       ▼
┌─────────────────────────────────────────────┐
│              FastAPI Backend  (Railway)      │
│                                             │
│  ┌──────────┐   ┌──────────┐   ┌─────────┐ │
│  │  Routes  │──▶│ Services │──▶│   RAG   │ │
│  └──────────┘   └──────────┘   │ Pipeline│ │
│                                └────┬────┘ │
│                                     │      │
│             ┌───────────────────────┴────┐ │
│             ▼                            ▼ │
│      ┌────────────┐             ┌──────────┐│
│      │  Supabase  │             │ ChromaDB ││
│      │ PostgreSQL │             │(vectors) ││
│      └────────────┘             └──────────┘│
└─────────────────────────────────────────────┘
```

## Why This Architecture

### Separation of concerns
- Frontend knows nothing about RAG, vectors, or AI. It only calls REST endpoints.
- Backend owns all business logic. This makes it easy to swap the frontend (e.g., mobile app, WhatsApp) without touching the AI logic.

### FastAPI over Django/Flask
- Async-first: critical for non-blocking LLM API and database calls under concurrent users.
- Built-in Pydantic validation and automatic OpenAPI docs.

### Supabase (PostgreSQL) for structured data
- Free tier: 500 MB storage, no credit card required.
- asyncpg connection pool (min 2, max 10) — low overhead, no ORM, raw SQL.
- Tables: `users`, `sessions`, `messages`, `documents`, `leads`, `wa_sessions`.
- Schema lives in `backend/schema.sql` — run it once in the Supabase SQL Editor.

### ChromaDB for vectors
- Lightweight, no additional cloud service needed in MVP.
- Each tenant gets a namespaced collection (`documents_{client_id}`).
- Can migrate to Pinecone/Weaviate later without changing RAG logic.

### sentence-transformers for embeddings
- `all-MiniLM-L6-v2` — 384-dimensional, runs entirely locally inside the container.
- No API key, no per-token cost, no network call on every query.
- Model is ~80 MB and is pre-downloaded into the Docker image at build time.

## Data Flow: Document Ingestion

```
PDF Upload → parse_pdf() → chunk_text() → embed_texts() → store_chunks() → PostgreSQL metadata record
```

### Groq + Gemini for LLM generation
- Primary: Groq (`llama-3.3-70b-versatile`) — fast inference, generous free tier.
- Fallback: Google Gemini 1.5 Flash — activated automatically if Groq fails.
- Local dev: Ollama (`llama3.1`) — fully offline, no API key needed.

## Data Flow: Chat Query

```
User message → embed_query() [local] → retrieve_chunks() → build prompt + context → Groq LLM → response
                                                                                         ↓ (on failure)
                                                                                    Gemini fallback
```

## Multi-Tenancy

Every document, session, and lead record includes a `client_id`. ChromaDB collections are per-client. In MVP, `client_id` defaults to `"default"` and is passed from the frontend via env var. Enforcement (auth middleware) is a post-MVP task.
