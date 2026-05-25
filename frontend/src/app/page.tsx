import Link from "next/link";
import { Zap, FileText, Code2, BarChart2, CheckCircle } from "lucide-react";

// ─── Static data ─────────────────────────────────────────────────────────────

const FEATURES = [
  {
    icon: FileText,
    title: "Powered by your documents",
    desc: "Upload PDFs, web pages, or text files. The AI learns your content and answers using only what you provide — no hallucinations.",
  },
  {
    icon: Code2,
    title: "Embed on any website",
    desc: "Two lines of code and the floating widget appears on any site. Fully branded with your colors, name, and welcome message.",
  },
  {
    icon: BarChart2,
    title: "Analytics and lead capture",
    desc: "Every conversation is logged. Contacts who interact with the bot are captured automatically and appear in your leads dashboard.",
  },
];

const STEPS = [
  { n: "01", title: "Upload your content", desc: "Drag-and-drop PDFs, paste a URL, or upload plain text. The pipeline chunks, embeds, and stores everything." },
  { n: "02", title: "Configure your widget", desc: "Set your brand color, company name, and greeting. Copy the two-line embed snippet from the Settings page." },
  { n: "03", title: "Go live", desc: "Paste the snippet on your website. Your AI is live instantly — answering questions 24/7 without any ongoing management." },
];

const CHECKS = [
  "No coding knowledge required",
  "Works with any website or CMS",
  "WhatsApp integration included",
  "Full conversation history",
  "Automatic lead capture",
  "Scales from 1 client to 1,000",
];

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100">

      {/* Nav */}
      <nav className="sticky top-0 z-50 border-b border-zinc-800/60 bg-zinc-950/80 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600">
              <Zap size={13} className="text-white" />
            </div>
            <span className="text-sm font-semibold text-zinc-100">RAGBot</span>
          </div>
          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="rounded-lg bg-zinc-800 px-4 py-2 text-sm font-medium text-zinc-200 transition hover:bg-zinc-700"
            >
              Sign in
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="mx-auto max-w-6xl px-6 pb-24 pt-20 text-center">
        <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-blue-800/50 bg-blue-950/40 px-3 py-1 text-xs text-blue-400">
          <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
          Powered by Groq + RAG
        </div>

        <h1 className="mx-auto mb-5 max-w-3xl text-4xl font-bold leading-tight tracking-tight text-zinc-50 sm:text-5xl lg:text-6xl">
          AI support that{" "}
          <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            knows your business
          </span>
        </h1>

        <p className="mx-auto mb-10 max-w-xl text-base leading-relaxed text-zinc-400 sm:text-lg">
          Train it on your documents. Embed it on your website in 2 minutes.
          Answer customer questions 24/7 — automatically.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4">
          <Link
            href="/login"
            className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            Admin dashboard
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-zinc-800/60 bg-zinc-900/40 py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-12 text-center text-2xl font-bold text-zinc-100">
            Everything you need to deliver AI chatbots for clients
          </h2>
          <div className="grid gap-6 sm:grid-cols-3">
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="rounded-2xl border border-zinc-800 bg-zinc-900 p-6"
              >
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-zinc-800">
                  <f.icon size={18} className="text-blue-400" />
                </div>
                <h3 className="mb-2 text-sm font-semibold text-zinc-100">{f.title}</h3>
                <p className="text-sm leading-relaxed text-zinc-500">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="mb-12 text-center text-2xl font-bold text-zinc-100">
            Live in under 10 minutes
          </h2>
          <div className="grid gap-6 sm:grid-cols-3">
            {STEPS.map((s) => (
              <div key={s.n} className="relative rounded-2xl border border-zinc-800 bg-zinc-900/60 p-6">
                <span className="mb-4 block font-mono text-xs font-bold text-zinc-700">{s.n}</span>
                <h3 className="mb-2 text-sm font-semibold text-zinc-100">{s.title}</h3>
                <p className="text-sm leading-relaxed text-zinc-500">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Checklist */}
      <section className="border-t border-zinc-800/60 bg-zinc-900/40 py-20">
        <div className="mx-auto max-w-6xl px-6 text-center">
          <h2 className="mb-10 text-2xl font-bold text-zinc-100">Built for freelancers and agencies</h2>
          <div className="mx-auto grid max-w-2xl grid-cols-1 gap-3 text-left sm:grid-cols-2">
            {CHECKS.map((c) => (
              <div key={c} className="flex items-center gap-3">
                <CheckCircle size={14} className="shrink-0 text-emerald-500" />
                <span className="text-sm text-zinc-300">{c}</span>
              </div>
            ))}
          </div>

          <div className="mt-12 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/login"
              className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
            >
              Get started free
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-800/60 py-8">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-blue-600">
              <Zap size={11} className="text-white" />
            </div>
            <span className="text-xs font-semibold text-zinc-400">RAGBot</span>
          </div>
          <p className="text-xs text-zinc-700">
            Built with Next.js, FastAPI, ChromaDB &amp; Groq LLM
          </p>
          <div className="flex gap-4 text-xs text-zinc-600">
            <Link href="/login" className="hover:text-zinc-400">Dashboard</Link>
            <Link href="/dashboard/settings" className="hover:text-zinc-400">Settings</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
