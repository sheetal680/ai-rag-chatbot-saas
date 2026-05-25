import { cn } from "@/utils/cn";

interface Props {
  className?: string;
}

export default function Skeleton({ className }: Props) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-lg bg-zinc-800/70",
        className
      )}
    />
  );
}
