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
 *
 * Por defecto se llena al entrar en pantalla, que es lo que corresponde a una
 * barra que vive más abajo. Con `alCargar` se llena apenas se monta: una barra
 * que ya está sobre el pliegue no tiene ningún scroll que esperar, y esperarlo
 * la dejaba vacía para siempre.
 */
export function BarraProgreso({
  porcentaje,
  color = "var(--accent)",
  etiqueta,
  alto = "h-2",
  delay = 0,
  alCargar = false,
  secundario,
}: {
  porcentaje: number;
  color?: string;
  etiqueta: string;
  alto?: string;
  delay?: number;
  /** Llenarse al montar en vez de al entrar en pantalla. */
  alCargar?: boolean;
  /**
   * Un segundo tramo, más tenue, detrás del principal. Para cuando lo
   * empezado también es avance y una barra que solo cuenta lo terminado se
   * queda en cero durante semanas.
   *
   * Es decorativo: el `aria-valuenow` sigue siendo el tramo principal, que es
   * el que la etiqueta nombra.
   */
  secundario?: number;
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
      className={`relative w-full overflow-hidden rounded-full bg-surface-hover ${alto}`}
    >
      {secundario != null && secundario > valor && (
        <div
          aria-hidden
          className="absolute inset-y-0 left-0 rounded-full opacity-25"
          style={{ width: `${Math.min(100, secundario)}%`, backgroundColor: color }}
        />
      )}
      <motion.div
        className="relative h-full rounded-full"
        style={{
          width: `${valor}%`,
          background: color,
          transformOrigin: "left center",
        }}
        initial={quieto ? false : { scaleX: 0 }}
        {...(alCargar
          ? { animate: { scaleX: 1 } }
          : { whileInView: { scaleX: 1 }, viewport: { once: true } })}
        transition={
          quieto ? { duration: 0 } : { duration: 0.7, delay, ease: [0.16, 1, 0.3, 1] }
        }
      />
    </div>
  );
}
