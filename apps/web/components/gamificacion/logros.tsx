"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { Logro } from "@/lib/logros";

/**
 * Racha e insignias del estudiante.
 *
 * Qué cuenta como logro y cuándo se consigue vive en `lib/logros.ts`, fuera de
 * este archivo: el panel es un Server Component y necesita calcularlos durante
 * el render, y una función exportada desde un módulo `"use client"` no se
 * puede llamar desde el servidor.
 *
 * Las bloqueadas se muestran igual, apagadas y con el requisito escrito, para
 * que funcionen como meta y no como sorpresa.
 */

/** Llama de la racha. Crece con los días, pero se detiene: no puede tapar el número. */
export function Racha({ dias }: { dias: number }) {
  const quieto = useReducedMotion();
  if (dias <= 0) return null;

  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-accent-warm/30 bg-accent-warm/10 px-3 py-1.5">
      <span
        className={quieto ? "" : "llama"}
        style={{ fontSize: `${Math.min(1 + dias * 0.04, 1.35)}rem`, lineHeight: 1 }}
        aria-hidden
      >
        🔥
      </span>
      <span className="text-sm font-semibold text-accent-warm-strong">
        {dias} {dias === 1 ? "día seguido" : "días seguidos"}
      </span>
    </div>
  );
}

export function Insignias({ logros }: { logros: Logro[] }) {
  const quieto = useReducedMotion();
  const conseguidos = logros.filter((l) => l.conseguido).length;

  return (
    <section className="card-panel p-6" aria-labelledby="h-logros">
      <div className="flex items-baseline justify-between gap-3">
        <h2 id="h-logros" className="font-semibold tracking-tight">
          Logros
        </h2>
        <span className="text-xs tabular-nums text-muted">
          {conseguidos} de {logros.length}
        </span>
      </div>

      <ul className="mt-4 grid grid-cols-4 gap-3 sm:grid-cols-4">
        {logros.map((logro, i) => (
          <li key={logro.id}>
            <motion.div
              initial={quieto ? false : { opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{
                duration: 0.4,
                delay: i * 0.05,
                ease: [0.16, 1, 0.3, 1],
              }}
              className={
                "relative flex aspect-square flex-col items-center justify-center gap-1 overflow-hidden rounded-xl border p-1 text-center " +
                (logro.conseguido
                  ? "border-accent/30 bg-accent/10"
                  : "border-border bg-surface")
              }
              // El título nativo da el detalle en escritorio; el texto de abajo
              // lo da en móvil, donde no hay hover.
              title={
                logro.conseguido
                  ? `${logro.titulo} — conseguido`
                  : `${logro.titulo} — ${logro.requisito}`
              }
            >
              {/* El destello solo recorre las insignias ya conseguidas: es la
                  recompensa, no un adorno permanente. */}
              {logro.conseguido && !quieto && (
                <span className="destello pointer-events-none absolute inset-0 opacity-60" />
              )}
              <span
                className={"text-xl " + (logro.conseguido ? "" : "opacity-30 grayscale")}
                aria-hidden
              >
                {logro.icono}
              </span>
              <span
                className={
                  "px-0.5 text-[10px] leading-tight " +
                  (logro.conseguido ? "font-semibold" : "text-muted")
                }
              >
                {logro.titulo}
              </span>
              <span className="sr-only">
                {logro.conseguido ? "Conseguido" : `Bloqueado: ${logro.requisito}`}
              </span>
            </motion.div>
          </li>
        ))}
      </ul>

      <p className="mt-4 text-xs text-muted">
        Cada logro se calcula con tus ensayos reales. Los apagados muestran lo
        que falta para desbloquearlos.
      </p>
    </section>
  );
}
