"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <main className="flex flex-1 items-center justify-center px-6 py-20">
      <div className="flex max-w-sm flex-col items-center rounded-2xl border border-border bg-surface px-6 py-12 text-center shadow-xl shadow-foreground/5">
        <span className="text-5xl font-semibold tracking-tight text-accent">
          ⚠
        </span>
        <h1 className="mt-3 text-lg font-semibold">Algo salió mal</h1>
        <p className="mt-2 text-sm text-muted">
          Ocurrió un error inesperado. Puedes intentar de nuevo o volver al
          inicio.
        </p>
        <div className="mt-6 flex gap-3">
          <button
            onClick={reset}
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
          >
            Reintentar
          </button>
          <Link
            href="/"
            className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium text-foreground"
          >
            Volver al inicio
          </Link>
        </div>
      </div>
    </main>
  );
}
