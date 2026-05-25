"use client";

import { useEffect } from "react";
import { CheckCircle, XCircle, Info, X } from "lucide-react";
import { useToastStore, type Toast } from "@/store/toastStore";
import { cn } from "@/utils/cn";

const ICONS = {
  success: CheckCircle,
  error:   XCircle,
  info:    Info,
} as const;

const STYLES = {
  success: "border-emerald-800/50 bg-emerald-950/80 text-emerald-300",
  error:   "border-red-800/50   bg-red-950/80   text-red-300",
  info:    "border-zinc-700     bg-zinc-900     text-zinc-200",
} as const;

function ToastItem({ toast }: { toast: Toast }) {
  const remove = useToastStore((s) => s.remove);
  const Icon = ICONS[toast.type];

  return (
    <div
      className={cn(
        "flex items-start gap-3 rounded-xl border px-4 py-3 text-sm shadow-lg",
        "animate-fade-in-up backdrop-blur-sm",
        STYLES[toast.type]
      )}
    >
      <Icon size={15} className="mt-0.5 shrink-0" />
      <p className="flex-1 leading-snug">{toast.message}</p>
      <button
        onClick={() => remove(toast.id)}
        className="shrink-0 opacity-60 transition-opacity hover:opacity-100"
        aria-label="Dismiss"
      >
        <X size={13} />
      </button>
    </div>
  );
}

export default function Toaster() {
  const toasts = useToastStore((s) => s.toasts);

  return (
    <div
      aria-live="polite"
      className="fixed bottom-6 right-6 z-[9999] flex w-80 flex-col gap-2"
    >
      {toasts.map((t) => (
        <ToastItem key={t.id} toast={t} />
      ))}
    </div>
  );
}
