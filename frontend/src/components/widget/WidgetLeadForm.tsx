"use client";

import { useState } from "react";
import axios from "axios";

interface Props {
  clientId: string;
  apiUrl: string;
  sessionId: string;
  onSuccess: () => void;
}

export default function WidgetLeadForm({ clientId, apiUrl, sessionId, onSuccess }: Props) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !email.trim()) return;
    setLoading(true);
    setError("");
    try {
      await axios.post(`${apiUrl}/api/v1/leads/`, {
        name: name.trim(),
        email: email.trim(),
        client_id: clientId,
        session_id: sessionId,
      });
      onSuccess();
    } catch {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-fade-in-up rounded-xl border border-zinc-700 bg-zinc-900/80 p-4">
      <p className="mb-0.5 text-sm font-semibold text-zinc-100">Stay connected</p>
      <p className="mb-3 text-xs text-zinc-400">
        Leave your details and we&apos;ll follow up with you.
      </p>
      <form onSubmit={handleSubmit} className="space-y-2">
        <input
          type="text"
          placeholder="Your name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-zinc-500 transition-colors"
        />
        <input
          type="email"
          placeholder="Email address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 outline-none focus:border-zinc-500 transition-colors"
        />
        {error && <p className="text-xs text-red-400">{error}</p>}
        <button
          type="submit"
          disabled={loading || !name.trim() || !email.trim()}
          className="w-full rounded-lg bg-blue-600 py-2 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:opacity-50"
        >
          {loading ? "Sending…" : "Send"}
        </button>
      </form>
    </div>
  );
}
