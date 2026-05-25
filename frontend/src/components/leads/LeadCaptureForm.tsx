"use client";

import { FormEvent, useState } from "react";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import { api } from "@/lib/api";
import type { Lead } from "@/types";

interface Props {
  sessionId: string;
  onClose: () => void;
}

export default function LeadCaptureForm({ sessionId, onClose }: Props) {
  const [form, setForm] = useState<Lead>({ name: "", email: "" });
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await api.post("/leads/", { ...form, session_id: sessionId });
      setSubmitted(true);
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <div className="p-6 text-center">
        <p className="font-medium text-gray-900">Thanks! We&apos;ll be in touch.</p>
        <Button variant="ghost" size="sm" className="mt-4" onClick={onClose}>
          Continue chatting
        </Button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-6">
      <h3 className="text-base font-semibold text-gray-900">Leave your details</h3>
      <Input
        id="lead-name"
        label="Name"
        required
        value={form.name}
        onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
      />
      <Input
        id="lead-email"
        label="Email"
        type="email"
        required
        value={form.email}
        onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
      />
      <div className="flex gap-2">
        <Button type="submit" loading={loading} className="flex-1">
          Submit
        </Button>
        <Button type="button" variant="secondary" onClick={onClose}>
          Skip
        </Button>
      </div>
    </form>
  );
}
