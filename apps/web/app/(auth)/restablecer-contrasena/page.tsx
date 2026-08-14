"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { ApiError, resetPassword } from "@/lib/api";


function ResetForm() {
  const token = useSearchParams().get("token") ?? "";
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await resetPassword(token, password);
      setDone(true);
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 400
          ? "El enlace no es válido o ya expiró. Pide uno nuevo."
          : "No se pudo actualizar la contraseña. Verifica que la API esté disponible."
      );
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <p className="mt-6 rounded-lg border border-danger/40 bg-danger/10 px-3 py-3 text-sm text-danger">
        Este link no trae el código de recuperación. Pide uno nuevo desde{" "}
        <Link href="/olvide-contrasena" className="font-medium underline">
          recuperar contraseña
        </Link>
        .
      </p>
    );
  }

  if (done) {
    return (
      <div className="mt-6">
        <p className="rounded-lg border border-success/40 bg-success/10 px-3 py-3 text-sm text-success">
          Tu contraseña se actualizó. Ya puedes iniciar sesión con la nueva.
        </p>
        <Link
          href="/login"
          className="btn-glow mt-4 block rounded-lg px-4 py-2 text-center text-sm font-medium text-accent-foreground"
        >
          Ir a iniciar sesión
        </Link>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3">
      <label className="flex flex-col gap-1.5 text-left">
        <span className="text-xs font-medium text-muted">Contraseña nueva</span>
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
        {loading ? "Guardando…" : "Guardar contraseña"}
      </button>
    </form>
  );
}

export default function RestablecerContrasenaPage() {
  return (
    <main className="flex flex-1 items-center justify-center px-6 py-20">
      <div className="w-full max-w-sm rounded-2xl border border-border bg-surface p-6 shadow-xl shadow-foreground/5">
        <span
          className="flex h-9 w-9 items-center justify-center rounded-lg text-xs font-bold text-white"
          style={{
            background: "linear-gradient(135deg, var(--accent), var(--accent-2))",
          }}
        >
          1K
        </span>
        <h1 className="mt-4 text-lg font-semibold">Crea una contraseña nueva</h1>
        <p className="mt-1 text-sm text-muted">
          El link es válido por 30 minutos y solo se puede usar una vez.
        </p>

        <Suspense>
          <ResetForm />
        </Suspense>
      </div>
    </main>
  );
}
