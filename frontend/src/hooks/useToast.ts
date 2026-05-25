import { useToastStore } from "@/store/toastStore";

export function useToast() {
  const add = useToastStore((s) => s.add);
  return {
    success: (message: string) => add(message, "success"),
    error:   (message: string) => add(message, "error"),
    info:    (message: string) => add(message, "info"),
  };
}
