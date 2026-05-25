import type { ChatMessage, ChatStreamEvent } from "@/lib/api";
import { streamChat } from "@/lib/api";

export { streamChat };
export type { ChatMessage, ChatStreamEvent };

export async function fetchChatHistory(sessionId: string): Promise<ChatMessage[]> {
  const res = await fetch(`/api/v1/chat/history/${sessionId}`);
  if (!res.ok) throw new Error("Failed to fetch history");
  return res.json();
}
