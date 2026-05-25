# Deployment Guide

Step-by-step instructions to go from local development to a live production deployment.

---

## Architecture Overview

```
                   ┌─────────────────────────────┐
  Browser  ───────▶│   Vercel (Next.js frontend) │
                   └──────────────┬──────────────┘
                                  │ HTTPS API calls
                                  ▼
                   ┌─────────────────────────────┐
                   │  Railway / Render (FastAPI)  │
                   │  - REST API                  │
                   │  - RAG pipeline              │
                   │  - JWT auth                  │
                   └────┬──────────────┬──────────┘
                        │              │
               ┌────────▼──────┐  ┌───▼────────────────────┐
               │  Supabase     │  │  ChromaDB              │
               │  (PostgreSQL) │  │  (persistent volume on │
               │  - users      │  │   Railway / Render)    │
               │  - sessions   │  └────────────────────────┘
               │  - messages   │
               │  - leads      │
               │  - documents  │
               └────────┬──────┘
                        │
               ┌────────▼───────────────┐
               │  Groq API (primary)    │
               │  + Gemini (fallback)   │
               │  sentence-transformers │
               │  (embeddings, local)   │
               └────────────────────────┘
```

---

## Prerequisites

- GitHub account with the project pushed to a repository
- [Supabase](https://supabase.com) account (free tier, no credit card required)
- [Groq API](https://console.groq.com) key — free tier available, no billing required
- [Google AI Studio](https://aistudio.google.com) key — optional, used as Gemini fallback
- [Railway](https://railway.app) account (preferred) **or** [Render](https://render.com) account
- [Vercel](https://vercel.com) account (free)

---

## Step 1 — Supabase Setup

Supabase is a hosted PostgreSQL platform with a generous free tier (500 MB storage, no credit card required).

1. Go to [supabase.com](https://supabase.com) → **Start your project** → sign up with GitHub
2. Click **New project** → choose your organisation → set:
   - **Name:** `ai-rag-chatbot`
   - **Database password:** generate a strong one and **save it**
   - **Region:** closest to your Railway/Render backend
3. Wait ~2 minutes for provisioning.
4. **Create the schema:**
   - Go to **SQL Editor** in the left sidebar
   - Paste the contents of `backend/schema.sql` and click **Run**
   - All tables and indexes are created. You should see "Success" for each statement.
5. **Get the connection string:**
   - Go to **Settings → Database → Connection string → URI**
   - Choose **Direct connection** (not the pooler — asyncpg manages its own pool)
   - Copy the URI. It looks like:
     ```
     postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
     ```
   - Append `?sslmode=require` to the end. **Save this** — it becomes your `DATABASE_URL`.

> **Free tier note:** Supabase pauses projects after 1 week of inactivity. The first request after a pause takes ~10 seconds (cold start). Upgrade to the Pro plan ($25/month) for always-on production use.

---

## Step 2 — Generate a Secret Key

Run this locally and save the output — this is your `SECRET_KEY`:

```bash
# Python
python -c "import secrets; print(secrets.token_hex(32))"

# Or OpenSSL
openssl rand -hex 32
```

---

## Step 3 — Deploy Backend to Railway (Recommended)

### 3a. Create Railway project

1. Go to [railway.app](https://railway.app) → **New Project**
2. Choose **Deploy from GitHub repo** → select your repository
3. Railway will detect the `backend/railway.toml` and Dockerfile automatically
4. Set the **Root Directory** to `backend`

### 3b. Set environment variables

In Railway → your service → **Variables**, add:

| Variable | Value |
|---|---|
| `ENVIRONMENT` | `production` |
| `SECRET_KEY` | *(output from Step 2)* |
| `GROQ_API_KEY` | `gsk_...` *(from console.groq.com)* |
| `GEMINI_API_KEY` | `AIza...` *(optional — Gemini fallback)* |
| `DATABASE_URL` | *(Supabase direct connection URI from Step 1, with ?sslmode=require)* |
| `ALLOWED_ORIGINS` | *(leave blank for now — fill in after Vercel deploy in Step 6)* |
| `CHROMA_PERSIST_DIR` | `/app/chroma_data` |
| `LOG_LEVEL` | `INFO` |

### 3c. Add a persistent volume for ChromaDB

Railway → your service → **Volumes** → **New Volume**:

- Mount path: `/app/chroma_data`
- Size: 1 GB

> **Important:** Without this volume, all vector embeddings are deleted every time you redeploy. Your documents would need to be re-uploaded.

### 3d. Deploy

Click **Deploy**. Railway builds the Docker image and starts the service (~3–5 minutes first time).

Once deployed, copy the public URL (e.g. `https://ai-rag-chatbot-production.up.railway.app`).

### 3e. Verify backend

Open: `https://your-railway-url.up.railway.app/health`

Expected:
```json
{"status": "ok", "version": "0.1.0", "env": "production"}
```

---

## Step 4 — Deploy Backend to Render (Alternative)

If you prefer Render over Railway:

1. The `render.yaml` file at the repo root is already configured
2. Go to [render.com](https://render.com) → **New** → **Blueprint**
3. Connect your GitHub repository — Render reads `render.yaml` automatically
4. Fill in the environment variables marked `sync: false` in the Render dashboard
5. Render provisions the service + a 1 GB persistent disk for ChromaDB

> **Note:** The free Render tier sleeps after 15 minutes of inactivity, causing ~30-second cold starts on the first request. Use the **Starter** plan ($7/month) for always-on production.

---

## Step 5 — Deploy Frontend to Vercel

### 5a. Import project

1. Go to [vercel.com](https://vercel.com) → **Add New Project**
2. Import from GitHub → select your repository
3. Set the **Root Directory** to `frontend`
4. Vercel auto-detects Next.js from `package.json`

### 5b. Set environment variables

In Vercel → your project → **Settings** → **Environment Variables**:

| Variable | Value | Environments |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `https://your-railway-url.up.railway.app` | All |
| `NEXT_PUBLIC_CLIENT_ID` | `default` | All |

### 5c. Deploy

Click **Deploy**. Vercel builds and hosts your Next.js app.

Copy the production URL (e.g. `https://your-app.vercel.app`).

---

## Step 6 — Wire CORS: Backend Knows About the Frontend

Now that you have your Vercel URL, update `ALLOWED_ORIGINS` in Railway/Render:

```
ALLOWED_ORIGINS=https://your-app.vercel.app
```

With a custom domain:
```
ALLOWED_ORIGINS=https://your-app.vercel.app,https://yourdomain.com
```

Trigger a redeploy on Railway/Render for the CORS setting to take effect.

---

## Step 7 — Create Your First Admin Account

Both services are live. Now create an account:

1. Open `https://your-app.vercel.app/signup`
2. Enter your name, email, and a strong password
3. You will be redirected to `/dashboard`

Your account is saved in Supabase (PostgreSQL). All future dashboard access requires login.

---

## Production Checklist

Run through every section before going live.

### Infrastructure

- [ ] Railway volume mounted at `/app/chroma_data` (or Render disk at same path)
- [ ] `CHROMA_PERSIST_DIR` env var matches the volume mount path exactly
- [ ] Supabase schema applied (`schema.sql` run in SQL Editor — no red errors)
- [ ] `DATABASE_URL` uses **direct connection** (port 5432) with `?sslmode=require`
- [ ] `ALLOWED_ORIGINS` set to the exact Vercel URL — no trailing slash, no wildcards
- [ ] `ENVIRONMENT=production` is set on Railway/Render

### Security

- [ ] `SECRET_KEY` is at least 32 random hex chars (never a guessable string)
- [ ] `SECRET_KEY`, `DATABASE_URL`, `GROQ_API_KEY` are env vars — never hardcoded
- [ ] `.env` and `.env.local` are in `.gitignore` and NOT committed to the repo
- [ ] Swagger UI is disabled on production: `GET /docs` returns 404
- [ ] `POST /api/v1/documents/upload` without JWT returns `401`
- [ ] `GET /api/v1/leads/` without JWT returns `401`
- [ ] Unauthenticated browser visit to `/dashboard` redirects to `/login`
- [ ] HMAC signature validation active on WhatsApp webhook (if WhatsApp is enabled)

### Core Functionality

- [ ] `GET /health` → `{"status": "ok"}`
- [ ] `GET /health/ready` → `{"status": "ok", "db": "ok"}`
- [ ] `/signup` creates an account and redirects to `/dashboard`
- [ ] `/login` works with the created credentials; JWT stored in cookie and localStorage
- [ ] `/dashboard/documents` — upload a PDF; confirm it appears in the list
- [ ] `/dashboard/documents` — ingest a URL; confirm it appears in the list
- [ ] `/chat` — type a question about uploaded content; receive a streamed AI answer
- [ ] Typing indicator shows during the initial connection; streaming cursor appears during token delivery
- [ ] Lead capture modal appears after 3 chat messages; submitting it records a lead in `/dashboard/leads`
- [ ] `/dashboard/analytics` — stat cards show non-zero values after test messages

### Performance

- [ ] First chat response arrives within 5 seconds (measures embedding + ChromaDB + Groq latency)
- [ ] Document upload completes within 30 seconds for a 10-page PDF
- [ ] Railway service memory usage stable after 10 chat requests (no leak)
- [ ] Supabase connection pool healthy: `GET /health/ready` never times out under light load

### CORS and Networking

- [ ] Browser DevTools → Network tab — no CORS errors on any API call
- [ ] SSE stream stays connected for multi-sentence answers (no premature disconnection)
- [ ] Embed widget loads on an external site via the `<script>` tag without CORS errors
- [ ] WhatsApp webhook verification: `GET /api/v1/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=...` returns the challenge (if WhatsApp is configured)

### Monitoring (post-launch)

- [ ] Railway → **Metrics** — track memory and CPU over 24 hours
- [ ] Set up Railway/Render deploy notifications (email or Slack)
- [ ] Add Supabase connection alert: Supabase → **Database** → **Reports** → watch connection count
- [ ] Review `/dashboard/analytics` unanswered queries after first real users — use results to add missing documents

---

## Environment Variable Reference

### Backend

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | Yes | — | JWT signing key — 32+ random hex chars |
| `DATABASE_URL` | Yes | — | Supabase direct PostgreSQL connection URI |
| `ALLOWED_ORIGINS` | Yes | — | Comma-separated frontend origin(s) |
| `ENVIRONMENT` | Yes | `development` | `development` / `staging` / `production` |
| `GROQ_API_KEY` | Recommended | — | Groq API key (primary LLM) |
| `GEMINI_API_KEY` | No | — | Google Gemini key (fallback LLM) |
| `LLM_PROVIDER` | No | `auto` | `auto` / `groq` / `gemini` / `ollama` |
| `GROQ_MODEL` | No | `llama-3.3-70b-versatile` | Groq chat model |
| `GEMINI_MODEL` | No | `gemini-1.5-flash` | Gemini chat model |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | sentence-transformers model (local) |
| `CHROMA_PERSIST_DIR` | No | `./chroma_data` | ChromaDB storage path |
| `LOG_LEVEL` | No | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `PORT` | No | `8000` | Injected by Railway/Render automatically |

### Frontend (Vercel)

| Variable | Required | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Yes | Full backend URL (no trailing slash) |
| `NEXT_PUBLIC_CLIENT_ID` | No | Default: `default` (MVP single-tenant) |

---

## Troubleshooting

**Backend won't start**
- Check Railway/Render build logs for Python import errors
- Verify `SECRET_KEY`, `DATABASE_URL`, and `GROQ_API_KEY` (or `GEMINI_API_KEY`) are set
- `ENVIRONMENT` must be exactly `development`, `staging`, or `production`

**CORS errors in the browser (Network tab shows blocked requests)**
- `ALLOWED_ORIGINS` must exactly match the Vercel origin (no trailing slash)
- Redeploy the backend after changing `ALLOWED_ORIGINS`

**ChromaDB data lost after redeploy**
- The persistent volume must be mounted at the path in `CHROMA_PERSIST_DIR`
- Railway: verify in the **Volumes** tab
- Render: disk section in `render.yaml` must match `CHROMA_PERSIST_DIR`

**401 on dashboard API calls**
- Token may have expired (7-day lifetime) — sign out and back in
- Check DevTools → Application → Local Storage → `auth_token` key exists

**Supabase connection timeout / SSL error**
- Ensure `?sslmode=require` is appended to `DATABASE_URL`
- Use the **direct connection** URI (port 5432), not the pooler (port 6543)
- URL-encode any special characters in the database password

**Swagger docs not visible on production**
- Intentional — docs are disabled when `ENVIRONMENT=production`
- Use `ENVIRONMENT=staging` for a preview environment with docs enabled

---

## Expected Monthly Costs

| Service | Plan | Cost/month |
|---|---|---|
| Vercel | Hobby (free for personal use) | $0 |
| Railway | Hobby ($5 credit included) | ~$5 |
| Supabase | Free tier (500 MB, pauses after 1 week idle) | $0 |
| ChromaDB volume (1 GB on Railway) | Included in Railway | $0 |
| Groq API | Free tier (generous limits) | $0 |
| Google Gemini | Free tier (optional fallback) | $0 |
| **Total** | | **~$5/month** |

Embeddings run locally inside the Docker container (sentence-transformers / all-MiniLM-L6-v2) — no API cost. Groq's free tier covers hundreds of queries per day. Supabase's free tier suits low-traffic deployments; upgrade to Pro ($25/month) for always-on uptime.

---

## Scaling Path

| Stage | Users | Action |
|---|---|---|
| MVP | 0–50 | Current setup — Railway Hobby + Supabase free tier |
| Early traction | 50–500 | Upgrade Railway to Pro; upgrade Supabase to Pro ($25/month) for always-on DB |
| Growth | 500–5000 | Add 2nd Railway replica; Redis for session caching; Supabase connection pooler (PgBouncer) |
| Multi-tenant SaaS | 5000+ | Organisation model; per-client subdomains; Stripe billing; consider Pinecone or Qdrant instead of local ChromaDB |
