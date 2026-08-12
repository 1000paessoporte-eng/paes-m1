"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@paes-m1/utils";
import { clearClientAuth, getClientUser, onClientAuthChange, type AuthUser } from "@/lib/auth";

const NAV_ITEMS = [
  { href: "/", label: "Inicio" },
  { href: "/arbol", label: "Árbol de Habilidades" },
  { href: "/examen", label: "Modo Ensayo" },
  { href: "/historial", label: "Mi progreso" },
  { href: "/analitica", label: "Analítica" },
] as const;

export function SiteHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    // Lectura de cookie (estado externo al DOM) tras montar: evita mismatch
    // de hidratación, ya que el SSR no tiene acceso a document.cookie.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setUser(getClientUser());
  }, [pathname]);

  useEffect(() => {
    // Re-lee la cookie ante login/logout/cambio de nombre disparado desde
    // otro componente en la MISMA página (sin esto, el header queda
    // desactualizado hasta el próximo cambio de ruta).
    return onClientAuthChange(() => setUser(getClientUser()));
  }, []);

  function handleLogout() {
    clearClientAuth();
    setUser(null);
    setOpen(false);
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2">
          <span
            className="flex h-7 w-7 items-center justify-center rounded-md text-xs font-bold text-white"
            style={{
              background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
            }}
          >
            m
          </span>
          <span className="text-sm font-semibold tracking-tight">milpaes</span>
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {NAV_ITEMS.map((item) => {
            const active =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "rounded-md px-3 py-1.5 text-sm transition-colors",
                  active
                    ? "bg-accent/10 text-foreground"
                    : "text-muted hover:bg-surface-hover hover:text-foreground"
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {user ? (
            <>
              <Link href="/perfil" className="text-sm text-muted hover:text-foreground">
                Hola, <span className="text-foreground">{user.name}</span>
              </Link>
              <button
                onClick={handleLogout}
                className="rounded-lg border border-border px-3 py-1.5 text-sm font-medium transition-colors hover:bg-surface-hover"
              >
                Cerrar sesión
              </button>
            </>
          ) : (
            <Link
              href="/login"
              className="rounded-lg border border-border px-3 py-1.5 text-sm font-medium transition-colors hover:bg-surface-hover"
            >
              Iniciar sesión
            </Link>
          )}
        </div>

        <button
          type="button"
          aria-label="Abrir menú"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
          className="flex h-9 w-9 items-center justify-center rounded-md text-foreground hover:bg-surface-hover md:hidden"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          >
            {open ? (
              <path d="M6 6l12 12M18 6L6 18" />
            ) : (
              <path d="M4 7h16M4 12h16M4 17h16" />
            )}
          </svg>
        </button>
      </div>

      {open && (
        <nav className="flex flex-col gap-1 border-t border-border px-4 py-3 md:hidden">
          {NAV_ITEMS.map((item) => {
            const active =
              item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className={cn(
                  "rounded-md px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-surface-hover text-foreground"
                    : "text-muted hover:bg-surface-hover hover:text-foreground"
                )}
              >
                {item.label}
              </Link>
            );
          })}
          {user ? (
            <button
              onClick={handleLogout}
              className="mt-1 rounded-md border border-border px-3 py-2 text-left text-sm font-medium hover:bg-surface-hover"
            >
              Cerrar sesión ({user.name})
            </button>
          ) : (
            <Link
              href="/login"
              onClick={() => setOpen(false)}
              className="mt-1 rounded-md border border-border px-3 py-2 text-sm font-medium hover:bg-surface-hover"
            >
              Iniciar sesión
            </Link>
          )}
        </nav>
      )}
    </header>
  );
}
