"use client";

import { ChangeEvent, useState } from "react";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { uploadPdf } from "@/lib/api";
import { CLIENT_ID } from "@/lib/constants";

interface UploadResult {
  doc_id: string;
  chunk_count: number;
}

export default function DocumentUpload() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState("");

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      setResult(null);
      setError("");
    }
  }

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    setError("");
    try {
      const data = await uploadPdf(file, CLIENT_ID);
      setResult(data);
      setFile(null);
    } catch {
      setError("Upload failed. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card>
      <h2 className="mb-4 text-base font-semibold text-gray-900">Upload PDF</h2>
      <input
        type="file"
        accept=".pdf"
        onChange={handleFileChange}
        className="block w-full text-sm text-gray-500 file:mr-4 file:rounded file:border-0 file:bg-brand-50 file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-brand-600"
      />
      {file ? (
        <p className="mt-2 text-xs text-gray-500">Selected: {file.name}</p>
      ) : null}
      {error ? <p className="mt-2 text-xs text-red-600">{error}</p> : null}
      {result ? (
        <p className="mt-2 text-xs text-green-600">
          Uploaded — {result.chunk_count} chunks indexed (ID: {result.doc_id})
        </p>
      ) : null}
      <Button
        onClick={handleUpload}
        loading={loading}
        disabled={!file}
        className="mt-4"
      >
        Upload & Index
      </Button>
    </Card>
  );
}
