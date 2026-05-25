# AI RAG Chatbot — Backend

FastAPI · Python 3.11 · asyncpg · Supabase (PostgreSQL) · ChromaDB · Groq / Gemini / Ollama · sentence-transformers · LangChain · structlog

---

## Quick Start

```bash
# 1. Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env and fill in at minimum: SECRET_KEY, DATABASE_URL, GROQ_API_KEY

# 4. Run dev server (port 8000, hot-reload)
uvicorn main:app --reload

# Or via Make
make dev
```

Swagger UI → http://localhost:8000/docs  
ReDoc      → http://localhost:8000/redoc  
Health     → http://localhost:8000/health

> **Note:** Swagger and ReDoc are disabled when `ENVIRONMENT=production`.

---

## Project Structure

```
backend/
├── main.py                    # FastAPI app — lifespan, CORS, middleware, routers
├── requirements.txt
├── Dockerfile                 # Production container (Railway / Render)
├── Procfile                   # Fallback for Heroku / Render native builds
├── railway.toml               # Railway deployment config
├── schema.sql                 # PostgreSQL DDL — run once in Supabase SQL Editor
├── pytest.ini
├── Makefile
│
├── app/
│   ├── api/v1/
│   │   └── routes/            # HTTP handlers only — no business logic
│   │       ├── auth.py        POST /register  POST /login  GET /me
│   │       ├── chat.py        POST /chat/  (SSE streaming)
│   │       ├── documents.py   POST /upload  POST /ingest-url  DELETE /{id}
│   │       ├── leads.py       POST /  GET /  PATCH /{id}/status
│   │       ├── analytics.py   GET /summary  /conversations  /volume  /top-questions  /unanswered
│   │       └── whatsapp.py    GET /webhook (verify)  POST /webhook (inbound)
│   │
│   ├── core/
│   │   ├── config.py          Pydantic Settings — reads from .env, validates types
│   │   ├── logging.py         structlog setup (JSON in prod, console in dev)
│   │   └── security.py        JWT (HS256, 7-day) + bcrypt via passlib
│   │
│   ├── db/
│   │   ├── postgres.py        asyncpg pool — connect / disconnect / get_pool / ensure_tables
│   │   └── chromadb.py        PersistentClient + get_collection(client_id)
│   │
│   ├── chains/
│   │   └── rag_chain.py       RAGChain: retrieve → prompt → Groq (primary) → Gemini (fallback)
│   │                          .run() full answer  |  .astream() SSE token generator
│   │
│   ├── retrieval/
│   │   ├── semantic.py        ChromaDB cosine search — threshold 0.30, top-5
│   │   └── __init__.py        retrieve() public entry point
│   │
│   ├── embeddings/
│   │   └── local_embedder.py  sentence-transformers all-MiniLM-L6-v2, 384-dim (local)
│   │
│   ├── parsers/               Text extraction only — no chunking, no DB calls
│   │   ├── pdf_parser.py      PyMuPDF (fitz) — bytes → plain text
│   │   ├── docx_parser.py     python-docx — bytes → plain text
│   │   └── web_parser.py      httpx + BeautifulSoup — URL → plain text
│   │
│   ├── prompts/
│   │   ├── templates.py       RAG_SYSTEM prompt, NO_CONTEXT_RESPONSE, chunk format
│   │   └── builder.py         build_rag_messages() — assembles the LangChain message list
│   │
│   ├── services/              Business logic — orchestrates db + rag + external APIs
│   │   ├── chat_service.py    stream_answer() (SSE)  answer_question() (WhatsApp)
│   │   │                      _maybe_capture_lead()  _extract_name()
│   │   ├── auth_service.py    register_user()  login_user()  get_user_by_id()
│   │   ├── document_service.py ingest_file()  ingest_url()  list_documents()  delete_document()
│   │   ├── analytics_service.py get_summary()  list_conversations()  get_volume()
│   │   │                        get_top_questions()  get_unanswered()
│   │   └── whatsapp_service.py process_inbound()  send_whatsapp_message()
│   │
│   ├── models/                Pydantic request/response schemas
│   │   ├── chat.py            ChatRequest, ChatResponse, ChatStreamEvent
│   │   ├── user.py            UserCreate, LoginRequest, TokenResponse, UserResponse
│   │   ├── lead.py            LeadCreate, LeadResponse
│   │   └── document.py        DocumentRecord, IngestResponse
│   │
│   ├── middleware/
│   │   └── request_logging.py Starlette middleware — logs method/path/status/ms
│   │
│   └── utils/
│       ├── id_generator.py    new_id() — ULID-style sortable IDs
│       └── validators.py      sanitize_client_id()
│
└── tests/
    ├── conftest.py            Fixtures — DB pool mocked for unit tests
    ├── unit/                  Fast, no network or DB required
    │   ├── test_chat_streaming.py   23 tests — SSE events, lead detection, RAGChain
    │   ├── test_chunker.py
    │   └── test_validators.py
    └── integration/           Require .env with real credentials
        └── test_health.py
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | — | JWT signing key — `openssl rand -hex 32` |
| `DATABASE_URL` | **Yes** | — | Supabase direct URI + `?sslmode=require` |
| `GROQ_API_KEY` | Recommended | — | Primary LLM — free at console.groq.com |
| `ALLOWED_ORIGINS` | **Yes (prod)** | `http://localhost:3000` | Comma-separated frontend origins |
| `ENVIRONMENT` | No | `development` | `development` / `staging` / `production` |
| `LOG_LEVEL` | No | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `LLM_PROVIDER` | No | `auto` | `auto` / `groq` / `gemini` / `ollama` |
| `GEMINI_API_KEY` | No | — | Fallback LLM — aistudio.google.com |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Groq chat model |
| `GEMINI_MODEL` | No | `gemini-1.5-flash` | Gemini chat model |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | sentence-transformers model (runs locally) |
| `CHROMA_PERSIST_DIR` | No | `./chroma_data` | ChromaDB storage path |
| `CHROMA_COLLECTION_NAME` | No | `documents` | Base collection name (tenant suffix added) |
| `PORT` | No | `8000` | Injected by Railway/Render automatically |
| `META_WEBHOOK_VERIFY_TOKEN` | No | — | WhatsApp — any string you choose |
| `META_APP_SECRET` | No | — | WhatsApp — from Meta App dashboard |
| `META_WHATSAPP_TOKEN` | No | — | WhatsApp — System User access token |
| `META_PHONE_NUMBER_ID` | No | — | WhatsApp — from API Setup page |

---

## API Overview

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/health` | — | Liveness probe |
| GET | `/health/ready` | — | Readiness probe (tests DB connection) |
| POST | `/api/v1/auth/register` | — | Create account, return JWT |
| POST | `/api/v1/auth/login` | — | Verify credentials, return JWT |
| GET | `/api/v1/auth/me` | JWT | Current user profile |
| POST | `/api/v1/chat/` | — | SSE streaming RAG answer |
| POST | `/api/v1/documents/upload` | JWT | Upload and index a file (PDF/DOCX/TXT) |
| POST | `/api/v1/documents/ingest-url` | JWT | Fetch and index a web page |
| GET | `/api/v1/documents/` | JWT | List indexed documents |
| DELETE | `/api/v1/documents/{id}` | JWT | Remove a document |
| POST | `/api/v1/leads/` | — | Capture a lead (public — called by widget) |
| GET | `/api/v1/leads/` | JWT | List leads |
| PATCH | `/api/v1/leads/{id}/status` | JWT | Update lead status |
| GET | `/api/v1/analytics/summary` | JWT | Session / message / lead / doc counts |
| GET | `/api/v1/analytics/conversations` | JWT | List sessions |
| GET | `/api/v1/analytics/conversations/{id}` | JWT | Full message log for a session |
| GET | `/api/v1/analytics/volume` | JWT | Daily message volume (last N days) |
| GET | `/api/v1/analytics/top-questions` | JWT | Most-asked user questions |
| GET | `/api/v1/analytics/unanswered` | JWT | Questions with no-context fallback |
| GET | `/api/v1/whatsapp/webhook` | — | Meta webhook verification challenge |
| POST | `/api/v1/whatsapp/webhook` | HMAC | Inbound WhatsApp messages |

---

## RAG Pipeline

```
Query flow
──────────
User question
    │
    ▼
embed_query()          # all-MiniLM-L6-v2 (384-dim, local — no API cost)
    │
    ▼
retrieve()             # ChromaDB cosine search, threshold 0.30, top-5 chunks
    │
    ├── no chunks found → yield NO_CONTEXT_RESPONSE immediately
    │
    ▼
build_rag_messages()   # system prompt + context chunks + conversation history
    │
    ▼
Groq LLM (primary)     # llama-3.3-70b-versatile, temperature 0.2
    │
    ├── rate-limit / error → Gemini fallback (ainvoke, not streaming)
    │
    ▼
stream tokens → SSE    # data: {"token":"…"}\n\n  …  data: {"done":true}\n\n

Ingest flow
───────────
File bytes / URL
    │
    ▼
parser (PDF/DOCX/web)  # bytes → plain text
    │
    ▼
RecursiveCharacterTextSplitter  # 500-char chunks, 50-char overlap
    │
    ▼
LocalEmbedder.embed()  # sentence-transformers, batched, asyncio.to_thread
    │
    ▼
ChromaDB upsert        # per-client collection: {CHROMA_COLLECTION_NAME}_{client_id}
    │
    ▼
Supabase INSERT        # documents table — metadata record for the dashboard
```

---

## Testing

```bash
# Unit tests — fast, no real DB or network
pytest tests/unit -v

# Integration tests — require .env with real credentials
pytest tests/integration -v

# All tests
pytest -v

# Via Make
make test
make test-integration
make test-all
```

---

## Deployment

### Railway (recommended)

1. Push code to GitHub
2. New Railway project → **Deploy from GitHub repo** → set **Root Directory** to `backend`
3. Railway detects `railway.toml` and the Dockerfile automatically
4. Set environment variables in **Railway → Variables** (see table above)
5. **Railway → Volumes → New Volume** — mount path: `/app/chroma_data`, size: 1 GB  
   *(without this volume, vector embeddings are deleted on every redeploy)*
6. Click **Deploy** — first build takes ~5 minutes (downloads PyTorch + embedding model)
7. Verify: `https://your-service.up.railway.app/health` → `{"status":"ok"}`

### Render (alternative)

```bash
# render.yaml at the repo root is already configured.
# 1. New → Blueprint → connect repo → Render reads render.yaml
# 2. Fill in the sync:false variables in the Render dashboard
# 3. Render provisions the service + 1 GB persistent disk for ChromaDB
```

> The **free Render tier sleeps** after 15 minutes of inactivity (30-second cold start).
> Use the **Starter plan ($7/month)** for production.

### Database setup (Supabase)

```bash
# Run schema.sql once in the Supabase SQL Editor:
# Supabase dashboard → SQL Editor → paste schema.sql → Run
```

> Supabase **pauses projects** after 1 week of inactivity on the free tier.
> Upgrade to Pro ($25/month) for always-on production databases.
