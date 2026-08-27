"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { cn } from "@paes-m1/utils";
import { clearClientAuth, getClientUser, onClientAuthChange, type AuthUser } from "@/lib/auth";
import { TemaToggle } from "@/components/tema-toggle";
import { Logotipo } from "@/components/ui/marca";

// Menú de la aplicación: solo tiene sentido con la sesión iniciada, porque
// todas estas rutas exigen autenticación.
const NAV_ITEMS = [
  { href: "/panel", label: "Inicio" },
  { href: "/arbol", label: "Árbol" },
  { href: "/examen", label: "Ensayos" },
  { href: "/meta", label: "Mi meta" },
  { href: "/historial", label: "Progreso" },
  { href: "/analitica", label: "Analítica" },
] as const;

// Menú de la portada pública: a quien todavía no tiene cuenta se le ofrecen
// las páginas que puede abrir, no las de la aplicación que lo rebotarían al
// login.
const NAV_PUBLICO = [
  { href: "/", label: "Inicio" },
  // El catálogo va segundo a propósito: son 1.855 fichas con las ponderaciones
  // oficiales del DEMRE, y hasta ahora solo se llegaba a ellas por el sitemap.
  // Sin un enlace desde el menú no las encontraba ni Google ni una persona.
  { href: "/carreras", label: "Carreras" },
  { href: "/simulador", label: "Simulador" },
  // Las lecciones del temario: el otro contenido que se lee sin cuenta.
  // Son una por nodo del árbol, en las cinco pruebas.
  { href: "/aprender", label: "Lecciones" },
  { href: "/demo", label: "Probar sin cuenta" },
  { href: "/preguntas-frecuentes", label: "Preguntas frecuentes" },
  { href: "/sobre-nosotros", label: "Sobre nosotros" },
] as const;

export function SiteHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);

  const items = user ? NAV_ITEMS : NAV_PUBLICO;

  // "Mi curso" solo aparece si la persona pertenece a uno. Es una sección que
  // casi nadie tiene, y enlazarla para todo el mundo llenaría la barra con
  // algo que la mayoría abriría una vez para encontrar un formulario que no le
  // sirve. Quien tiene un código lo escribe en /colegio, que sigue existiendo.
  const conCurso = user?.tiene_colegio
    ? [...items, { href: "/colegio", label: "Mi curso" } as const]
    : items;

  // El panel de admin solo se enlaza para admins. Ocultarlo es comodidad, no
  // seguridad: /api/admin exige el rol en cada llamada.
  const navItems = user?.is_admin
    ? [...conCurso, { href: "/admin", label: "Admin" } as const]
    : conCurso;

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
    <header className="glass sticky top-0 z-50">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href={user ? "/panel" : "/"} className="flex items-center">
          <Logotipo className="text-base font-bold text-foreground" tamanoPx={16} />
        </Link>

        <nav className="hidden items-center gap-1 lg:flex">
          {navItems.map((item) => {
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

        <div className="hidden items-center gap-3 lg:flex">
          <TemaToggle />
          {user ? (
            <>
              <Link href="/perfil" className="text-sm text-muted hover:text-foreground">
                Hola, <span className="text-foreground">{user.name.split(" ")[0]}</span>
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

        <div className="flex items-center gap-2 lg:hidden">
          {/* La única puerta sin fricción del producto, fuera del menú.
              Hasta acá "Probar sin cuenta" solo existía dentro del desplegable:
              en un celular había que tocar las tres rayitas para descubrir que
              se podía probar sin registrarse. De 71 personas que vieron la
              portada en diez días, 4 llegaron al demo. No se le pide nada a
              nadie para entrar ahí, así que no tiene por qué estar escondido.

              Solo para visitantes: quien ya tiene cuenta rinde ensayos de
              verdad y no necesita la muestra de cinco preguntas. */}
          {!user && (
            <Link
              href="/demo"
              className="btn-glow rounded-lg px-3 py-1.5 text-sm font-semibold text-accent-foreground"
            >
              Probar gratis
            </Link>
          )}

          <button
            type="button"
            aria-label="Abrir menú"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
            className="flex h-9 w-9 items-center justify-center rounded-md text-foreground hover:bg-surface-hover"
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
      </div>

      {open && (
        <nav className="flex flex-col gap-1 border-t border-border px-4 py-3 lg:hidden">
          {navItems.map((item) => {
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
          <div className="mt-2 flex items-center justify-between border-t border-border px-3 pt-3">
            <span className="text-sm text-muted">Tema</span>
            <TemaToggle />
          </div>
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
