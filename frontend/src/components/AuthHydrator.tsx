"use client";

import { useEffect } from "react";
import { useAuthStore } from "@/store/authStore";

/**
 * Renders nothing — mounts once and hydrates the auth store from localStorage.
 * Must be a client component placed in the root layout.
 */
export default function AuthHydrator() {
  useEffect(() => {
    useAuthStore.getState().hydrate();
  }, []);

  return null;
}
