"use client";

import { ChangeEvent, useEffect, useRef, useState } from "react";
import {
  Trash2,
  Upload,
  Link as LinkIcon,
  FileText,
  Globe,
  CheckCircle,
  Loader2,
} from "lucide-react";
import { deleteDocument, ingestUrl, listDocuments, uploadDocument } from "@/lib/api";
import { getClientId } from "@/lib/constants";
import DataTable, { type Column } from "@/components/dashboard/DataTable";
import type { Document } from "@/types";
import { cn } from "@/utils/cn";
import { useToast } from "@/hooks/useToast";

type Tab = "upload" | "url";
type UploadStep = "idle" | "uploading" | "processing" | "indexing" | "done";

const STEP_LABELS: Record<UploadStep, string> = {
  idle: "Upload & Index",
  uploading: "Uploading…",
  processing: "Processing…",
  indexing: "Indexing…",
  done: "Done!",
};

const INGEST_STEP_LABELS: Record<UploadStep, string> = {
  idle: "Ingest URL",
  uploading: "Fetching…",
  processing: "Processing…",
  indexing: "Indexing…",
  done: "Done!",
};

export default function DocumentsPanel() {
  const toast = useToast();
  const [docs, setDocs] = useState<Document[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [tab, setTab] = useState<Tab>("upload");

  // file upload
  const [file, setFile] = useState<File | null>(null);
  const [uploadStep, setUploadStep] = useState<UploadStep>("idle");
  const [uploadChunks, setUploadChunks] = useState(0);
  const uploadTimers = useRef<ReturnType<typeof setTimeout>[]>([]);

  // URL ingest
  const [url, setUrl] = useState("");
  const [ingestStep, setIngestStep] = useState<UploadStep>("idle");
  const [ingestChunks, setIngestChunks] = useState(0);
  const ingestTimers = useRef<ReturnType<typeof setTimeout>[]>([]);

  // deleting
  const [deletingId, setDeletingId] = useState<string | null>(null);

  function clearTimers(timers: ReturnType<typeof setTimeout>[]) {
    timers.forEach(clearTimeout);
    timers.length = 0;
  }

  async function fetchDocs() {
    try {
      const data = await listDocuments(getClientId());
      setDocs(data);
    } catch {
      // ignore — table stays empty
    } finally {
      setLoadingDocs(false);
    }
  }

  useEffect(() => {
    fetchDocs();
  }, []);

  async function handleFileUpload() {
    if (!file) return;

    clearTimers(uploadTimers.current);
    setUploadStep("uploading");

    // Simulate step progression while the real request is in-flight
    uploadTimers.current.push(setTimeout(() => setUploadStep("processing"), 1400));
    uploadTimers.current.push(setTimeout(() => setUploadStep("indexing"), 2800));

    try {
      const res = await uploadDocument(file, getClientId());
      clearTimers(uploadTimers.current);
      setUploadStep("done");
      setUploadChunks(res.chunk_count);
      setFile(null);
      await fetchDocs();
      uploadTimers.current.push(
        setTimeout(() => setUploadStep("idle"), 3000)
      );
    } catch {
      clearTimers(uploadTimers.current);
      setUploadStep("idle");
      toast.error("Upload failed. Please check the file and try again.");
    }
  }

  async function handleUrlIngest() {
    if (!url.trim()) return;

    clearTimers(ingestTimers.current);
    setIngestStep("uploading");

    ingestTimers.current.push(setTimeout(() => setIngestStep("processing"), 1400));
    ingestTimers.current.push(setTimeout(() => setIngestStep("indexing"), 2800));

    try {
      const res = await ingestUrl(url.trim(), getClientId());
      clearTimers(ingestTimers.current);
      setIngestStep("done");
      setIngestChunks(res.chunk_count);
      setUrl("");
      await fetchDocs();
      ingestTimers.current.push(
        setTimeout(() => setIngestStep("idle"), 3000)
      );
    } catch {
      clearTimers(ingestTimers.current);
      setIngestStep("idle");
      toast.error("Ingestion failed. Check the URL is accessible and try again.");
    }
  }

  async function handleDelete(docId: string) {
    setDeletingId(docId);
    try {
      await deleteDocument(docId, getClientId());
      setDocs((prev) => prev.filter((d) => d.doc_id !== docId));
      toast.success("Document removed from knowledge base.");
    } catch {
      toast.error("Delete failed. Please try again.");
    } finally {
      setDeletingId(null);
    }
  }

  const columns: Column<Document>[] = [
    {
      key: "filename",
      header: "Document",
      render: (doc: Document) => (
        <div className="flex items-center gap-2">
          {doc.type === "url" ? (
            <Globe size={14} className="text-zinc-500" />
          ) : (
            <FileText size={14} className="text-zinc-500" />
          )}
          <span className="truncate max-w-xs">
            {doc.filename ?? doc.source_url ?? "—"}
          </span>
        </div>
      ),
    },
    {
      key: "type",
      header: "Type",
      render: (doc: Document) => (
        <span className="uppercase text-xs text-zinc-500">{doc.type}</span>
      ),
    },
    {
      key: "chunk_count",
      header: "Chunks",
      render: (doc: Document) => String(doc.chunk_count),
    },
    {
      key: "created_at",
      header: "Added",
      render: (doc: Document) =>
        new Date(doc.created_at).toLocaleDateString("en-US", {
          month: "short",
          day: "numeric",
          year: "numeric",
        }),
    },
    {
      key: "actions",
      header: "",
      className: "w-10",
      render: (doc: Document) => (
        <button
          onClick={() => handleDelete(doc.doc_id)}
          disabled={deletingId === doc.doc_id}
          className="rounded-lg p-1.5 text-zinc-600 transition hover:bg-red-950/40 hover:text-red-400 disabled:opacity-40"
        >
          <Trash2 size={14} />
        </button>
      ),
    },
  ];

  const isUploading = uploadStep !== "idle";
  const isIngesting = ingestStep !== "idle";

  return (
    <div className="space-y-6 px-8 py-6">
      {/* Upload card */}
      <div className="rounded-xl border border-zinc-800 bg-zinc-900 p-5">
        {/* Tabs */}
        <div className="mb-4 flex gap-1 rounded-lg border border-zinc-800 bg-zinc-950 p-1 w-fit">
          {(["upload", "url"] as Tab[]).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={cn(
                "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-xs font-medium transition",
                tab === t
                  ? "bg-zinc-800 text-zinc-100"
                  : "text-zinc-500 hover:text-zinc-300"
              )}
            >
              {t === "upload" ? <Upload size={12} /> : <LinkIcon size={12} />}
              {t === "upload" ? "Upload file" : "Ingest URL"}
            </button>
          ))}
        </div>

        {tab === "upload" ? (
          <div className="space-y-3">
            <input
              type="file"
              accept=".pdf,.docx,.txt,.md"
              disabled={isUploading}
              onChange={(e: ChangeEvent<HTMLInputElement>) =>
                setFile(e.target.files?.[0] ?? null)
              }
              className="block w-full text-sm text-zinc-400 file:mr-3 file:rounded-lg file:border-0 file:bg-zinc-800 file:px-3 file:py-1.5 file:text-xs file:font-medium file:text-zinc-300 hover:file:bg-zinc-700 disabled:opacity-50"
            />
            {file && !isUploading && (
              <p className="text-xs text-zinc-500">Selected: {file.name}</p>
            )}

            {/* Progress steps */}
            {isUploading && (
              <ProgressSteps step={uploadStep} chunkCount={uploadChunks} />
            )}

            <button
              onClick={handleFileUpload}
              disabled={!file || isUploading}
              className={cn(
                "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-60",
                uploadStep === "done"
                  ? "bg-emerald-600 hover:bg-emerald-500"
                  : "bg-blue-600 hover:bg-blue-500"
              )}
            >
              {uploadStep === "idle" && <Upload size={14} />}
              {uploadStep === "done" && <CheckCircle size={14} />}
              {isUploading && uploadStep !== "done" && (
                <Loader2 size={14} className="animate-spin" />
              )}
              {uploadStep === "done"
                ? `Done! ${uploadChunks} chunk${uploadChunks !== 1 ? "s" : ""} indexed`
                : STEP_LABELS[uploadStep]}
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            <input
              type="url"
              value={url}
              disabled={isIngesting}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/page"
              className="w-full rounded-lg border border-zinc-700 bg-zinc-800 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-600 focus:border-zinc-500 focus:outline-none disabled:opacity-50"
            />

            {/* Progress steps */}
            {isIngesting && (
              <ProgressSteps step={ingestStep} chunkCount={ingestChunks} />
            )}

            <button
              onClick={handleUrlIngest}
              disabled={!url.trim() || isIngesting}
              className={cn(
                "flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium text-white transition disabled:cursor-not-allowed disabled:opacity-60",
                ingestStep === "done"
                  ? "bg-emerald-600 hover:bg-emerald-500"
                  : "bg-blue-600 hover:bg-blue-500"
              )}
            >
              {ingestStep === "idle" && <Globe size={14} />}
              {ingestStep === "done" && <CheckCircle size={14} />}
              {isIngesting && ingestStep !== "done" && (
                <Loader2 size={14} className="animate-spin" />
              )}
              {ingestStep === "done"
                ? `Done! ${ingestChunks} chunk${ingestChunks !== 1 ? "s" : ""} indexed`
                : INGEST_STEP_LABELS[ingestStep]}
            </button>
          </div>
        )}
      </div>

      {/* Documents table */}
      <div>
        <h2 className="mb-3 text-sm font-medium text-zinc-400">
          Knowledge base ({loadingDocs ? "…" : docs.length} documents)
        </h2>
        <DataTable
          columns={columns}
          data={docs}
          keyField="doc_id"
          emptyMessage="No documents ingested yet. Upload a file or ingest a URL above."
        />
      </div>
    </div>
  );
}

// ─── Progress steps indicator ─────────────────────────────────────────────────

const STEPS: { key: UploadStep; label: string }[] = [
  { key: "uploading", label: "Uploading" },
  { key: "processing", label: "Processing" },
  { key: "indexing", label: "Indexing" },
  { key: "done", label: "Done" },
];

function ProgressSteps({
  step,
  chunkCount,
}: {
  step: UploadStep;
  chunkCount: number;
}) {
  const isDone = step === "done";
  const currentIdx = isDone ? STEPS.length : STEPS.findIndex((s) => s.key === step);

  return (
    <div className="flex items-center gap-1">
      {STEPS.map((s, i) => {
        const completed = i < currentIdx;
        const active = !isDone && s.key === step;

        return (
          <div key={s.key} className="flex items-center gap-1">
            <div
              className={cn(
                "flex h-5 w-5 items-center justify-center rounded-full text-[9px] font-bold transition-colors",
                completed
                  ? "bg-emerald-600 text-white"
                  : active
                  ? "bg-blue-600 text-white"
                  : "bg-zinc-800 text-zinc-600"
              )}
            >
              {completed ? (
                <CheckCircle size={11} />
              ) : active ? (
                <Loader2 size={10} className="animate-spin" />
              ) : (
                String(i + 1)
              )}
            </div>
            <span
              className={cn(
                "text-[10px] transition-colors",
                completed ? "text-emerald-500" : active ? "text-zinc-200" : "text-zinc-600"
              )}
            >
              {isDone && s.key === "done" ? `${chunkCount} chunks` : s.label}
            </span>
            {i < STEPS.length - 1 && (
              <span className="mx-1 text-zinc-700 text-[10px]">›</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
