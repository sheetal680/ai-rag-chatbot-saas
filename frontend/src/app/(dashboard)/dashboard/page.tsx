"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { BarChart2, FileText, MessageSquare, Users, ArrowRight } from "lucide-react";
import { getAnalyticsSummary } from "@/lib/api";
import { CLIENT_ID } from "@/lib/constants";
import PageHeader from "@/components/dashboard/PageHeader";
import StatCard from "@/components/dashboard/StatCard";
import Skeleton from "@/components/ui/Skeleton";
import type { AnalyticsSummary } from "@/types";

const QUICK_LINKS = [
  {
    href: "/dashboard/documents",
    label: "Manage knowledge base",
    desc: "Upload PDFs, text files, or web pages",
  },
  {
    href: "/dashboard/conversations",
    label: "View conversations",
    desc: "Browse full chat logs with customers",
  },
  {
    href: "/dashboard/leads",
    label: "Review leads",
    desc: "Track contacts captured during chats",
  },
];

export default function DashboardOverviewPage() {
  const [stats, setStats] = useState<AnalyticsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    getAnalyticsSummary(CLIENT_ID)
      .then(setStats)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  }, []);

  const cards = [
    { label: "Total Sessions", value: stats?.total_sessions ?? 0, icon: MessageSquare },
    { label: "Total Messages", value: stats?.total_messages ?? 0, icon: BarChart2 },
    { label: "Leads Captured", value: stats?.total_leads ?? 0, icon: Users },
    { label: "Documents", value: stats?.total_documents ?? 0, icon: FileText },
  ];

  return (
    <div>
      <PageHeader title="Overview" description="Your chatbot at a glance." />

      <div className="space-y-6 p-8">
        {/* Stat cards */}
        {loading ? (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
                <Skeleton className="mb-3 h-3 w-24" />
                <Skeleton className="h-8 w-16" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 px-5 py-8 text-center text-sm text-zinc-500">
            Could not load stats — the backend may be starting up. Refresh to retry.
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
            {cards.map((c) => (
              <StatCard key={c.label} label={c.label} value={c.value} icon={c.icon} />
            ))}
          </div>
        )}

        {/* Quick links */}
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          {QUICK_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="group flex items-center justify-between rounded-xl border border-zinc-800 bg-zinc-900 p-4 transition hover:border-zinc-700 hover:bg-zinc-800/60"
            >
              <div>
                <p className="text-sm font-medium text-zinc-200">{link.label}</p>
                <p className="mt-0.5 text-xs text-zinc-600">{link.desc}</p>
              </div>
              <ArrowRight
                size={14}
                className="shrink-0 text-zinc-600 transition group-hover:text-zinc-400 group-hover:translate-x-0.5"
              />
            </Link>
          ))}
        </div>

        {/* Getting started hint when no data */}
        {!loading && !error && stats?.total_documents === 0 && (
          <div className="rounded-xl border border-blue-900/40 bg-blue-950/30 px-5 py-4">
            <p className="text-sm font-medium text-blue-300">Get started in 3 steps</p>
            <ol className="mt-2 space-y-1 text-xs text-blue-400/80">
              <li>1. Upload your knowledge base documents in <strong className="text-blue-300">Documents</strong></li>
              <li>2. Copy the embed snippet from <strong className="text-blue-300">Settings</strong> and add it to your website</li>
              <li>3. Watch conversations and leads appear here automatically</li>
            </ol>
          </div>
        )}
      </div>
    </div>
  );
}
