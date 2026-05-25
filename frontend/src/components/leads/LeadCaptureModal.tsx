"use client";

import { FormEvent, useState } from "react";
import { X, CheckCircle } from "lucide-react";
import { api } from "@/lib/api";
import type { Lead } from "@/types";

interface Props {
  sessionId: string;
  onClose: () => void;
}

export default function LeadCaptureModal({ sessionId, onClose }: Props) {
  const [form, setForm] = useState<Lead>({ name: "", email: "" });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/leads/", { ...form, session_id: sessionId });
      setSubmitted(true);
    } catch {
      // silently ignore — don't block the user from chatting
    } finally {
      setLoading(false);
    }
  }

  return (
    /* Backdrop */
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
      <div className="w-full max-w-sm rounded-2xl border border-zinc-700 bg-zinc-900 shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-4">
          <h3 className="text-sm font-semibold text-zinc-100">
            {submitted ? "You&apos;re all set!" : "Stay connected"}
          </h3>
          <button
            onClick={onClose}
            className="rounded-lg p-1 text-zinc-500 transition hover:bg-zinc-800 hover:text-zinc-300"
          >
            <X size={16} />
          </button>
        </div>

        {submitted ? (
          <div className="flex flex-col items-center gap-3 px-5 py-8 text-center">
            <CheckCircle size={40} className="text-green-500" />
            <p className="text-sm text-zinc-300">
              Thanks! We&apos;ll follow up with you soon.
            </p>
            <button
              onClick={onClose}
              className="mt-2 rounded-xl bg-blue-600 px-6 py-2 text-sm font-medium text-white transition hover:bg-blue-500"
            >
              Continue chatting
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4 px-5 py-5">
            <p className="text-xs text-zinc-500">
              Leave your details and we&apos;ll send you a follow-up from our team.
            </p>

            <div className="space-y-1">
              <label className="text-xs font-medium text-zinc-400" htmlFor="modal-name">
                Name
              </label>
              <input
                id="modal-name"
                required
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                className="w-full rounded-xl border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:border-zinc-500 focus:outline-none"
                placeholder="Your name"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-zinc-400" htmlFor="modal-email">
                Email
              </label>
              <input
                id="modal-email"
                type="email"
                required
                value={form.email}
                onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
                className="w-full rounded-xl border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:border-zinc-500 focus:outline-none"
                placeholder="you@example.com"
              />
            </div>

            <div className="flex gap-2 pt-1">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 rounded-xl bg-blue-600 py-2 text-sm font-medium text-white transition hover:bg-blue-500 disabled:opacity-60"
              >
                {loading ? "Submitting…" : "Submit"}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="rounded-xl border border-zinc-700 bg-zinc-800 px-4 py-2 text-sm text-zinc-400 transition hover:bg-zinc-700 hover:text-zinc-200"
              >
                Skip
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
