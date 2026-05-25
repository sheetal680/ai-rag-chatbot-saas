import { api } from "@/lib/api";
import { getClientId } from "@/lib/constants";

export interface Document {
  doc_id: string;
  filename: string;
  chunk_count: number;
  created_at: string;
}

export async function uploadDocument(file: File): Promise<{ doc_id: string; chunk_count: number }> {
  const form = new FormData();
  form.append("file", file);
  form.append("client_id", getClientId());
  const { data } = await api.post("/documents/upload-pdf", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function listDocuments(): Promise<Document[]> {
  const { data } = await api.get<Document[]>(`/documents/?client_id=${getClientId()}`);
  return data;
}

export async function deleteDocument(docId: string): Promise<void> {
  await api.delete(`/documents/${docId}`);
}
