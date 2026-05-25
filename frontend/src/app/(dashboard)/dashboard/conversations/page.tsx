"use client";

import { useEffect, useState } from "react";
import { getConversation, listConversations } from "@/lib/api";
import { CLIENT_ID } from "@/lib/constants";
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
    listConversations(CLIENT_ID).then(setConversations).catch(() => null);
  }, []);

  async function handleSelect(sessionId: string) {
    if (sessionId === selected) return;
    setSelected(sessionId);
    setLoadingDetail(true);
    setDetail(null);
    try {
      const data = await getConversation(sessionId, CLIENT_ID);
      setDetail(data);
    } catch {
      setDetail({ session_id: sessionId, messages: [] });
    } finally {
      setLoadingDetail(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      <PageHeader
        title="Conversations"
        description={`${conversations.length} session${conversations.length !== 1 ? "s" : ""} recorded`}
      />
      <div className="flex flex-1 overflow-hidden">
        {/* Left: session list */}
        <div className="w-72 shrink-0 overflow-y-auto border-r border-zinc-800 scrollbar-hide">
          <ConversationsList
            conversations={conversations}
            selectedId={selected}
            onSelect={handleSelect}
          />
        </div>

        {/* Right: message detail */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {selected === null ? (
            <div className="flex flex-1 items-center justify-center">
              <p className="text-sm text-zinc-600">Select a conversation to view messages</p>
            </div>
          ) : (
            <>
              <div className="border-b border-zinc-800 px-6 py-3">
                <p className="font-mono text-xs text-zinc-600">Session: {selected}</p>
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
