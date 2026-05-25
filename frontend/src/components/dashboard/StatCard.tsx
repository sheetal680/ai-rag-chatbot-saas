import { type LucideIcon } from "lucide-react";
import { cn } from "@/utils/cn";

interface Props {
  label: string;
  value: number | string;
  subtext?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
}

export default function StatCard({ label, value, subtext, icon: Icon }: Props) {
  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
      <div className="flex items-start justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-zinc-500">{label}</p>
        {Icon && (
          <div className="rounded-lg bg-zinc-800 p-1.5">
            <Icon size={14} className="text-zinc-400" />
          </div>
        )}
      </div>
      <p className={cn("mt-2 font-bold text-zinc-100", typeof value === "number" ? "text-3xl" : "text-2xl")}>
        {value}
      </p>
      {subtext && <p className="mt-1 text-xs text-zinc-600">{subtext}</p>}
    </div>
  );
}
