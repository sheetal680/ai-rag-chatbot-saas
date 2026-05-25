"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import WidgetHeader from "./WidgetHeader";
import WidgetInput from "./WidgetInput";
import WidgetLeadForm from "./WidgetLeadForm";
import WidgetMessage from "./WidgetMessage";

interface WMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  isError?: boolean;
  isStreaming?: boolean;
}

const SUGGESTIONS = [
  "What can you help me with?",
  "Tell me about your services",
  "How do I get started?",
];

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

function TypingIndicator() {
  return (
    <div className="flex items-end gap-1 pl-1">
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          className="h-2 w-2 rounded-full bg-zinc-500 animate-dot-bounce"
          style={{ animationDelay: `${i * 0.16}s` }}
        />
      ))}
    </div>
  );
}

export default function WidgetChatInner() {
  const params = useSearchParams();

  const clientId    = params.get("clientId")    ?? "default";
  const apiUrl      = params.get("apiUrl")      ?? (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000");
  const primaryColor= params.get("primaryColor")?? "#2563eb";
  const companyName = params.get("companyName") ?? "AI Assistant";
  const greeting    = params.get("greeting")    ?? "Hi! How can I help you today?";

  const [messages, setMessages]       = useState<WMessage[]>([]);
  const [input, setInput]             = useState("");
  const [isTyping, setIsTyping]       = useState(false);
  const [showLeadForm, setShowLeadForm] = useState(false);
  const [leadSubmitted, setLeadSubmitted] = useState(false);
  const [sessionId]                   = useState(uid);
  const bottomRef = useRef<HTMLDivElement>(null);

  const userCount = messages.filter((m) => m.role === "user").length;

  useEffect(() => {
    if (userCount === 3 && !leadSubmitted) setShowLeadForm(true);
  }, [userCount, leadSubmitted]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping, showLeadForm]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || isTyping) return;

    const history = messages.map((m) => ({ role: m.role, content: m.content }));

    setMessages((prev) => [...prev, { id: uid(), role: "user", content: text }]);
    setInput("");
    setIsTyping(true);

    const assistantId = uid();
    setMessages((prev) => [
      ...prev,
      { id: assistantId, role: "assistant", content: "", isStreaming: true },
    ]);

    try {
      const res = await fetch(`${apiUrl}/api/v1/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: text,
          client_id: clientId,
          session_id: sessionId,
          history,
        }),
      });

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader  = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer    = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() ?? "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const ev = JSON.parse(line.slice(6));
            if (ev.token !== undefined) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? { ...m, content: m.content + ev.token }
                    : m
                )
              );
            }
            if (ev.done || ev.error !== undefined) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? {
                        ...m,
                        isStreaming: false,
                        ...(ev.error ? { content: ev.error, isError: true } : {}),
                      }
                    : m
                )
              );
            }
          } catch {
            // skip malformed SSE line
          }
        }
      }
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? {
                ...m,
                content: "Sorry, I couldn't reach the server. Please try again.",
                isError: true,
                isStreaming: false,
              }
            : m
        )
      );
    } finally {
      setIsTyping(false);
    }
  };

  const hasStreamingMessage = messages.some((m) => m.isStreaming);
  const handleClose = () => window.parent.postMessage({ type: "chatbot:close" }, "*");

  return (
    <div className="flex h-screen flex-col bg-zinc-950">
      <WidgetHeader
        companyName={companyName}
        primaryColor={primaryColor}
        onClose={handleClose}
      />

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="space-y-3">
            <div className="flex items-start gap-2">
              <div
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-xs font-bold text-white"
                style={{ background: primaryColor }}
              >
                {companyName.charAt(0).toUpperCase()}
              </div>
              <div className="max-w-[85%] rounded-2xl rounded-bl-sm bg-zinc-800 px-3.5 py-2.5 text-sm text-zinc-100">
                {greeting}
              </div>
            </div>
            <div className="flex flex-wrap gap-2 pl-10">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  className="rounded-full border border-zinc-700 px-3 py-1 text-xs text-zinc-400 transition-colors hover:border-zinc-500 hover:text-zinc-200"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <WidgetMessage
            key={msg.id}
            role={msg.role}
            content={msg.content}
            primaryColor={primaryColor}
            isError={msg.isError}
            isStreaming={msg.isStreaming}
          />
        ))}

        {isTyping && !hasStreamingMessage && <TypingIndicator />}

        {showLeadForm && !leadSubmitted && (
          <WidgetLeadForm
            clientId={clientId}
            apiUrl={apiUrl}
            sessionId={sessionId}
            onSuccess={() => {
              setLeadSubmitted(true);
              setShowLeadForm(false);
            }}
          />
        )}

        <div ref={bottomRef} />
      </div>

      <WidgetInput
        value={input}
        onChange={setInput}
        onSend={sendMessage}
        isDisabled={isTyping}
        primaryColor={primaryColor}
      />
    </div>
  );
}
