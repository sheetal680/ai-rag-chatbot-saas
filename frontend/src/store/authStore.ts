/**
 * Auth store — persists token to localStorage + a same-site cookie.
 *
 * Token storage strategy:
 *   - localStorage: read by the Axios interceptor on every API call
 *   - Plain JS cookie (auth_token): read by Next.js middleware for
 *     server-side route protection (redirects unauthenticated users)
 *
 * Security note: localStorage is readable by JS (not httpOnly).
 * Upgrade path → route /api/auth/* through Next.js API routes that
 * set httpOnly cookies, then remove localStorage usage entirely.
 */
import { create } from "zustand";
import type { AuthUser } from "@/types";

const TOKEN_KEY = "auth_token";
const USER_KEY = "auth_user";
const COOKIE_MAX_AGE = 60 * 60 * 24 * 7; // 7 days

interface AuthState {
  token: string | null;
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (token: string, user: AuthUser) => void;
  logout: () => void;
  hydrate: () => void;
}

function setCookie(name: string, value: string, maxAge: number) {
  document.cookie = `${name}=${value}; path=/; max-age=${maxAge}; SameSite=Lax`;
}

function deleteCookie(name: string) {
  document.cookie = `${name}=; path=/; max-age=0; SameSite=Lax`;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  isAuthenticated: false,

  login: (token, user) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    setCookie(TOKEN_KEY, token, COOKIE_MAX_AGE);
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    deleteCookie(TOKEN_KEY);
    set({ token: null, user: null, isAuthenticated: false });
  },

  hydrate: () => {
    const token = localStorage.getItem(TOKEN_KEY);
    const raw = localStorage.getItem(USER_KEY);
    if (token && raw) {
      try {
        const user: AuthUser = JSON.parse(raw);
        // Sync cookie in case it expired (e.g. user cleared cookies manually)
        setCookie(TOKEN_KEY, token, COOKIE_MAX_AGE);
        set({ token, user, isAuthenticated: true });
      } catch {
        localStorage.removeItem(TOKEN_KEY);
        localStorage.removeItem(USER_KEY);
      }
    }
  },
}));
