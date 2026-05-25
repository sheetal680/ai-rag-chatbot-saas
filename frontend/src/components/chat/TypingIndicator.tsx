import { Bot } from "lucide-react";

export default function TypingIndicator() {
  return (
    <div className="flex items-start gap-3 animate-fade-in-up">
      {/* Matches ChatMessage bot avatar */}
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-600 shadow-sm mt-0.5">
        <Bot size={14} className="text-white" />
      </div>

      <div className="rounded-2xl rounded-tl-sm bg-zinc-800 px-4 py-3.5 shadow-sm">
        <span className="flex items-center gap-1.5 h-4">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="h-2 w-2 rounded-full bg-zinc-400 animate-dot-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </span>
      </div>
    </div>
  );
}
