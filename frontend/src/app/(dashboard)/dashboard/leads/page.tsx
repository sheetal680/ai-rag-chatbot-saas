import PageHeader from "@/components/dashboard/PageHeader";
import LeadsTable from "@/components/dashboard/leads/LeadsTable";

export const metadata = { title: "Leads — Admin" };

export default function LeadsPage() {
  return (
    <div>
      <PageHeader
        title="Leads"
        description="Contacts captured through the chatbot lead form."
      />
      <div className="p-4 sm:p-8">
        <LeadsTable />
      </div>
    </div>
  );
}
