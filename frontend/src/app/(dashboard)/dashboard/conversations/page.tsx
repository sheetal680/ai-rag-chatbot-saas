"use client";

import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { getConversation, listConversations } from "@/lib/api";
import { getClientId } from "@/lib/constants";
import PageHeader from "@/components/dashboard/PageHeader";
import ConversationsList from "@/components/dashboard/conversations/ConversationsList";
import ConversationDetail from "@/components/dashboard/conversations/ConversationDetail";
import type { ConversationDetail as ConversationDetailType, ConversationSummary } from "@/types";

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<ConversationDetailType | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  useEffect(() => {
    listConversations(getClientId()).then(setConversations).catch(() => null);
  }, []);

  async function handleSelect(sessionId: string) {
    if (sessionId === selected) return;
    setSelected(sessionId);
    setLoadingDetail(true);
    setDetail(null);
    try {
      const data = await getConversation(sessionId, getClientId());
      setDetail(data);
    } catch {
      setDetail({ session_id: sessionId, messages: [] });
    } finally {
      setLoadingDetail(false);
    }
  }

  function handleBack() {
    setSelected(null);
    setDetail(null);
  }

  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="Conversations"
        description={`${conversations.length} session${conversations.length !== 1 ? "s" : ""} recorded`}
      />
      <div className="flex flex-1 overflow-hidden">
        {/* Left: session list — full width on mobile when no selection */}
        <div
          className={[
            "shrink-0 overflow-y-auto border-r border-zinc-800 scrollbar-hide",
            "w-full sm:w-72",
            selected ? "hidden sm:block" : "block",
          ].join(" ")}
        >
          <ConversationsList
            conversations={conversations}
            selectedId={selected}
            onSelect={handleSelect}
          />
        </div>

        {/* Right: message detail — full width on mobile when selected */}
        <div
          className={[
            "flex flex-1 flex-col overflow-hidden",
            selected ? "flex" : "hidden sm:flex",
          ].join(" ")}
        >
          {selected === null ? (
            <div className="flex flex-1 items-center justify-center">
              <p className="text-sm text-zinc-600">Select a conversation to view messages</p>
            </div>
          ) : (
            <>
              <div className="flex items-center gap-3 border-b border-zinc-800 px-4 py-3 sm:px-6">
                <button
                  onClick={handleBack}
                  className="sm:hidden rounded-lg p-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100 transition"
                  aria-label="Back to conversations"
                >
                  <ArrowLeft size={16} />
                </button>
                <p className="font-mono text-xs text-zinc-600 truncate">Session: {selected}</p>
              </div>
              <ConversationDetail
                sessionId={selected}
                messages={detail?.messages ?? []}
                loading={loadingDetail}
              />
            </>
          )}
        </div>
      </div>
    </div>
  );
}
