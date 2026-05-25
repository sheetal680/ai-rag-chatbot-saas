export const CLIENT_ID = process.env.NEXT_PUBLIC_CLIENT_ID ?? "default";
export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const CHAT_ROUTES = {
  new: "/chat/new",
  session: (id: string) => `/chat/${id}`,
} as const;

export const DASHBOARD_ROUTES = {
  overview: "/dashboard",
  analytics: "/dashboard/analytics",
  documents: "/dashboard/documents",
  leads: "/dashboard/leads",
  conversations: "/dashboard/conversations",
  settings: "/dashboard/settings",
} as const;
