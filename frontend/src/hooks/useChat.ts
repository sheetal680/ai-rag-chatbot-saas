"use client";

import { useCallback, useEffect, useRef } from "react";
import { useChatStore } from "@/store/chatStore";
import { streamChat } from "@/lib/api";
import { getClientId } from "@/lib/constants";
import type { Message } from "@/types";
import { randomId } from "@/utils/format";

export function useChat(sessionId: string) {
  const {
    messages,
    loading,
    error,
    initSession,
    addMessage,
    appendToken,
    finalizeMessage,
    setMessageError,
    setLoading,
    setError,
    clearMessages,
  } = useChatStore();

  useEffect(() => {
    initSession(sessionId);
  }, [sessionId, initSession]);

  // Keep a ref to `messages` so sendMessage can capture history without being
  // listed as a dep. Without this, sendMessage would be recreated on every
  // streaming token (because messages gets a new array ref each token), which
  // caused cascading re-renders and the "Maximum update depth exceeded" error.
  const messagesRef = useRef<Message[]>(messages);
  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  const sendMessage = useCallback(
    async (text: string) => {
      // Snapshot history from the ref — stable, doesn't re-create the callback
      const history = messagesRef.current.map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const userMsg: Message = {
        id: randomId(),
        role: "user",
        content: text,
        timestamp: new Date(),
      };
      addMessage(userMsg);
      setLoading(true);
      setError(null);

      const assistantId = randomId();
      addMessage({
        id: assistantId,
        role: "assistant",
        content: "",
        timestamp: new Date(),
        isStreaming: true,
      });

      try {
        for await (const event of streamChat(text, sessionId, getClientId(), history)) {
          if (event.token !== undefined) {
            appendToken(assistantId, event.token);
          }
          if (event.error !== undefined) {
            setMessageError(
              assistantId,
              event.error || "Something went wrong. Please try again."
            );
            setError(event.error);
            return;
          }
          if (event.done) {
            // Guard: empty stream → show a friendly error instead of blank bubble
            const current = useChatStore
              .getState()
              .messages.find((m) => m.id === assistantId);
            if (!current?.content.trim()) {
              setMessageError(
                assistantId,
                "Sorry, I couldn't generate a response. Please try again."
              );
            } else {
              finalizeMessage(assistantId);
            }
          }
        }
      } catch (err: unknown) {
        const msg =
          err instanceof Error
            ? err.message
            : "Connection error. Please check your network and try again.";
        setMessageError(assistantId, msg);
        setError(msg);
      } finally {
        setLoading(false);
      }
    },
    // No `messages` here — we read it via messagesRef instead.
    // This keeps sendMessage stable across streaming re-renders.
    [
      sessionId,
      addMessage,
      appendToken,
      finalizeMessage,
      setMessageError,
      setLoading,
      setError,
    ]
  );

  return { messages, loading, error, sendMessage, clearChat: clearMessages };
}
