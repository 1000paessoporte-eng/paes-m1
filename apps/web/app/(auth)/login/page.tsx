"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { GoogleButton } from "@/components/auth/google-button";
import { ApiError, loginUser } from "@/lib/api";
import { setClientAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const { access_token, user } = await loginUser(email, password);
      setClientAuth(access_token, user);
      router.push("/examen");
      router.refresh();
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 401
          ? "Correo o contraseña incorrectos."
          : "No se pudo iniciar sesión. Verifica que la API esté disponible."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-1 items-center justify-center px-6 py-20">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-surface p-6 shadow-xl shadow-foreground/5">
        <span
          className="flex h-9 w-9 items-center justify-center rounded-lg text-xs font-bold text-white"
          style={{
            background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
          }}
        >
          m
        </span>
        <h1 className="mt-4 text-lg font-semibold">Inicia sesión en milpaes</h1>
        <p className="mt-1 text-sm text-muted">
          Continúa tus ensayos y tu progreso donde los dejaste.
        </p>

        <div className="mt-6 flex justify-center">
          <GoogleButton redirectTo="/examen" onError={setError} />
        </div>

        <div className="my-5 flex items-center gap-3 text-xs text-muted">
          <span className="h-px flex-1 bg-border" />
          o con tu correo
          <span className="h-px flex-1 bg-border" />
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
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
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
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
            {loading ? "Ingresando…" : "Continuar"}
          </button>
        </form>

        <p className="mt-4 text-center text-xs text-muted">
          ¿No tienes cuenta?{" "}
          <Link href="/registro" className="font-medium text-accent hover:underline">
            Crear cuenta
          </Link>
        </p>
      </div>
    </main>
  );
}
