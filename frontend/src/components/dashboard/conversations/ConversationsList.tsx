import { MessageSquare } from "lucide-react";
import { cn } from "@/utils/cn";
import type { ConversationSummary } from "@/types";

interface Props {
  conversations: ConversationSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export default function ConversationsList({ conversations, selectedId, onSelect }: Props) {
  if (conversations.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center py-20 text-center">
        <div>
          <MessageSquare size={28} className="mx-auto mb-2 text-zinc-700" />
          <p className="text-sm text-zinc-600">No conversations yet.</p>
        </div>
      </div>
    );
  }

  return (
    <ul className="divide-y divide-zinc-800/60">
      {conversations.map((c) => (
        <li key={c.session_id}>
          <button
            onClick={() => onSelect(c.session_id)}
            className={cn(
              "w-full px-4 py-3 text-left transition hover:bg-zinc-800/40",
              selectedId === c.session_id && "bg-zinc-800"
            )}
          >
            <p className="truncate text-sm font-medium text-zinc-200">
              {c.preview || "New conversation"}
            </p>
            <div className="mt-0.5 flex items-center gap-2 text-xs text-zinc-600">
              <span>{c.message_count} messages</span>
              <span>·</span>
              <span>
                {new Date(c.created_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })}
              </span>
            </div>
          </button>
        </li>
      ))}
    </ul>
  );
}
