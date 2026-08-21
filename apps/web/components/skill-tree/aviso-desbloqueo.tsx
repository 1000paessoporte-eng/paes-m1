"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";

/**
 * El momento en que se abre un nodo del árbol.
 *
 * El árbol promete un desbloqueo: practicas un tema, lo dominas, y se abre el
 * siguiente. Pero eso pasaba en silencio y solo se contaba al final de la
 * sesión, en un recuadro de texto, cuando el alumno ya estaba mirando otra
 * cosa. El único momento del producto que se gana --que no se regala por
 * entrar-- no tenía ninguna señal.
 *
 * Acá se avisa CUANDO pasa: el aviso baja, el círculo se llena y se va solo a
 * los cuatro segundos y medio. No interrumpe: no hay botón que apretar ni
 * nada que cerrar, porque el alumno está a mitad de una ronda de práctica y
 * cortarlo para felicitarlo sería cobrarle la felicitación.
 *
 * Nada de confeti. Esto es una herramienta de estudio para alguien de
 * dieciocho años que se juega la universidad, no un juego de teléfono.
 */

/** Cuánto queda en pantalla antes de irse solo. */
const MS_VISIBLE = 4500;

export function AvisoDesbloqueo({ nodos }: { nodos: string[] }) {
  const quieto = useReducedMotion();

  // Qué tanda ya se mostró y se fue. Se guarda la CLAVE de la tanda y no un
  // booleano: si después se abre otro nodo, la clave cambia y el aviso vuelve
  // a salir solo.
  //
  // Lo visible se DERIVA de las props en vez de copiarse a estado dentro de un
  // efecto: escribir estado sincrónicamente en un efecto encadena renders, y
  // este proyecto lo tiene prohibido por regla de lint.
  const [tandaOculta, setTandaOculta] = useState<string | null>(null);
  const clave = nodos.join("|");
  const visible = nodos.length > 0 && tandaOculta !== clave;

  useEffect(() => {
    if (!visible) return;
    const id = setTimeout(() => setTandaOculta(clave), MS_VISIBLE);
    return () => clearTimeout(id);
  }, [visible, clave]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          // `polite` y no `assertive`: es una buena noticia, no una alerta.
          role="status"
          aria-live="polite"
          initial={quieto ? { opacity: 0 } : { opacity: 0, y: -24, scale: 0.96 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={quieto ? { opacity: 0 } : { opacity: 0, y: -16, scale: 0.98 }}
          transition={{ duration: 0.42, ease: [0.16, 1, 0.3, 1] }}
          className="fixed top-20 left-1/2 z-50 w-[min(22rem,calc(100vw-2rem))] -translate-x-1/2"
        >
          <div className="flex items-start gap-3 rounded-2xl border border-success/40 bg-background p-4 shadow-[0_8px_32px_-12px_rgb(var(--sombra-color)/0.35)]">
            {/* El círculo se llena: es el mismo gesto del nodo pasando de
                bloqueado a disponible en el árbol. */}
            <motion.span
              className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-success"
              initial={quieto ? false : { scale: 0.3, opacity: 0.4 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.45, delay: 0.12, ease: [0.34, 1.56, 0.64, 1] }}
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="var(--on-fill)"
                strokeWidth="3"
                strokeLinecap="round"
                strokeLinejoin="round"
                aria-hidden="true"
              >
                <path d="M20 6 9 17l-5-5" />
              </svg>
            </motion.span>

            <div className="min-w-0">
              <p className="text-sm font-semibold text-success">
                {nodos.length === 1 ? "Tema desbloqueado" : "Temas desbloqueados"}
              </p>
              <p className="mt-0.5 text-sm leading-snug">{nodos.join(" · ")}</p>
              <p className="mt-1 text-xs text-muted">
                Ya puedes practicarlo en el árbol.
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
