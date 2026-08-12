import type { ReactNode } from "react";

interface StatTileProps {
  label: string;
  value: string;
  icon: ReactNode;
}

export function StatTile({ label, value, icon }: StatTileProps) {
  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      <div className="flex items-center gap-2 text-muted">
        {icon}
        <span className="text-xs">{label}</span>
      </div>
      <p className="mt-2 text-3xl font-semibold tracking-tight text-foreground">
        {value}
      </p>
    </div>
  );
}
