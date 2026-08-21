"use client";

import { motion, useReducedMotion } from "framer-motion";

/**
 * Tu puntaje contra el mínimo de una carrera, sobre la escala real.
 *
 * Reemplaza a una línea de texto que decía "812 / 780". Ese número no dice
 * nada solo: no se sabe si 812 está raspando el mínimo o sobrado, ni cuánto
 * falta cuando no alcanza. Sobre la escala de 100 a 1000, con el mínimo
 * marcado, se ve de un vistazo.
 *
 * Y es lo que convierte al simulador en algo que da ganas de tocar: al mover
 * un deslizador el punto se DESPLAZA por la regla y cruza la marca. Ver a
 * "Medicina" pasar de gris a verde es el momento de esta pantalla, y estaba
 * ocurriendo en un texto de 12 píxeles.
 */

/** Los extremos de la escala PAES. */
const MIN = 100;
const MAX = 1000;

function posicion(puntaje: number): number {
  const acotado = Math.min(MAX, Math.max(MIN, puntaje));
  return ((acotado - MIN) / (MAX - MIN)) * 100;
}

export function ReglaPuntaje({
  nombre,
  detalle,
  puntaje,
  minimo,
  color,
}: {
  nombre: string;
  detalle?: string;
  /** El ponderado simulado. `null` cuando faltan puntajes para calcularlo. */
  puntaje: number | null;
  /** El mínimo de postulación que declara la carrera, si lo declara. */
  minimo: number | null;
  color: string;
}) {
  const quieto = useReducedMotion();
  const alcanza = puntaje != null && minimo != null && puntaje >= minimo;
  const brecha = puntaje != null && minimo != null ? minimo - puntaje : null;

  return (
    <li className="py-2.5">
      <div className="flex items-baseline justify-between gap-3">
        <p className="min-w-0 truncate text-sm font-medium">
          {nombre}
          {detalle && <span className="font-normal text-muted"> · {detalle}</span>}
        </p>
        <p className="shrink-0 text-xs tabular-nums">
          {puntaje == null ? (
            <span className="text-muted">faltan puntajes</span>
          ) : minimo == null ? (
            <span className="text-muted">{puntaje} pts · sin mínimo</span>
          ) : alcanza ? (
            <span className="font-semibold text-success">alcanzas el mínimo</span>
          ) : (
            <span className="text-muted">
              te faltan <strong className="text-foreground">{brecha}</strong> pts
            </span>
          )}
        </p>
      </div>

      {/* La regla. Va de 100 a 1000 SIEMPRE, no reescalada a los valores de
          esta carrera: la gracia es comparar todas las preferencias sobre la
          misma vara, y una escala que se ajusta por fila haría que dos puntos
          distintos se vean en el mismo lugar. */}
      <div className="relative mt-2 h-2 rounded-full bg-surface-hover">
        {puntaje != null && (
          <motion.div
            className="absolute inset-y-0 left-0 rounded-full"
            style={{ backgroundColor: alcanza ? "var(--success)" : color }}
            initial={false}
            animate={{ width: `${posicion(puntaje)}%` }}
            transition={
              quieto ? { duration: 0 } : { type: "spring", stiffness: 260, damping: 30 }
            }
          />
        )}

        {/* El mínimo: una marca vertical, no un color de fondo. Es un umbral
            --se cruza o no se cruza-- y un degradado lo volvería difuso. */}
        {minimo != null && (
          <span
            className="absolute -top-1 -bottom-1 w-[2px] rounded-full bg-foreground"
            style={{ left: `${posicion(minimo)}%` }}
            aria-hidden
          />
        )}

        {puntaje != null && (
          <motion.span
            className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-surface"
            style={{ backgroundColor: alcanza ? "var(--success)" : color }}
            initial={false}
            animate={{ left: `${posicion(puntaje)}%` }}
            transition={
              quieto ? { duration: 0 } : { type: "spring", stiffness: 260, damping: 30 }
            }
          />
        )}
      </div>

      <div className="mt-1 flex justify-between text-[10px] text-muted tabular-nums">
        <span>{MIN}</span>
        {minimo != null && <span>mínimo {minimo}</span>}
        <span>{MAX}</span>
      </div>
    </li>
  );
}
