"use client";

import { useCallback, useEffect, useState } from "react";
import type { SessionSummary } from "@/types";

const STORAGE_KEY = "chat_sessions";
const MAX_SESSIONS = 20;

function loadSessions(): SessionSummary[] {
  if (typeof window === "undefined") return [];
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "[]");
  } catch {
    return [];
  }
}

export function useSessionHistory() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);

  useEffect(() => {
    setSessions(loadSessions());
  }, []);

  const addSession = useCallback((id: string, preview: string) => {
    setSessions((prev) => {
      const filtered = prev.filter((s) => s.id !== id);
      const updated = [
        { id, preview: preview.slice(0, 60), createdAt: Date.now() },
        ...filtered,
      ].slice(0, MAX_SESSIONS);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const deleteSession = useCallback((id: string) => {
    setSessions((prev) => {
      const updated = prev.filter((s) => s.id !== id);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });
  }, []);

  const clearAll = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setSessions([]);
  }, []);

  return { sessions, addSession, deleteSession, clearAll };
}
