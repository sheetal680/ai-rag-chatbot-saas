"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface Props {
  role: "user" | "assistant";
  content: string;
  primaryColor: string;
  isError?: boolean;
  isStreaming?: boolean;
}

export default function WidgetMessage({ role, content, primaryColor, isError, isStreaming }: Props) {
  if (role === "user") {
    return (
      <div className="flex justify-end animate-fade-in-up">
        <div
          className="max-w-[75%] rounded-2xl rounded-br-sm px-3.5 py-2.5 text-sm text-white"
          style={{ background: primaryColor }}
        >
          {content}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start animate-fade-in-up">
      <div
        className={`max-w-[85%] rounded-2xl rounded-bl-sm px-3.5 py-2.5 text-sm ${
          isError
            ? "border border-red-900/50 bg-red-950/40 text-red-300"
            : "bg-zinc-800 text-zinc-100"
        }`}
      >
        <div className="chat-prose">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{content || "​"}</ReactMarkdown>
          {isStreaming && (
            <span className="inline-block h-3.5 w-0.5 animate-pulse bg-current align-middle ml-0.5" />
          )}
        </div>
      </div>
    </div>
  );
}
