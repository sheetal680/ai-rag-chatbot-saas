"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BarChart2,
  FileText,
  LayoutDashboard,
  LogOut,
  MessageSquare,
  Settings,
  Users,
  Zap,
} from "lucide-react";
import { cn } from "@/utils/cn";
import { useAuth } from "@/hooks/useAuth";

const NAV = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard, exact: true },
  { href: "/dashboard/analytics", label: "Analytics", icon: BarChart2 },
  { href: "/dashboard/documents", label: "Documents", icon: FileText },
  { href: "/dashboard/leads", label: "Leads", icon: Users },
  { href: "/dashboard/conversations", label: "Conversations", icon: MessageSquare },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export default function DashboardSidebar() {
  const pathname = usePathname();
  const { user, signOut } = useAuth();

  function isActive(href: string, exact?: boolean) {
    return exact ? pathname === href : pathname.startsWith(href);
  }

  return (
    <aside className="flex w-56 shrink-0 flex-col border-r border-zinc-800 bg-zinc-900">
      {/* Brand */}
      <div className="flex items-center gap-2.5 border-b border-zinc-800 px-5 py-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600">
          <Zap size={14} className="text-white" />
        </div>
        <span className="text-sm font-semibold text-zinc-100">RAG Admin</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 px-3 py-4">
        {NAV.map(({ href, label, icon: Icon, exact }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition",
              isActive(href, exact)
                ? "bg-zinc-800 text-zinc-100 font-medium"
                : "text-zinc-400 hover:bg-zinc-800/60 hover:text-zinc-200"
            )}
          >
            <Icon size={16} />
            {label}
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-zinc-800 px-4 py-3 space-y-1">
        <Link
          href="/chat/new"
          className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-xs text-zinc-500 transition hover:bg-zinc-800/60 hover:text-zinc-300"
        >
          <MessageSquare size={13} />
          Open chatbot
        </Link>

        {user && (
          <div className="mt-1 rounded-lg border border-zinc-800 bg-zinc-950/50 px-3 py-2">
            <p className="truncate text-xs font-medium text-zinc-300">{user.name}</p>
            <p className="truncate text-[10px] text-zinc-600">{user.email}</p>
          </div>
        )}

        <button
          onClick={signOut}
          className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-xs text-zinc-600 transition hover:bg-zinc-800/60 hover:text-red-400"
        >
          <LogOut size={13} />
          Sign out
        </button>
      </div>
    </aside>
  );
}
