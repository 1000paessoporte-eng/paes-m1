"use client";

import { motion, useReducedMotion } from "framer-motion";

/**
 * Barra de progreso que se llena al aparecer.
 *
 * Lleva `role="progressbar"` con sus valores: un lector de pantalla anuncia
 * "68 por ciento" sin depender de que la animación ocurra. La animación es
 * para el que ve; el dato está igual para todos.
 *
 * El largo lo da `width` y la animación solo escala horizontalmente, así que
 * si el JavaScript falla la barra igual queda del tamaño correcto.
 */
export function BarraProgreso({
  porcentaje,
  color = "var(--accent)",
  etiqueta,
  alto = "h-2",
  delay = 0,
}: {
  porcentaje: number;
  color?: string;
  etiqueta: string;
  alto?: string;
  delay?: number;
}) {
  const quieto = useReducedMotion();
  const valor = Math.max(0, Math.min(100, porcentaje));

  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(valor)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={etiqueta}
      className={`w-full overflow-hidden rounded-full bg-surface-hover ${alto}`}
    >
      <motion.div
        className="h-full rounded-full"
        style={{
          width: `${valor}%`,
          background: color,
          transformOrigin: "left center",
        }}
        initial={quieto ? false : { scaleX: 0 }}
        whileInView={{ scaleX: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }}
      />
    </div>
  );
}
