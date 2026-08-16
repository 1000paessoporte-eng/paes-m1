"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { marcarMostrado } from "@/lib/anuncios";

/**
 * El aviso del plan Pro para quien está en el plan Gratis.
 *
 * Muestra el consumo real —"llevas 3 de 4 ensayos este mes"— antes que el
 * precio. Un aviso que parte por lo que cuesta es publicidad; uno que parte
 * por dónde va la persona es información, y solo después ofrece la salida.
 * Con el consumo en cero el argumento no existe todavía, así que el panel lo
 * omite: insistirle con un tope a quien no se ha acercado a él es ruido.
 *
 * Aparece con retraso y no de inmediato: quien entra apurado a rendir un
 * ensayo alcanza a ver dónde está parado antes de que algo lo interrumpa.
 */

const ESPERA_MS = 1200;

export function AnuncioPlanes({
  usados,
  limite,
  precio,
}: {
  usados: number;
  limite: number | null;
  precio: string;
}) {
  const [abierto, setAbierto] = useState(false);
  const quieto = useReducedMotion();
  const cerrarRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    const id = setTimeout(() => setAbierto(true), ESPERA_MS);
    return () => clearTimeout(id);
  }, []);

  useEffect(() => {
    if (!abierto) return;
    cerrarRef.current?.focus();
    function alPresionar(e: KeyboardEvent) {
      if (e.key === "Escape") cerrar();
    }
    document.addEventListener("keydown", alPresionar);
    return () => document.removeEventListener("keydown", alPresionar);
  }, [abierto]);

  function cerrar() {
    marcarMostrado("planes");
    setAbierto(false);
  }

  const restantes = limite != null ? Math.max(0, limite - usados) : null;
  const sinCupo = restantes === 0;

  return (
    <AnimatePresence>
      {abierto && (
        <motion.div
          className="fixed inset-0 z-50 flex items-end justify-center bg-foreground/40 p-4 backdrop-blur-sm sm:items-center"
          initial={quieto ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={cerrar}
        >
          <motion.div
            role="dialog"
            aria-modal="true"
            aria-labelledby="titulo-planes"
            onClick={(e) => e.stopPropagation()}
            initial={quieto ? false : { opacity: 0, y: 24, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="card-panel relative w-full max-w-lg overflow-hidden p-6 sm:p-7"
          >
            <button
              ref={cerrarRef}
              type="button"
              onClick={cerrar}
              aria-label="Cerrar el anuncio"
              className="absolute top-3 right-3 flex h-8 w-8 items-center justify-center rounded-full text-muted transition-colors hover:bg-surface-hover hover:text-foreground"
            >
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2.2"
                strokeLinecap="round"
                aria-hidden
              >
                <path d="M6 6l12 12M18 6L6 18" />
              </svg>
            </button>

            <span className="inline-block rounded-full bg-accent/10 px-2.5 py-1 text-[11px] font-semibold text-accent">
              Plan Pro
            </span>

            <h2
              id="titulo-planes"
              className="mt-3 text-2xl font-bold tracking-tight sm:text-3xl"
            >
              {sinCupo
                ? "Te quedaste sin ensayos este mes"
                : "Ensayos sin límite y todo tu progreso"}
            </h2>

            {limite != null && (
              <div className="mt-4 rounded-xl border border-border bg-surface p-4">
                <div className="flex items-baseline justify-between gap-3 text-sm">
                  <span className="tabular-nums">
                    <strong>{usados}</strong>
                    <span className="text-muted"> de {limite} ensayos este mes</span>
                  </span>
                  <span
                    className={
                      "shrink-0 text-xs font-medium " +
                      (sinCupo ? "text-accent-warm-strong" : "text-muted")
                    }
                  >
                    {sinCupo ? "Sin cupo" : `Te quedan ${restantes}`}
                  </span>
                </div>
                <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-surface-hover">
                  <div
                    className="h-full rounded-full transition-[width] duration-700"
                    style={{
                      width: `${Math.min(100, (usados / limite) * 100)}%`,
                      background: sinCupo
                        ? "var(--accent-warm)"
                        : "var(--accent)",
                    }}
                  />
                </div>
              </div>
            )}

            <ul className="mt-4 flex flex-col gap-2 text-sm text-muted">
              {[
                "Ensayos sin límite, de las cinco pruebas",
                "Comparación de tu puntaje entre ensayos y por eje",
                "Hasta 10 preferencias en Mi meta, con simulador",
                "Recomendación automática de qué reforzar",
              ].map((item) => (
                <li key={item} className="flex gap-2">
                  <span aria-hidden className="text-accent">
                    ✓
                  </span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>

            <div className="mt-5 flex flex-wrap items-center gap-3">
              <Link
                href="/planes"
                onClick={cerrar}
                className="btn-glow rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground"
              >
                Ver el plan Pro · {precio}
              </Link>
              <button
                type="button"
                onClick={cerrar}
                className="rounded-lg border border-border px-4 py-2.5 text-sm font-medium transition-colors hover:bg-surface-hover"
              >
                Ahora no
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
