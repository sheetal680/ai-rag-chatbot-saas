import { PanelLeft, Bot, Trash2 } from "lucide-react";

interface Props {
  onToggleSidebar: () => void;
  sidebarOpen: boolean;
  onClearChat: () => void;
  hasMessages: boolean;
}

export default function ChatHeader({
  onToggleSidebar,
  sidebarOpen,
  onClearChat,
  hasMessages,
}: Props) {
  return (
    <header className="flex items-center gap-3 border-b border-zinc-800 bg-zinc-950/95 backdrop-blur-sm px-4 py-3 sticky top-0 z-10 shrink-0">
      {/* Sidebar toggle */}
      <button
        onClick={onToggleSidebar}
        aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
        title={sidebarOpen ? "Close sidebar" : "Open sidebar"}
        className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-400 transition hover:bg-zinc-800 hover:text-zinc-100"
      >
        <PanelLeft size={18} />
      </button>

      {/* Bot avatar */}
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-600 shadow-sm shrink-0">
        <Bot size={17} className="text-white" />
      </div>

      {/* Title + status */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-zinc-100 truncate">
          AI Support Assistant
        </p>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="h-1.5 w-1.5 rounded-full bg-green-400 shadow-sm shadow-green-400/50" />
          <p className="text-xs text-zinc-500">Online · Ready to help</p>
        </div>
      </div>

      {/* Clear conversation */}
      {hasMessages && (
        <button
          onClick={onClearChat}
          title="Clear conversation"
          className="flex h-8 w-8 items-center justify-center rounded-lg text-zinc-500 transition hover:bg-zinc-800 hover:text-red-400"
        >
          <Trash2 size={16} />
        </button>
      )}
    </header>
  );
}
