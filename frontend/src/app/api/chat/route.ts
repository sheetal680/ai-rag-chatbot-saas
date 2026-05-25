import { NextRequest } from "next/server";

// Thin proxy: client → Next.js API route → FastAPI backend (SSE pass-through).
export async function POST(req: NextRequest) {
  const body = await req.json();
  const apiBase = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

  const upstream = await fetch(`${apiBase}/api/v1/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  return new Response(upstream.body, {
    status: upstream.status,
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
      "Connection": "keep-alive",
    },
  });
}
