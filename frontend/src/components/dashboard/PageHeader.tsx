interface Props {
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export default function PageHeader({ title, description, action }: Props) {
  return (
    <div className="flex items-start justify-between border-b border-zinc-800 px-4 py-4 sm:px-8 sm:py-6">
      <div>
        <h1 className="text-xl font-semibold text-zinc-100">{title}</h1>
        {description && <p className="mt-0.5 text-sm text-zinc-500">{description}</p>}
      </div>
      {action && <div>{action}</div>}
    </div>
  );
}
