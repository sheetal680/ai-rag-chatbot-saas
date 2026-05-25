// ─── Chat ────────────────────────────────────────────────────────────────────

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  isError?: boolean;
  isStreaming?: boolean;
}

export interface ChatSession {
  session_id: string;
  client_id: string;
  created_at: string;
  messages: Message[];
}

export interface SessionSummary {
  id: string;
  preview: string;
  createdAt: number;
}

// ─── Leads ───────────────────────────────────────────────────────────────────

export interface Lead {
  name: string;
  email: string;
  phone?: string;
  message?: string;
}

export type LeadStatus = "new" | "contacted" | "qualified" | "closed";

export interface LeadRecord {
  id: string;
  name: string;
  email: string;
  phone?: string;
  status: LeadStatus;
  session_id?: string;
  created_at: string;
}

// ─── Analytics ───────────────────────────────────────────────────────────────

export interface AnalyticsSummary {
  total_sessions: number;
  total_messages: number;
  total_leads: number;
  total_documents: number;
}

export interface VolumePoint {
  date: string;
  messages: number;
  sessions: number;
}

export interface TopQuestion {
  content: string;
  frequency: number;
}

export interface UnansweredQuery {
  content: string;
  occurrences: number;
}

// ─── Conversations ────────────────────────────────────────────────────────────

export interface ConversationSummary {
  session_id: string;
  preview: string;
  message_count: number;
  created_at: string;
  last_message_at: string;
}

export interface ConversationMessage {
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface ConversationDetail {
  session_id: string;
  messages: ConversationMessage[];
}

// ─── Documents ───────────────────────────────────────────────────────────────

export interface Document {
  doc_id: string;
  filename?: string;
  source_url?: string;
  chunk_count: number;
  type: string;
  created_at: string;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: "admin" | "viewer";
  client_id: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}
