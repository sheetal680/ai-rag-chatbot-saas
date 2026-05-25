"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useChat } from "@/hooks/useChat";
import { useSessionHistory } from "@/hooks/useSessionHistory";
import { randomId } from "@/utils/format";

import ChatHeader from "./ChatHeader";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import ChatSidebar from "./ChatSidebar";
import TypingIndicator from "./TypingIndicator";
import EmptyState from "./EmptyState";
import LeadCaptureModal from "@/components/leads/LeadCaptureModal";

const LEAD_TRIGGER_COUNT = 3;

interface Props {
  sessionId: string;
}

export default function ChatWindow({ sessionId }: Props) {
  const router = useRouter();
  const { messages, loading, sendMessage, clearChat } = useChat(sessionId);
  const { sessions, addSession, deleteSession, clearAll } = useSessionHistory();

  // Default open on desktop, closed on mobile (post-mount to avoid SSR mismatch)
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [leadShown, setLeadShown] = useState(false);
  const [showLeadModal, setShowLeadModal] = useState(false);

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (window.innerWidth >= 768) setSidebarOpen(true);
  }, []);

  // Auto-scroll whenever messages update or loading state changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Track session title — only fires when the first user message is created.
  // IMPORTANT: dep is the MESSAGE ID, not the messages array.
  // Using the full `messages` array as a dep caused the effect to re-run on
  // every streaming token (new array ref each appendToken call), which called
  // addSession hundreds of times and caused "Maximum update depth exceeded".
  const firstUserMsg = messages.find((m) => m.role === "user");
  useEffect(() => {
    if (firstUserMsg) {
      addSession(sessionId, firstUserMsg.content);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [firstUserMsg?.id, sessionId, addSession]);

  // Trigger lead modal once per session after N user messages
  const userCount = messages.filter((m) => m.role === "user").length;
  const hasStreamingMessage = messages.some((m) => m.isStreaming);
  useEffect(() => {
    if (!leadShown && userCount >= LEAD_TRIGGER_COUNT) {
      setLeadShown(true);
      setShowLeadModal(true);
    }
  }, [userCount, leadShown]);

  function handleNewChat() {
    router.push(`/chat/${randomId()}`);
  }

  return (
    <div className="flex h-screen bg-zinc-950 overflow-hidden">
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/60 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-y-0 left-0 z-30 md:relative md:z-auto md:inset-auto">
          <ChatSidebar
            sessions={sessions}
            currentSessionId={sessionId}
            onClearAll={clearAll}
            onNewChat={handleNewChat}
            onDeleteSession={deleteSession}
          />
        </div>
      )}

      {/* Main area */}
      <div className="flex flex-1 flex-col min-w-0">
        <ChatHeader
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen((v) => !v)}
          onClearChat={clearChat}
          hasMessages={messages.length > 0}
        />

        {/* Messages */}
        <div className="flex flex-1 flex-col overflow-y-auto px-3 sm:px-6 py-4 gap-5 scrollbar-hide">
          {messages.length === 0 && !loading ? (
            <EmptyState onSuggest={sendMessage} />
          ) : (
            <>
              {messages.map((msg) => (
                <ChatMessage key={msg.id} message={msg} />
              ))}
              {/* Typing indicator disappears the moment the first streaming
                  message is added (hasStreamingMessage becomes true) */}
              {loading && !hasStreamingMessage && <TypingIndicator />}
            </>
          )}
          <div ref={bottomRef} />
        </div>

        <ChatInput onSend={sendMessage} disabled={loading} />
      </div>

      {showLeadModal && (
        <LeadCaptureModal
          sessionId={sessionId}
          onClose={() => setShowLeadModal(false)}
        />
      )}
    </div>
  );
}
