"use client";

import { useEffect, useState } from "react";
import { Menu, Zap } from "lucide-react";
import DashboardSidebar from "./DashboardSidebar";

export default function DashboardShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Open sidebar by default on desktop after mount (avoids SSR mismatch)
  useEffect(() => {
    if (window.innerWidth >= 768) setSidebarOpen(true);
  }, []);

  return (
    <div className="flex h-screen bg-zinc-950 text-zinc-100 overflow-hidden">
      {/* Mobile backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/60 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar — fixed overlay on mobile, static on desktop */}
      <div
        className={[
          "fixed inset-y-0 left-0 z-40 transition-transform duration-200",
          "md:relative md:z-auto md:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        ].join(" ")}
      >
        <DashboardSidebar onClose={() => setSidebarOpen(false)} />
      </div>

      {/* Main column */}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        {/* Mobile top bar — hidden on md+ */}
        <div className="flex items-center gap-3 border-b border-zinc-800 bg-zinc-900/95 px-4 py-3 md:hidden">
          <button
            onClick={() => setSidebarOpen(true)}
            aria-label="Open navigation"
            className="rounded-lg p-1.5 text-zinc-400 transition hover:bg-zinc-800 hover:text-zinc-100"
          >
            <Menu size={20} />
          </button>
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-blue-600">
              <Zap size={11} className="text-white" />
            </div>
            <span className="text-sm font-semibold text-zinc-100">RAG Admin</span>
          </div>
        </div>

        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}
