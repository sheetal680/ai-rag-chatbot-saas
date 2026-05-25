import axios from "axios";
import type {
  AnalyticsSummary,
  AuthUser,
  ConversationDetail,
  ConversationSummary,
  Document,
  LeadRecord,
  TokenResponse,
  TopQuestion,
  UnansweredQuery,
  VolumePoint,
} from "@/types";

export const api = axios.create({
  baseURL: (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000") + "/api/v1",
  headers: { "Content-Type": "application/json" },
});

// Attach the stored JWT to every request automatically.
// Reads directly from localStorage to avoid a circular dependency with authStore.
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("auth_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ─── Auth ─────────────────────────────────────────────────────────────────────

export async function loginUser(
  email: string,
  password: string
): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/login", { email, password });
  return data;
}

export async function registerUser(
  name: string,
  email: string,
  password: string
): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/register", { name, email, password });
  return data;
}

export async function getMe(): Promise<AuthUser> {
  const { data } = await api.get<AuthUser>("/auth/me");
  return data;
}

// ─── Chat ─────────────────────────────────────────────────────────────────────

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatStreamEvent {
  token?: string;
  done?: boolean;
  session_id?: string;
  lead_captured?: boolean;
  error?: string;
}

export async function* streamChat(
  question: string,
  sessionId: string,
  clientId: string,
  history: ChatMessage[]
): AsyncGenerator<ChatStreamEvent> {
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const res = await fetch(`${apiBase}/api/v1/chat/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      question,
      session_id: sessionId,
      client_id: clientId,
      history,
    }),
  });

  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          yield JSON.parse(line.slice(6)) as ChatStreamEvent;
        } catch {
          // skip malformed SSE lines
        }
      }
    }
  }
}

// ─── Documents ────────────────────────────────────────────────────────────────

export async function uploadDocument(
  file: File,
  clientId: string
): Promise<{ doc_id: string; chunk_count: number }> {
  const form = new FormData();
  form.append("file", file);
  form.append("client_id", clientId);
  const { data } = await api.post("/documents/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

/** @deprecated Use uploadDocument instead */
export async function uploadPdf(
  file: File,
  clientId: string
): Promise<{ doc_id: string; chunk_count: number }> {
  return uploadDocument(file, clientId);
}

export async function ingestUrl(
  url: string,
  clientId: string
): Promise<{ doc_id: string; chunk_count: number }> {
  const { data } = await api.post("/documents/ingest-url", null, {
    params: { url, client_id: clientId },
  });
  return data;
}

export async function listDocuments(
  clientId: string,
  skip = 0,
  limit = 50
): Promise<Document[]> {
  const { data } = await api.get<Document[]>("/documents/", {
    params: { client_id: clientId, skip, limit },
  });
  return data;
}

export async function deleteDocument(
  docId: string,
  clientId: string
): Promise<{ deleted: boolean }> {
  const { data } = await api.delete(`/documents/${docId}`, {
    params: { client_id: clientId },
  });
  return data;
}

// ─── Analytics ────────────────────────────────────────────────────────────────

export async function getAnalyticsSummary(clientId: string): Promise<AnalyticsSummary> {
  const { data } = await api.get<AnalyticsSummary>("/analytics/summary", {
    params: { client_id: clientId },
  });
  return data;
}

export async function listConversations(
  clientId: string,
  skip = 0,
  limit = 30
): Promise<ConversationSummary[]> {
  const { data } = await api.get<ConversationSummary[]>("/analytics/conversations", {
    params: { client_id: clientId, skip, limit },
  });
  return data;
}

export async function getConversation(
  sessionId: string,
  clientId: string
): Promise<ConversationDetail> {
  const { data } = await api.get<ConversationDetail>(
    `/analytics/conversations/${sessionId}`,
    { params: { client_id: clientId } }
  );
  return data;
}

export async function getVolume(
  clientId: string,
  days = 30
): Promise<VolumePoint[]> {
  const { data } = await api.get<VolumePoint[]>("/analytics/volume", {
    params: { client_id: clientId, days },
  });
  return data;
}

export async function getTopQuestions(
  clientId: string,
  limit = 10
): Promise<TopQuestion[]> {
  const { data } = await api.get<TopQuestion[]>("/analytics/top-questions", {
    params: { client_id: clientId, limit },
  });
  return data;
}

export async function getUnanswered(
  clientId: string,
  limit = 10
): Promise<UnansweredQuery[]> {
  const { data } = await api.get<UnansweredQuery[]>("/analytics/unanswered", {
    params: { client_id: clientId, limit },
  });
  return data;
}

// ─── Leads ────────────────────────────────────────────────────────────────────

export async function listLeads(
  clientId: string,
  skip = 0,
  limit = 50
): Promise<LeadRecord[]> {
  const { data } = await api.get<LeadRecord[]>("/leads/", {
    params: { client_id: clientId, skip, limit },
  });
  return data;
}

export async function updateLeadStatus(
  leadId: string,
  status: string,
  clientId: string
): Promise<{ lead_id: string; status: string }> {
  const { data } = await api.patch(`/leads/${leadId}/status`, null, {
    params: { status, client_id: clientId },
  });
  return data;
}
