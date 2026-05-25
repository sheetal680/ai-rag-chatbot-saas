# AI RAG Chatbot — Frontend

Next.js 16 · TypeScript · Tailwind CSS · App Router · Zustand

## Quick Start

```bash
# 1. Copy env file
cp .env.local.example .env.local

# 2. Install dependencies
npm install

# 3. Start dev server (port 3000)
npm run dev
```

The frontend proxies all `/api/backend/*` requests to the FastAPI backend at `NEXT_PUBLIC_API_URL`.

---

## Folder Structure

```
src/
├── app/                  # Next.js App Router pages & API routes
│   ├── layout.tsx        # Root HTML shell (fonts, metadata, global styles)
│   ├── page.tsx          # Home — redirects to /chat/new
│   ├── globals.css       # Tailwind directives + global base styles
│   ├── (auth)/           # Login & register (MVP placeholder)
│   ├── (dashboard)/      # Admin layout + admin/analytics pages
│   ├── chat/[sessionId]/ # Chatbot UI page
│   └── api/chat/         # Next.js API route → proxies to FastAPI
│
├── components/           # Reusable UI building blocks
│   ├── ui/               # Generic: Button, Input, Card
│   ├── chat/             # ChatWindow, MessageBubble, ChatInput
│   ├── leads/            # LeadCaptureForm
│   ├── admin/            # DocumentUpload
│   └── analytics/        # StatCard
│
├── features/             # Feature barrels — group related exports together
│   ├── chat/             # Re-exports chat components + useChat hook
│   ├── admin/            # Re-exports DocumentUpload + documentService
│   └── analytics/        # Re-exports StatCard
│
├── hooks/                # Custom React hooks
│   ├── useChat.ts        # Chat send/receive + Zustand wiring
│   └── useLocalStorage.ts
│
├── lib/                  # Shared infrastructure
│   ├── api.ts            # Axios instance + typed fetch helpers
│   └── constants.ts      # CLIENT_ID, API_BASE, route constants
│
├── services/             # Raw API call functions (no React)
│   ├── chatService.ts    # Chat history, send message
│   └── documentService.ts# Upload, list, delete documents
│
├── store/                # Global state (Zustand)
│   └── chatStore.ts      # messages[], loading, addMessage, clearMessages
│
├── styles/               # CSS modules & animation files (use sparingly)
│
├── types/                # TypeScript interfaces shared across the app
│   └── index.ts          # Message, Lead, AnalyticsSummary, User, Document
│
└── utils/                # Pure functions with no React/Next dependencies
    ├── cn.ts             # Tailwind class merger (clsx + tailwind-merge)
    └── format.ts         # randomId, formatDate, truncate
```

---

## Key Architectural Decisions

### Why `(dashboard)` and `(auth)` in parentheses?
These are **Route Groups** — Next.js lets you group routes without adding them to the URL. `/app/(dashboard)/admin/page.tsx` resolves to `/admin`, not `/dashboard/admin`. It also lets each group have its own `layout.tsx`.

### Why `features/` on top of `components/`?
`components/` contains pure UI. `features/` re-exports the right components **plus** their service layer as a cohesive unit. Pages import from `features/`, not directly from deep paths.

### Where does the chatbot UI live?
`src/app/chat/[sessionId]/page.tsx` → renders `<ChatWindow sessionId={...} />`
`src/components/chat/` → all chat-specific UI components
`src/hooks/useChat.ts` → all chat state & API logic

### Where do dashboard pages live?
`src/app/(dashboard)/admin/page.tsx` — document uploads  
`src/app/(dashboard)/analytics/page.tsx` — usage stats  
`src/app/(dashboard)/layout.tsx` — shared sidebar navigation

### How does the frontend talk to FastAPI?
Two paths, choose based on use case:

| Path | When to use |
|------|-------------|
| Direct via `src/lib/api.ts` (Axios) | Client components that need real-time responses |
| Via `src/app/api/*/route.ts` (Next.js API routes) | When you want to keep the backend URL server-side only |

`next.config.ts` also sets up a rewrite so `/api/backend/*` → `FastAPI /api/v1/*`.

---

## Environment Variables

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | FastAPI backend URL (default: `http://localhost:8000`) |
| `NEXT_PUBLIC_CLIENT_ID` | Tenant ID for multi-client setup (default: `default`) |

---

## Scripts

```bash
npm run dev          # Dev server with hot reload
npm run build        # Production build
npm run start        # Serve production build
npm run lint         # ESLint check
npm run type-check   # TypeScript check (no emit)
```
