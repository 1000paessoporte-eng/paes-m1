"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { ApiError, registerUser } from "@/lib/api";
import { setClientAuth } from "@/lib/auth";

export default function RegistroPage() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { access_token, user } = await registerUser(email, password, name);
      setClientAuth(access_token, user);
      router.push("/arbol");
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setError("Ese correo ya está registrado. Intenta iniciar sesión.");
      } else if (err instanceof ApiError && err.status === 422) {
        setError("Revisa el correo y usa una contraseña de al menos 8 caracteres.");
      } else {
        setError("No se pudo crear la cuenta. Verifica que la API esté disponible.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="bg-grid-fade relative flex flex-1 items-center justify-center overflow-hidden px-6 py-20">
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-1/3 -z-10 h-[320px] w-[560px] -translate-x-1/2 -translate-y-1/2 rounded-full opacity-25 blur-[100px]"
        style={{
          background:
            "radial-gradient(closest-side, var(--accent), var(--accent-2), transparent)",
        }}
      />

      <div className="w-full max-w-sm rounded-2xl border border-border bg-surface p-6 shadow-2xl shadow-black/20">
        <span
          className="flex h-9 w-9 items-center justify-center rounded-lg text-xs font-bold text-white"
          style={{
            background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
          }}
        >
          M1
        </span>
        <h1 className="mt-4 text-lg font-semibold">Crea tu cuenta</h1>
        <p className="mt-1 text-sm text-muted">
          Empieza a desbloquear el árbol de habilidades desde nivel 1.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3">
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
            <span className="text-xs font-medium text-muted">Contraseña</span>
            <input
              type="password"
              required
              minLength={8}
              autoComplete="new-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mínimo 8 caracteres"
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
            {loading ? "Creando cuenta…" : "Crear cuenta"}
          </button>
        </form>

        <p className="mt-4 text-center text-xs text-muted">
          ¿Ya tienes cuenta?{" "}
          <Link href="/login" className="font-medium text-accent hover:underline">
            Inicia sesión
          </Link>
        </p>
      </div>
    </main>
  );
}
