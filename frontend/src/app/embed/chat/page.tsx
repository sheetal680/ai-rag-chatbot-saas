import { Suspense } from "react";
import WidgetChatInner from "@/components/widget/WidgetChatInner";

export const metadata = { title: "Chat" };

export default function EmbedChatPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-screen items-center justify-center bg-zinc-950">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
        </div>
      }
    >
      <WidgetChatInner />
    </Suspense>
  );
}
