import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/utils/cn";
import type { ConversationMessage } from "@/types";

interface Props {
  sessionId: string;
  messages: ConversationMessage[];
  loading: boolean;
}

export default function ConversationDetail({ messages, loading }: Props) {
  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <p className="text-sm text-zinc-600">Loading…</p>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-6 scrollbar-hide">
      {messages.map((msg, i) => {
        const isUser = msg.role === "user";
        return (
          <div key={i} className={cn("flex items-end gap-2", isUser && "flex-row-reverse")}>
            <div
              className={cn(
                "max-w-[76%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
                isUser
                  ? "rounded-br-sm bg-blue-600 text-white"
                  : "rounded-bl-sm bg-zinc-800 text-zinc-100"
              )}
            >
              {isUser ? (
                <p>{msg.content}</p>
              ) : (
                <div className="chat-prose">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
