"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { Zap } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { cn } from "@/utils/cn";

export default function SignupPage() {
  const { signUp } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }
    setLoading(true);
    try {
      await signUp(name, email, password);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(detail ?? "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-950 px-4">
      <div className="w-full max-w-sm">
        {/* Logo */}
        <div className="mb-8 flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
            <Zap size={16} className="text-white" />
          </div>
          <span className="text-sm font-semibold text-zinc-100">RAG Admin</span>
        </div>

        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-8">
          <h1 className="mb-1 text-xl font-semibold text-zinc-100">Create account</h1>
          <p className="mb-6 text-sm text-zinc-500">
            Set up your admin account to get started.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-400" htmlFor="name">
                Full name
              </label>
              <input
                id="name"
                type="text"
                autoComplete="name"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Smith"
                className="w-full rounded-xl border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-blue-500 focus:outline-none transition"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-400" htmlFor="email">
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full rounded-xl border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-blue-500 focus:outline-none transition"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-400" htmlFor="password">
                Password
                <span className="ml-1 font-normal text-zinc-600">(min 8 chars)</span>
              </label>
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-xl border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-blue-500 focus:outline-none transition"
              />
            </div>

            {error && (
              <p className="rounded-lg border border-red-900/50 bg-red-950/40 px-3 py-2 text-xs text-red-400">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={loading}
              className={cn(
                "w-full rounded-xl py-2.5 text-sm font-medium text-white transition",
                loading
                  ? "bg-blue-700 opacity-70 cursor-not-allowed"
                  : "bg-blue-600 hover:bg-blue-500"
              )}
            >
              {loading ? "Creating account…" : "Create account"}
            </button>
          </form>

          <p className="mt-6 text-center text-xs text-zinc-600">
            Already have an account?{" "}
            <Link href="/login" className="text-zinc-400 transition hover:text-zinc-200">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </main>
  );
}
