import { create } from "zustand";
import type { Message } from "@/types";

// ── localStorage helpers ───────────────────────────────────────────────────────

const MSG_KEY = (sid: string) => `chat_messages_${sid}`;

type PersistedMsg = Omit<Message, "timestamp"> & { timestamp: string };

function saveToStorage(sessionId: string | null, messages: Message[]): void {
  if (!sessionId || typeof window === "undefined") return;
  try {
    // Never persist an in-flight streaming message
    const rows: PersistedMsg[] = messages
      .filter((m) => !m.isStreaming)
      .map((m) => ({
        ...m,
        timestamp:
          m.timestamp instanceof Date
            ? m.timestamp.toISOString()
            : String(m.timestamp),
      }));
    localStorage.setItem(MSG_KEY(sessionId), JSON.stringify(rows));
  } catch {
    // ignore quota errors
  }
}

function loadFromStorage(sessionId: string): Message[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(MSG_KEY(sessionId));
    if (!raw) return [];
    const rows = JSON.parse(raw) as PersistedMsg[];
    return rows.map((m) => ({ ...m, timestamp: new Date(m.timestamp) }));
  } catch {
    return [];
  }
}

// ── Store ──────────────────────────────────────────────────────────────────────

interface ChatState {
  sessionId: string | null;
  messages: Message[];
  loading: boolean;
  error: string | null;
  initSession: (id: string) => void;
  addMessage: (msg: Message) => void;
  appendToken: (id: string, token: string) => void;
  finalizeMessage: (id: string) => void;
  setMessageError: (id: string, error: string) => void;
  setLoading: (v: boolean) => void;
  setError: (err: string | null) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessionId: null,
  messages: [],
  loading: false,
  error: null,

  // Load persisted messages when switching to a new session
  initSession: (id) => {
    if (get().sessionId !== id) {
      const stored = loadFromStorage(id);
      set({ sessionId: id, messages: stored, error: null });
    }
  },

  // Save user messages immediately so they survive a page refresh even
  // before the assistant reply arrives
  addMessage: (msg) => {
    set((s) => ({ messages: [...s.messages, msg], error: null }));
    if (msg.role === "user") {
      const { sessionId, messages } = get();
      saveToStorage(sessionId, messages.filter((m) => !m.isStreaming));
    }
  },

  // Hot path — no persistence here; finalizeMessage does it once streaming ends
  appendToken: (id, token) =>
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === id ? { ...m, content: m.content + token } : m
      ),
    })),

  // Persist the completed exchange (user + assistant) once streaming is done
  finalizeMessage: (id) => {
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === id ? { ...m, isStreaming: false } : m
      ),
    }));
    const { sessionId, messages } = get();
    saveToStorage(sessionId, messages);
  },

  // Persist even on error so the error message survives a refresh
  setMessageError: (id, error) => {
    set((s) => ({
      messages: s.messages.map((m) =>
        m.id === id
          ? { ...m, content: error, isError: true, isStreaming: false }
          : m
      ),
    }));
    const { sessionId, messages } = get();
    saveToStorage(sessionId, messages);
  },

  setLoading: (v) => set({ loading: v }),
  setError: (err) => set({ error: err }),

  // Clear in-memory state AND the localStorage entry for this session
  clearMessages: () => {
    const { sessionId } = get();
    set({ messages: [], error: null });
    if (sessionId && typeof window !== "undefined") {
      localStorage.removeItem(MSG_KEY(sessionId));
    }
  },
}));
