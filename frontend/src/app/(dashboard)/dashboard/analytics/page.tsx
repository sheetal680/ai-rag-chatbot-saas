"use client";

import { useEffect, useState } from "react";
import { BarChart2, FileText, HelpCircle, MessageSquare, Users } from "lucide-react";
import {
  getAnalyticsSummary,
  getTopQuestions,
  getUnanswered,
  getVolume,
} from "@/lib/api";
import { getClientId } from "@/lib/constants";
import PageHeader from "@/components/dashboard/PageHeader";
import StatCard from "@/components/dashboard/StatCard";
import type { AnalyticsSummary, TopQuestion, UnansweredQuery, VolumePoint } from "@/types";

// ─── Sub-components ───────────────────────────────────────────────────────────

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <p className="mb-3 text-xs font-medium uppercase tracking-wide text-zinc-500">
      {children}
    </p>
  );
}

function EmptyNotice({ message }: { message: string }) {
  return (
    <p className="py-10 text-center text-sm text-zinc-600">{message}</p>
  );
}

function QuestionRow({
  rank,
  content,
  badge,
  badgeLabel,
}: {
  rank: number;
  content: string;
  badge: number;
  badgeLabel: string;
}) {
  return (
    <div className="flex items-start gap-3 border-b border-zinc-800/60 py-3 last:border-0">
      <span className="mt-0.5 w-5 shrink-0 font-mono text-xs text-zinc-600">{rank}.</span>
      <p className="flex-1 text-sm text-zinc-200 leading-snug">{content}</p>
      <span className="shrink-0 rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">
        {badge} {badgeLabel}
      </span>
    </div>
  );
}

// ─── Page ─────────────────────────────────────────────────────────────────────

export default function AnalyticsPage() {
  const [stats, setStats]       = useState<AnalyticsSummary | null>(null);
  const [volume, setVolume]     = useState<VolumePoint[]>([]);
  const [topQ, setTopQ]         = useState<TopQuestion[]>([]);
  const [unanswered, setUnanswered] = useState<UnansweredQuery[]>([]);

  useEffect(() => {
    getAnalyticsSummary(getClientId()).then(setStats).catch(() => null);
    getVolume(getClientId(), 14).then(setVolume).catch(() => null);
    getTopQuestions(getClientId()).then(setTopQ).catch(() => null);
    getUnanswered(getClientId()).then(setUnanswered).catch(() => null);
  }, []);

  const maxMessages = Math.max(...volume.map((v) => v.messages), 1);

  return (
    <div>
      <PageHeader title="Analytics" description="Usage statistics for the last 14 days." />

      <div className="space-y-6 p-8">

        {/* ── Stat cards ──────────────────────────────────────────────────── */}
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {[
            { label: "Sessions",  value: stats?.total_sessions  ?? "—", icon: MessageSquare },
            { label: "Messages",  value: stats?.total_messages  ?? "—", icon: BarChart2 },
            { label: "Leads",     value: stats?.total_leads     ?? "—", icon: Users },
            { label: "Documents", value: stats?.total_documents ?? "—", icon: FileText },
          ].map((c) => (
            <StatCard key={c.label} label={c.label} value={c.value} icon={c.icon} />
          ))}
        </div>

        {/* ── Message volume bar chart ─────────────────────────────────────── */}
        <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
          <SectionTitle>Daily message volume (14 days)</SectionTitle>
          {volume.length === 0 ? (
            <EmptyNotice message="No data yet." />
          ) : (
            <>
              <div className="flex h-32 items-end gap-1">
                {volume.map((v) => (
                  <div key={v.date} className="group relative flex flex-1 flex-col items-center">
                    <div
                      className="w-full rounded-t bg-blue-600/70 transition group-hover:bg-blue-500"
                      style={{
                        height: `${Math.round((v.messages / maxMessages) * 100)}%`,
                        minHeight: 2,
                      }}
                    />
                    <span className="absolute bottom-[-18px] hidden text-[9px] text-zinc-600 group-hover:block">
                      {v.date.slice(5)}
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-3 flex justify-between text-[10px] text-zinc-700">
                <span>{volume[0].date.slice(5)}</span>
                <span>{volume[volume.length - 1].date.slice(5)}</span>
              </div>
            </>
          )}
        </div>

        {/* ── Bottom two-column grid ───────────────────────────────────────── */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">

          {/* Top questions */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
            <SectionTitle>Top questions</SectionTitle>
            {topQ.length === 0 ? (
              <EmptyNotice message="No questions recorded yet." />
            ) : (
              <div>
                {topQ.map((q, i) => (
                  <QuestionRow
                    key={i}
                    rank={i + 1}
                    content={q.content}
                    badge={q.frequency}
                    badgeLabel={q.frequency === 1 ? "ask" : "asks"}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Unanswered queries */}
          <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
            <div className="mb-3 flex items-center gap-2">
              <SectionTitle>Unanswered queries</SectionTitle>
              <span className="mb-3 ml-auto shrink-0 rounded-full border border-yellow-800/50 bg-yellow-950/40 px-2 py-0.5 text-[10px] text-yellow-400">
                Knowledge gaps
              </span>
            </div>
            {unanswered.length === 0 ? (
              <div className="py-10 text-center">
                <HelpCircle size={22} className="mx-auto mb-2 text-zinc-700" />
                <p className="text-sm text-zinc-600">No unanswered queries — great coverage!</p>
              </div>
            ) : (
              <div>
                {unanswered.map((q, i) => (
                  <QuestionRow
                    key={i}
                    rank={i + 1}
                    content={q.content}
                    badge={q.occurrences}
                    badgeLabel={q.occurrences === 1 ? "time" : "times"}
                  />
                ))}
              </div>
            )}
            {unanswered.length > 0 && (
              <p className="mt-3 text-[11px] text-zinc-600">
                Upload documents to fill these knowledge gaps in the Documents page.
              </p>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
