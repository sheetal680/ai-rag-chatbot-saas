"use client";

interface Props {
  companyName: string;
  primaryColor: string;
  onClose: () => void;
}

export default function WidgetHeader({ companyName, primaryColor, onClose }: Props) {
  return (
    <div className="flex shrink-0 items-center gap-3 border-b border-zinc-800 bg-zinc-900 px-4 py-3">
      <div
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
        style={{ background: primaryColor }}
      >
        {companyName.charAt(0).toUpperCase()}
      </div>

      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-semibold text-zinc-100">{companyName}</p>
        <p className="flex items-center gap-1.5 text-xs text-zinc-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
          Online
        </p>
      </div>

      <button
        onClick={onClose}
        aria-label="Close chat"
        className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg text-zinc-500 transition-colors hover:bg-zinc-800 hover:text-zinc-100"
      >
        <svg
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </div>
  );
}
