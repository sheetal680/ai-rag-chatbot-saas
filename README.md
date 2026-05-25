# AI RAG Chatbot SaaS

A production-ready, multi-client AI chatbot service powered by Retrieval-Augmented Generation (RAG). Businesses upload their documents; customers get instant, accurate answers.

## Tech Stack

| Layer | Technology | Cost |
|---|---|---|
| Frontend | Next.js 16 · TypeScript · Tailwind CSS | Free (Vercel) |
| Backend | Python 3.11 · FastAPI · asyncpg | ~$5/mo (Railway Hobby) |
| Primary DB | Supabase (PostgreSQL) | Free tier (500 MB) |
| Vector DB | ChromaDB (self-hosted in container) | Free |
| LLM — Primary | Groq `llama-3.3-70b-versatile` | Free tier |
| LLM — Fallback | Google Gemini 1.5 Flash | Free tier |
| LLM — Local dev | Ollama `llama3.1` | Free |
| Embeddings | sentence-transformers `all-MiniLM-L6-v2` | Free (local, 384-dim) |
| Parsing | LangChain · PyMuPDF · BeautifulSoup4 | Free |
| WhatsApp | Meta Cloud API (WhatsApp Business) | Free (1,000 conv/mo) |
| Deployment | Vercel (frontend) · Railway (backend) | Free + ~$5/mo |

## Project Structure

```
ai-rag-chatbot-saas/
├── frontend/          # Next.js app — customer chat UI + admin dashboard
├── backend/           # FastAPI — RAG pipeline, chat, ingestion APIs
├── docs/              # Architecture, API reference, deployment guides
├── prompts/           # Versioned system prompts (treated as config)
├── scripts/           # Ops scripts: ingestion, seeding, pipeline tests
├── .gitignore
├── README.md
└── CLAUDE.md
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # fill in secrets
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # fill in secrets
npm run dev
```

## Core Features

- **Document Ingestion** — PDF, DOCX, web pages, plain text via LangChain parsers
- **RAG Pipeline** — chunk → embed (local) → store → retrieve → generate
- **AI Chat** — Groq (primary) + Gemini fallback, context-aware responses
- **Admin Dashboard** — upload docs, view conversations, manage leads, analytics
- **Lead Capture** — collect visitor info during both web chat and WhatsApp sessions
- **WhatsApp Integration** — Meta Cloud API, free for first 1,000 conversations/month
- **Embed Widget** — drop-in `<script>` tag for any website
- **Analytics** — session counts, message volume, lead conversion

## Environment Variables

See `backend/.env.example` and `frontend/.env.local.example` for required variables.

## API Documentation

Run the backend and visit `http://localhost:8000/docs` for the interactive Swagger UI.

## Deployment

See [docs/deployment.md](docs/deployment.md) for Vercel + Railway deployment guide.
