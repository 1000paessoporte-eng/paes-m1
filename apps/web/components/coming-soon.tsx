import type { ReactNode } from "react";

interface ComingSoonProps {
  title: string;
  description: string;
  icon: ReactNode;
}

export function ComingSoon({ title, description, icon }: ComingSoonProps) {
  return (
    <div className="flex flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10 text-accent">
        {icon}
      </div>
      <span className="mt-5 rounded-full border border-border bg-background px-2.5 py-0.5 text-[11px] font-medium text-muted">
        Próximamente
      </span>
      <h1 className="mt-3 text-xl font-semibold">{title}</h1>
      <p className="mt-2 max-w-md text-sm text-muted">{description}</p>
    </div>
  );
}
