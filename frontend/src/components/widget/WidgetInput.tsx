"use client";

import { useRef } from "react";

interface Props {
  value: string;
  onChange: (v: string) => void;
  onSend: (text: string) => void;
  isDisabled: boolean;
  primaryColor: string;
}

export default function WidgetInput({ value, onChange, onSend, isDisabled, primaryColor }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value);
    const el = e.target;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 100) + "px";
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim()) onSend(value);
    }
  };

  return (
    <div className="shrink-0 border-t border-zinc-800 bg-zinc-950 p-3">
      <div className="flex items-end gap-2 rounded-xl border border-zinc-700 bg-zinc-900 px-3 py-2 focus-within:border-zinc-600 transition-colors">
        <textarea
          ref={ref}
          rows={1}
          value={value}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          disabled={isDisabled}
          placeholder="Type a message…"
          className="flex-1 resize-none bg-transparent text-sm text-zinc-100 placeholder-zinc-500 outline-none disabled:opacity-50"
          style={{ maxHeight: "100px" }}
        />
        <button
          onClick={() => { if (value.trim()) onSend(value); }}
          disabled={!value.trim() || isDisabled}
          aria-label="Send"
          className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-white transition-opacity disabled:opacity-30"
          style={{ background: primaryColor }}
        >
          <svg
            width="13"
            height="13"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
      <p className="mt-1.5 text-center text-[10px] text-zinc-700">Powered by AI</p>
    </div>
  );
}
