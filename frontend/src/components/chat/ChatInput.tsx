"use client";

import { KeyboardEvent, useRef, useEffect, useState } from "react";
import { SendHorizonal } from "lucide-react";
import { cn } from "@/utils/cn";

const MAX_CHARS = 2000;

interface Props {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export default function ChatInput({ onSend, disabled }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [charCount, setCharCount] = useState(0);

  function resize() {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    // allow up to ~8 rows
    el.style.height = Math.min(el.scrollHeight, 200) + "px";
  }

  useEffect(() => {
    resize();
    ref.current?.focus();
  }, []);

  function submit() {
    const value = ref.current?.value.trim();
    if (!value || disabled || charCount > MAX_CHARS) return;
    onSend(value);
    if (ref.current) {
      ref.current.value = "";
      ref.current.style.height = "auto";
      setCharCount(0);
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function handleInput() {
    resize();
    setCharCount(ref.current?.value.length ?? 0);
  }

  const isOverLimit = charCount > MAX_CHARS;
  const isEmpty = charCount === 0;
  const canSend = !disabled && !isEmpty && !isOverLimit;

  return (
    <div className="border-t border-zinc-800 bg-zinc-950 px-3 sm:px-6 pt-3 pb-4">
      <div
        className={cn(
          "rounded-2xl border bg-zinc-900 px-4 py-3 transition-all",
          isOverLimit
            ? "border-red-500/60 ring-1 ring-red-500/20"
            : "border-zinc-700 focus-within:border-zinc-500 focus-within:ring-1 focus-within:ring-zinc-500/20"
        )}
      >
        <textarea
          ref={ref}
          rows={1}
          disabled={disabled}
          placeholder="Message AI Assistant… (Shift+Enter for new line)"
          onInput={handleInput}
          onKeyDown={handleKeyDown}
          className="w-full resize-none bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none disabled:opacity-50 leading-6 min-h-[28px]"
        />

        {/* Bottom row: char count + send */}
        <div className="flex items-center justify-between mt-2.5">
          <span
            className={cn(
              "text-xs transition-colors",
              isEmpty
                ? "opacity-0"
                : isOverLimit
                ? "text-red-400"
                : charCount > MAX_CHARS * 0.85
                ? "text-yellow-500"
                : "text-zinc-600"
            )}
          >
            {charCount.toLocaleString()} / {MAX_CHARS.toLocaleString()}
          </span>

          <button
            onClick={submit}
            disabled={!canSend}
            aria-label="Send message"
            className={cn(
              "flex h-8 w-8 items-center justify-center rounded-lg transition-all",
              canSend
                ? "bg-blue-600 text-white shadow-sm hover:bg-blue-500 active:scale-95 active:bg-blue-700"
                : "bg-zinc-800 text-zinc-600 cursor-not-allowed"
            )}
          >
            <SendHorizonal size={15} />
          </button>
        </div>
      </div>

      <p className="mt-2 text-center text-[10px] text-zinc-700">
        AI can make mistakes — verify important information.
      </p>
    </div>
  );
}
