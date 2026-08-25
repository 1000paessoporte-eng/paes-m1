"use client";

import Link from "next/link";
import { useEffect } from "react";
import { IconoAdvertencia } from "@/components/ui/iconos";

export default function DashboardError({
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
    <div className="flex flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
      <span className="flex h-11 w-11 items-center justify-center rounded-full bg-accent/10 text-accent">
        <IconoAdvertencia tamano={22} />
      </span>
      <h1 className="mt-3 text-lg font-semibold">No se pudo cargar esta sección</h1>
      <p className="mt-2 max-w-md text-sm text-muted">
        Hubo un problema al conectar con el servidor. Puedes reintentar o
        volver al árbol de habilidades.
      </p>
      <div className="mt-6 flex gap-3">
        <button
          onClick={reset}
          className="btn-glow rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
        >
          Reintentar
        </button>
        <Link
          href="/arbol"
          className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium text-foreground"
        >
          Ir al árbol
        </Link>
      </div>
    </div>
  );
}
