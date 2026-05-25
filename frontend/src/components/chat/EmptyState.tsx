import { Bot, Sparkles } from "lucide-react";

interface Props {
  onSuggest: (q: string) => void;
}

const SUGGESTED = [
  { emoji: "🏠", text: "What services do you offer?" },
  { emoji: "🚀", text: "How can I get started?" },
  { emoji: "💰", text: "What are your pricing plans?" },
  { emoji: "📞", text: "How do I contact support?" },
];

export default function EmptyState({ onSuggest }: Props) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-8 px-4 py-10 text-center">
      {/* Hero icon */}
      <div className="relative">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-600 shadow-lg shadow-blue-900/30 ring-4 ring-zinc-900">
          <Bot size={32} className="text-white" />
        </div>
        {/* Online dot */}
        <div className="absolute bottom-1 right-1 h-4 w-4 rounded-full bg-green-400 ring-2 ring-zinc-950" />
      </div>

      {/* Greeting */}
      <div className="space-y-2">
        <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">
          How can I help you today?
        </h1>
        <p className="text-sm text-zinc-500 max-w-sm mx-auto leading-relaxed">
          I&apos;m your AI assistant. Ask me anything about our products,
          services, or documentation.
        </p>
      </div>

      {/* Suggested questions */}
      <div className="w-full max-w-lg">
        <div className="flex items-center justify-center gap-1.5 mb-3">
          <Sparkles size={11} className="text-zinc-600" />
          <p className="text-[10px] font-semibold uppercase tracking-widest text-zinc-600">
            Try asking
          </p>
        </div>
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          {SUGGESTED.map((q) => (
            <button
              key={q.text}
              onClick={() => onSuggest(q.text)}
              className="group flex items-center gap-3 rounded-xl border border-zinc-700/80 bg-zinc-800/40 px-4 py-3.5 text-left text-sm text-zinc-300 transition hover:border-zinc-500 hover:bg-zinc-800 hover:text-zinc-100 active:scale-[0.97]"
            >
              <span className="text-lg shrink-0 select-none">{q.emoji}</span>
              <span className="leading-snug">{q.text}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
