"use client";

import { useEffect } from "react";
import "./globals.css";

export default function GlobalError({
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
    <html lang="es" className="h-full antialiased">
      <body className="min-h-full flex flex-1 items-center justify-center bg-background px-6 py-20 text-foreground">
        <div className="flex max-w-sm flex-col items-center rounded-2xl border border-border bg-surface px-6 py-12 text-center shadow-xl shadow-foreground/5">
          <span className="text-5xl font-semibold tracking-tight text-accent">
            ⚠
          </span>
          <h1 className="mt-3 text-lg font-semibold">
            La aplicación no pudo cargar
          </h1>
          <p className="mt-2 text-sm text-muted">
            Ocurrió un error inesperado al iniciar la página. Intenta de
            nuevo.
          </p>
          <button
            onClick={reset}
            className="btn-glow mt-6 rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
          >
            Reintentar
          </button>
        </div>
      </body>
    </html>
  );
}
