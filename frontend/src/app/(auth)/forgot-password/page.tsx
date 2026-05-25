"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Zap } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    // TODO: call POST /api/v1/auth/forgot-password once implemented
    setSubmitted(true);
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-950 px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
            <Zap size={16} className="text-white" />
          </div>
          <span className="text-sm font-semibold text-zinc-100">RAG Admin</span>
        </div>

        <div className="rounded-2xl border border-zinc-800 bg-zinc-900 p-8">
          {submitted ? (
            <div className="space-y-4 text-center">
              <p className="text-sm font-medium text-zinc-100">Check your email</p>
              <p className="text-xs text-zinc-500">
                If an account exists for <span className="text-zinc-300">{email}</span>, a
                reset link has been sent.
              </p>
              <Link
                href="/login"
                className="mt-2 inline-flex items-center gap-1.5 text-xs text-zinc-500 transition hover:text-zinc-300"
              >
                <ArrowLeft size={12} /> Back to sign in
              </Link>
            </div>
          ) : (
            <>
              <h1 className="mb-1 text-xl font-semibold text-zinc-100">Reset password</h1>
              <p className="mb-6 text-sm text-zinc-500">
                Enter your email and we&apos;ll send you a reset link.
              </p>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-zinc-400" htmlFor="email">
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                    className="w-full rounded-xl border border-zinc-700 bg-zinc-800 px-3 py-2.5 text-sm text-zinc-100 placeholder-zinc-600 focus:border-blue-500 focus:outline-none transition"
                  />
                </div>

                <div className="rounded-lg border border-yellow-900/40 bg-yellow-950/20 px-3 py-2">
                  <p className="text-xs text-yellow-600">
                    Password reset emails are not yet wired up — coming in a future release.
                  </p>
                </div>

                <button
                  type="submit"
                  className="w-full rounded-xl bg-blue-600 py-2.5 text-sm font-medium text-white transition hover:bg-blue-500"
                >
                  Send reset link
                </button>
              </form>

              <Link
                href="/login"
                className="mt-6 flex items-center gap-1.5 text-xs text-zinc-600 transition hover:text-zinc-400"
              >
                <ArrowLeft size={12} /> Back to sign in
              </Link>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
