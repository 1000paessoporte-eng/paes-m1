"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { IconoLogro, Logro } from "@/lib/logros";
import {
  IconoBrote,
  IconoCorona,
  IconoCumbre,
  IconoDiana,
  IconoLibros,
  IconoLlama,
  IconoPunteria,
  IconoRayo,
  type PropsIcono,
} from "@/components/ui/iconos";

/** La clave que guarda `lib/logros.ts` se convierte acá en el dibujo. */
const ICONOS: Record<IconoLogro, (props: PropsIcono) => React.ReactElement> = {
  diana: IconoDiana,
  libros: IconoLibros,
  llama: IconoLlama,
  rayo: IconoRayo,
  punteria: IconoPunteria,
  brote: IconoBrote,
  cumbre: IconoCumbre,
  corona: IconoCorona,
};

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
        className={
          (quieto ? "flex" : "llama flex") + " text-accent-warm-strong"
        }
        aria-hidden
      >
        <IconoLlama tamano={Math.round(Math.min(16 + dias * 0.64, 22))} />
      </span>
      <span className="text-sm font-semibold text-accent-warm-strong">
        {dias} {dias === 1 ? "día seguido" : "días seguidos"}
      </span>
    </div>
  );
}

/**
 * El dibujo de una insignia. La conseguida toma el color de acento; la
 * bloqueada queda apagada, que es lo que antes hacía el `grayscale` sobre el
 * emoji —y que sobre un emoji nunca funcionó del todo.
 */
function IconoDeLogro({ logro }: { logro: Logro }) {
  const Icono = ICONOS[logro.icono];
  return (
    <Icono
      tamano={22}
      className={logro.conseguido ? "text-accent" : "text-muted opacity-40"}
    />
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
              <IconoDeLogro logro={logro} />
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
