import Card from "@/components/ui/Card";

interface Props {
  label: string;
  value: number | string;
  subtext?: string;
}

export default function StatCard({ label, value, subtext }: Props) {
  return (
    <Card>
      <p className="text-xs font-medium uppercase tracking-wide text-gray-500">{label}</p>
      <p className="mt-1 text-3xl font-bold text-gray-900">{value}</p>
      {subtext ? <p className="mt-1 text-xs text-gray-400">{subtext}</p> : null}
    </Card>
  );
}
