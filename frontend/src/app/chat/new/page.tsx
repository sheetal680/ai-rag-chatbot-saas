"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { randomId } from "@/utils/format";

export default function NewChatPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace(`/chat/${randomId()}`);
  }, [router]);

  return null;
}
