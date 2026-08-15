"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { cn } from "@paes-m1/utils";
import { GoogleButton } from "@/components/auth/google-button";
import { ApiError, loginUser, registerUser } from "@/lib/api";
import { setClientAuth } from "@/lib/auth";

/**
 * Panel único de entrada: iniciar sesión y crear cuenta en la misma pantalla,
 * con Google arriba de las dos. Antes eran dos páginas separadas y había que
 * saltar de una a otra perdiendo lo escrito.
 *
 * `/login` y `/registro` siguen existiendo como rutas (hay enlaces repartidos
 * por todo el sitio, el sitemap y los correos); cada una solo decide qué
 * pestaña abre. Cambiar de pestaña actualiza la URL con `replace` para que la
 * barra de direcciones y el botón de atrás no queden mintiendo.
 */

export type AuthTab = "login" | "registro";

/** A dónde ir tras entrar, si la pantalla anterior no pidió algo distinto. */
const DESTINO_POR_DEFECTO = "/panel";

/**
 * Solo se aceptan rutas internas. Un `next` con `http://` o `//` permitiría
 * mandar a alguien a un sitio ajeno desde un enlace de 1000paes.
 */
function destinoSeguro(next: string | null): string {
  if (!next || !next.startsWith("/") || next.startsWith("//")) {
    return DESTINO_POR_DEFECTO;
  }
  return next;
}

interface Props {
  initialTab: AuthTab;
}

export function AuthPanel({ initialTab }: Props) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const destino = destinoSeguro(searchParams.get("next"));

  const [tab, setTab] = useState<AuthTab>(initialTab);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const esRegistro = tab === "registro";

  function cambiarTab(siguiente: AuthTab) {
    if (siguiente === tab) return;
    setTab(siguiente);
    setError(null);
    setPassword("");
    const query = searchParams.toString();
    const ruta = siguiente === "login" ? "/login" : "/registro";
    router.replace(query ? `${ruta}?${query}` : ruta);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { access_token, user } = esRegistro
        ? await registerUser(email, password, name)
        : await loginUser(email, password);
      setClientAuth(access_token, user);
      router.push(destino);
      router.refresh();
    } catch (err) {
      setError(mensajeDeError(err, esRegistro));
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-1 items-center justify-center px-6 py-20">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-surface p-6 shadow-xl shadow-foreground/5">
        <span
          className="flex h-9 w-9 items-center justify-center rounded-lg text-xs font-bold text-accent-foreground"
          style={{
            background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
          }}
        >
          1K
        </span>
        <h1 className="mt-4 text-lg font-semibold">
          {esRegistro ? "Crea tu cuenta en 1000paes" : "Inicia sesión en 1000paes"}
        </h1>
        <p className="mt-1 text-sm text-muted">
          {esRegistro
            ? "Empieza a rendir ensayos y a seguir tu progreso."
            : "Continúa tus ensayos y tu progreso donde los dejaste."}
        </p>

        {/* ── Pestañas ─────────────────────────────────────────────────── */}
        <div
          role="tablist"
          aria-label="Entrar o crear cuenta"
          className="mt-5 grid grid-cols-2 gap-1 rounded-xl border border-border bg-background p-1"
        >
          {(["login", "registro"] as const).map((valor) => (
            <button
              key={valor}
              role="tab"
              type="button"
              aria-selected={tab === valor}
              onClick={() => cambiarTab(valor)}
              className={cn(
                "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                tab === valor
                  ? "bg-surface text-foreground shadow-sm"
                  : "text-muted hover:text-foreground"
              )}
            >
              {valor === "login" ? "Entrar" : "Crear cuenta"}
            </button>
          ))}
        </div>

        <div className="mt-5 flex justify-center">
          <GoogleButton redirectTo={destino} onError={setError} />
        </div>

        <div className="my-5 flex items-center gap-3 text-xs text-muted">
          <span className="h-px flex-1 bg-border" />
          o con tu correo
          <span className="h-px flex-1 bg-border" />
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          {esRegistro && (
            <label className="flex flex-col gap-1.5 text-left">
              <span className="text-xs font-medium text-muted">Nombre</span>
              <input
                type="text"
                required
                autoComplete="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Tu nombre"
                className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted/60"
              />
            </label>
          )}

          <label className="flex flex-col gap-1.5 text-left">
            <span className="text-xs font-medium text-muted">Correo</span>
            <input
              type="email"
              required
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tu@correo.com"
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted/60"
            />
          </label>

          <label className="flex flex-col gap-1.5 text-left">
            <span className="flex items-center justify-between text-xs font-medium text-muted">
              Contraseña
              {!esRegistro && (
                <Link
                  href="/olvide-contrasena"
                  className="font-medium text-accent hover:underline"
                >
                  ¿Olvidaste tu contraseña?
                </Link>
              )}
            </span>
            <input
              type="password"
              required
              minLength={esRegistro ? 8 : undefined}
              autoComplete={esRegistro ? "new-password" : "current-password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={esRegistro ? "Mínimo 8 caracteres" : "••••••••"}
              className="rounded-lg border border-border bg-background px-3 py-2 text-sm text-foreground placeholder:text-muted/60"
            />
          </label>

          {error && (
            <p className="rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-xs text-danger">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-glow mt-2 rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading
              ? esRegistro
                ? "Creando cuenta…"
                : "Ingresando…"
              : esRegistro
                ? "Crear cuenta"
                : "Continuar"}
          </button>
        </form>

        {esRegistro && (
          <p className="mt-3 text-center text-[11px] leading-relaxed text-muted">
            Al crear una cuenta aceptas los{" "}
            <Link href="/terminos" className="text-accent hover:underline">
              Términos
            </Link>{" "}
            y la{" "}
            <Link href="/privacidad" className="text-accent hover:underline">
              Política de Privacidad
            </Link>
            .
          </p>
        )}
      </div>
    </main>
  );
}

function mensajeDeError(err: unknown, esRegistro: boolean): string {
  if (err instanceof ApiError) {
    if (!esRegistro && err.status === 401) return "Correo o contraseña incorrectos.";
    if (esRegistro && err.status === 409) {
      return "Ese correo ya está registrado. Entra con tu contraseña.";
    }
    if (esRegistro && err.status === 422) {
      return "Revisa el correo y usa una contraseña de al menos 8 caracteres.";
    }
  }
  return esRegistro
    ? "No se pudo crear la cuenta. Verifica que la API esté disponible."
    : "No se pudo iniciar sesión. Verifica que la API esté disponible.";
}
