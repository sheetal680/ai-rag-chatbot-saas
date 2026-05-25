export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/**
 * Returns the current user's client_id from the persisted auth store.
 * Falls back to the NEXT_PUBLIC_CLIENT_ID env var (used by the embed widget
 * when no user is logged in). Never returns "default" — that was the shared
 * collection name that caused cross-user data leakage.
 */
export function getClientId(): string {
  if (typeof window === "undefined") return "";
  try {
    const raw = localStorage.getItem("auth_user");
    if (raw) {
      const user = JSON.parse(raw) as { client_id?: string };
      if (user?.client_id) return user.client_id;
    }
  } catch {
    // localStorage unavailable or corrupt — fall through
  }
  return process.env.NEXT_PUBLIC_CLIENT_ID ?? "";
}

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
