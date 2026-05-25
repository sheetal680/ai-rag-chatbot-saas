# API Reference

Base URL: `/api/v1`

Interactive docs available at `GET /docs` (Swagger UI) when the backend is running.

## Chat

### `POST /chat/`

Send a question and receive an AI-generated answer grounded in ingested documents.

**Body:**
```json
{
  "question": "What is your return policy?",
  "session_id": "sess_abc123",
  "client_id": "default",
  "history": [
    { "role": "user", "content": "Hi" },
    { "role": "assistant", "content": "Hello! How can I help?" }
  ]
}
```

**Response:**
```json
{
  "answer": "Our return policy allows ...",
  "session_id": "sess_abc123"
}
```

## Documents

### `POST /documents/upload-pdf`

Upload a PDF for ingestion into the RAG pipeline.

**Form data:** `file` (PDF), `client_id` (string)

**Response:** `{ "doc_id": "...", "chunk_count": 42 }`

### `POST /documents/ingest-url`

Fetch and ingest a web page.

**Query params:** `url`, `client_id`

**Response:** `{ "doc_id": "...", "chunk_count": 18 }`

## Leads

### `POST /leads/`

Capture a lead from a chat session.

**Body:** `{ "name", "email", "phone?", "client_id", "session_id", "message?" }`

### `GET /leads/?client_id=default`

List leads for a client (admin use).

## Analytics

### `GET /analytics/summary?client_id=default`

Returns session, message, lead, and document counts.

## Health

### `GET /health`

Returns `{ "status": "ok", "version": "0.1.0" }`. Used by Railway health checks.
