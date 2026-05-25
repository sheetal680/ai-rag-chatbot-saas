"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Copy, Check, ThumbsUp, ThumbsDown, Bot, User } from "lucide-react";
import { cn } from "@/utils/cn";
import type { Message } from "@/types";

interface Props {
  message: Message;
}

function formatTime(ts: Date | string): string {
  try {
    return new Intl.DateTimeFormat("en", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    }).format(new Date(ts));
  } catch {
    return "";
  }
}

// Renders streaming text word-by-word with a fade-in on each new token span.
// React preserves existing keyed spans (no re-animation); only newly mounted
// spans (new indices) trigger the CSS animation.
function StreamingContent({ content }: { content: string }) {
  const parts = content.split(/(\s+)/);
  return (
    <p className="whitespace-pre-wrap break-words leading-relaxed text-sm text-zinc-100">
      {parts.map((part, i) => (
        <span key={i} className="animate-fade-in-word">
          {part}
        </span>
      ))}
      <span className="inline-block h-3.5 w-0.5 animate-pulse bg-zinc-300 align-middle ml-0.5" />
    </p>
  );
}

export default function ChatMessage({ message }: Props) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // clipboard unavailable
    }
  }

  // ── User bubble ─────────────────────────────────────────────────────────────
  if (isUser) {
    return (
      <div className="flex justify-end items-end gap-2.5 animate-fade-in-up">
        <div className="flex flex-col items-end gap-1 max-w-[80%] sm:max-w-[70%]">
          <div className="rounded-2xl rounded-br-sm bg-blue-600 px-4 py-3 text-sm leading-relaxed text-white shadow-sm">
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          </div>
          <span className="text-[10px] text-zinc-600 px-1">
            {formatTime(message.timestamp)}
          </span>
        </div>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-700 shadow-sm">
          <User size={14} className="text-zinc-300" />
        </div>
      </div>
    );
  }

  // ── Assistant bubble ─────────────────────────────────────────────────────────
  return (
    <div className="flex items-start gap-3 animate-fade-in-up">
      {/* Bot avatar */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-600 shadow-sm mt-0.5">
        <Bot size={14} className="text-white" />
      </div>

      <div className="flex flex-col gap-1.5 min-w-0 max-w-[85%] sm:max-w-[80%]">
        {/* Bubble */}
        <div
          className={cn(
            "rounded-2xl rounded-tl-sm px-4 py-3 text-sm leading-relaxed shadow-sm",
            message.isError
              ? "border border-red-900/50 bg-red-950/40 text-red-300"
              : "bg-zinc-800 text-zinc-100"
          )}
        >
          {message.isStreaming ? (
            // While streaming: plain text word-by-word (avoids ReactMarkdown
            // re-parsing partial markdown on every token)
            message.content ? (
              <StreamingContent content={message.content} />
            ) : (
              // No tokens yet — show the blinking cursor only
              <span className="inline-block h-3.5 w-0.5 animate-pulse bg-zinc-300 align-middle" />
            )
          ) : message.isError ? (
            <p className="leading-relaxed">{message.content}</p>
          ) : (
            // Streaming done: render full markdown
            <div className="chat-prose">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content || "​"}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Action bar — only on finalized, non-error messages */}
        {!message.isStreaming && !message.isError && message.content && (
          <div className="flex items-center gap-0.5 px-1">
            <span className="text-[10px] text-zinc-600 mr-2">
              {formatTime(message.timestamp)}
            </span>

            {/* Copy */}
            <button
              onClick={handleCopy}
              title="Copy message"
              className="flex h-6 w-6 items-center justify-center rounded-md text-zinc-600 transition hover:bg-zinc-800 hover:text-zinc-300"
            >
              {copied ? (
                <Check size={12} className="text-green-400" />
              ) : (
                <Copy size={12} />
              )}
            </button>

            {/* Thumbs up */}
            <button
              onClick={() => setFeedback(feedback === "up" ? null : "up")}
              title="Good response"
              className={cn(
                "flex h-6 w-6 items-center justify-center rounded-md transition hover:bg-zinc-800",
                feedback === "up"
                  ? "text-green-400"
                  : "text-zinc-600 hover:text-zinc-300"
              )}
            >
              <ThumbsUp size={12} />
            </button>

            {/* Thumbs down */}
            <button
              onClick={() => setFeedback(feedback === "down" ? null : "down")}
              title="Bad response"
              className={cn(
                "flex h-6 w-6 items-center justify-center rounded-md transition hover:bg-zinc-800",
                feedback === "down"
                  ? "text-red-400"
                  : "text-zinc-600 hover:text-zinc-300"
              )}
            >
              <ThumbsDown size={12} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
