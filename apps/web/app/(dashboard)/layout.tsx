import Link from "next/link";

const NAV_ITEMS = [
  { href: "/arbol", label: "Árbol de Habilidades" },
  { href: "/examen", label: "Modo Examen" },
  { href: "/feedback", label: "Feedback" },
  { href: "/analitica", label: "Analítica" },
] as const;

export default function DashboardLayout({ children }: LayoutProps<"/">) {
  return (
    <div className="flex flex-1">
      <aside className="hidden w-56 shrink-0 border-r border-border p-4 sm:block">
        <nav className="flex flex-col gap-1">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="rounded-md px-3 py-2 text-sm text-muted transition-colors hover:bg-surface-hover hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </aside>
      <div className="flex-1 p-6">{children}</div>
    </div>
  );
}
