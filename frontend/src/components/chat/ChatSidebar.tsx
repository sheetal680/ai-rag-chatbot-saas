"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { MessageSquarePlus, Trash2, ArrowLeft, X } from "lucide-react";
import { cn } from "@/utils/cn";
import type { SessionSummary } from "@/types";

interface Props {
  sessions: SessionSummary[];
  currentSessionId: string;
  onClearAll: () => void;
  onNewChat: () => void;
  onDeleteSession: (id: string) => void;
}

export default function ChatSidebar({
  sessions,
  currentSessionId,
  onClearAll,
  onNewChat,
  onDeleteSession,
}: Props) {
  const router = useRouter();

  return (
    <aside className="flex h-full w-64 shrink-0 flex-col border-r border-zinc-800 bg-zinc-900">
      {/* Header actions */}
      <div className="p-3 space-y-2 border-b border-zinc-800">
        {/* Back to dashboard */}
        <button
          onClick={() => router.push("/dashboard")}
          className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs text-zinc-500 transition hover:bg-zinc-800 hover:text-zinc-300 w-full"
        >
          <ArrowLeft size={13} />
          Back to Dashboard
        </button>

        {/* New Chat — prominent */}
        <button
          onClick={onNewChat}
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-500 active:scale-[0.98] active:bg-blue-700"
        >
          <MessageSquarePlus size={16} />
          New Chat
        </button>
      </div>

      {/* Session list */}
      <div className="flex-1 overflow-y-auto p-2 scrollbar-hide">
        {sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-2 py-10">
            <MessageSquarePlus size={24} className="text-zinc-700" />
            <p className="text-xs text-zinc-600 text-center px-4">
              No conversations yet. Start a new chat!
            </p>
          </div>
        ) : (
          <>
            <p className="px-2 pb-1.5 pt-1 text-[10px] font-semibold uppercase tracking-wider text-zinc-600">
              Recent
            </p>
            <ul className="space-y-0.5">
              {sessions.map((s) => {
                const isActive = currentSessionId === s.id;
                const title =
                  s.preview
                    ? s.preview.length > 42
                      ? s.preview.slice(0, 42) + "…"
                      : s.preview
                    : "New conversation";

                return (
                  <li key={s.id} className="group relative">
                    <Link
                      href={`/chat/${s.id}`}
                      className={cn(
                        "flex items-center rounded-lg px-3 py-2.5 pr-9 text-sm transition select-none",
                        isActive
                          ? "bg-zinc-700/80 text-zinc-100 font-medium"
                          : "text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
                      )}
                    >
                      <span className="truncate leading-snug">{title}</span>
                    </Link>

                    {/* Per-session delete — visible on hover */}
                    <button
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        onDeleteSession(s.id);
                      }}
                      aria-label="Delete conversation"
                      className={cn(
                        "absolute right-1.5 top-1/2 -translate-y-1/2 flex h-6 w-6 items-center justify-center rounded-md transition",
                        "text-zinc-600 opacity-0 group-hover:opacity-100 hover:bg-zinc-700 hover:text-red-400"
                      )}
                    >
                      <X size={13} />
                    </button>
                  </li>
                );
              })}
            </ul>
          </>
        )}
      </div>

      {/* Clear all */}
      {sessions.length > 0 && (
        <div className="border-t border-zinc-800 p-3">
          <button
            onClick={onClearAll}
            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-zinc-500 transition hover:bg-zinc-800 hover:text-red-400"
          >
            <Trash2 size={13} />
            Clear all history
          </button>
        </div>
      )}
    </aside>
  );
}
