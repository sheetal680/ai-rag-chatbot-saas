"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { loginUser, registerUser } from "@/lib/api";

export function useAuth() {
  const router = useRouter();
  const { token, user, isAuthenticated, login, logout } = useAuthStore();

  async function signIn(email: string, password: string) {
    const res = await loginUser(email, password);
    login(res.access_token, res.user);
    router.push("/dashboard");
  }

  async function signUp(name: string, email: string, password: string) {
    const res = await registerUser(name, email, password);
    login(res.access_token, res.user);
    router.push("/dashboard");
  }

  function signOut() {
    logout();
    router.push("/login");
  }

  return { token, user, isAuthenticated, signIn, signUp, signOut };
}
