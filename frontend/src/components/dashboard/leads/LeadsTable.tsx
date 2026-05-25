"use client";

import { useEffect, useState } from "react";
import { listLeads, updateLeadStatus } from "@/lib/api";
import { CLIENT_ID } from "@/lib/constants";
import type { LeadRecord, LeadStatus } from "@/types";
import { cn } from "@/utils/cn";

const STATUS_OPTIONS: LeadStatus[] = ["new", "contacted", "qualified", "closed"];

const STATUS_STYLES: Record<LeadStatus, string> = {
  new: "bg-blue-950/50 text-blue-400 border-blue-900",
  contacted: "bg-yellow-950/50 text-yellow-400 border-yellow-900",
  qualified: "bg-green-950/50 text-green-400 border-green-900",
  closed: "bg-zinc-800 text-zinc-500 border-zinc-700",
};

export default function LeadsTable() {
  const [leads, setLeads] = useState<LeadRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);

  useEffect(() => {
    listLeads(CLIENT_ID)
      .then(setLeads)
      .finally(() => setLoading(false));
  }, []);

  async function handleStatusChange(id: string, status: LeadStatus) {
    setUpdatingId(id);
    try {
      await updateLeadStatus(id, status, CLIENT_ID);
      setLeads((prev) => prev.map((l) => (l.id === id ? { ...l, status } : l)));
    } catch {
      // ignore — status reverts visually
    } finally {
      setUpdatingId(null);
    }
  }

  if (loading) {
    return <div className="py-20 text-center text-sm text-zinc-600">Loading leads…</div>;
  }

  if (leads.length === 0) {
    return (
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 py-20 text-center">
        <p className="text-sm text-zinc-600">No leads captured yet.</p>
        <p className="mt-1 text-xs text-zinc-700">Leads appear when users submit the chat form.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-900">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-zinc-800">
            {["Name", "Email", "Phone", "Status", "Date"].map((h) => (
              <th
                key={h}
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-zinc-500"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-zinc-800/60">
          {leads.map((lead) => (
            <tr key={lead.id} className="transition hover:bg-zinc-800/30">
              <td className="px-4 py-3 font-medium text-zinc-200">{lead.name}</td>
              <td className="px-4 py-3 text-zinc-400">{lead.email}</td>
              <td className="px-4 py-3 text-zinc-500">{lead.phone ?? "—"}</td>
              <td className="px-4 py-3">
                <select
                  value={lead.status ?? "new"}
                  disabled={updatingId === lead.id}
                  onChange={(e) => handleStatusChange(lead.id, e.target.value as LeadStatus)}
                  className={cn(
                    "rounded-full border px-2.5 py-0.5 text-xs font-medium focus:outline-none disabled:opacity-50",
                    STATUS_STYLES[lead.status ?? "new"]
                  )}
                >
                  {STATUS_OPTIONS.map((s) => (
                    <option key={s} value={s} className="bg-zinc-900 text-zinc-100">
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </option>
                  ))}
                </select>
              </td>
              <td className="px-4 py-3 text-zinc-500">
                {new Date(lead.created_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
