import PageHeader from "@/components/dashboard/PageHeader";
import DocumentsPanel from "@/components/dashboard/documents/DocumentsPanel";

export const metadata = { title: "Documents — Admin" };

export default function DocumentsPage() {
  return (
    <div>
      <PageHeader
        title="Documents"
        description="Manage the knowledge base. Uploaded files are chunked, embedded, and indexed for RAG retrieval."
      />
      <DocumentsPanel />
    </div>
  );
}
