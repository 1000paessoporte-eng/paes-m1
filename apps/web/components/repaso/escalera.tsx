"use client";

import { motion, useReducedMotion } from "framer-motion";

/** Los mismos peldaños que aplica el servidor. Si cambian allá, cambian acá. */
export const ESCALERA_DIAS = [1, 3, 7, 16, 35] as const;

/**
 * En qué peldaño va una pregunta, dibujado.
 *
 * El repaso entero se apoya en una idea --"cada vez que la aciertas tarda más
 * en volver, y a la quinta se va"-- que hasta ahora no se veía en ninguna
 * parte: la pantalla parecía un cuestionario cualquiera. Cinco barras que
 * crecen dicen en un vistazo cuánto falta para sacarse esa pregunta de encima,
 * y convierten acertar en algo que se ve avanzar.
 *
 * Las barras crecen de alto además de encenderse: el color solo no basta para
 * quien no lo distingue, y la altura ya dice "esto va subiendo".
 */
export function Escalera({
  nivel,
  color,
  className = "",
}: {
  /** Peldaños ya conseguidos, de 0 a 5. */
  nivel: number;
  /** El color de la prueba a la que pertenece la pregunta. */
  color: string;
  className?: string;
}) {
  const quieto = useReducedMotion();

  return (
    <div
      className={`flex items-end gap-[3px] ${className}`}
      role="img"
      aria-label={
        nivel >= ESCALERA_DIAS.length
          ? "Pregunta dominada"
          : `Peldaño ${nivel} de ${ESCALERA_DIAS.length}`
      }
    >
      {ESCALERA_DIAS.map((dias, i) => {
        const alcanzado = i < nivel;
        return (
          <motion.span
            key={dias}
            className="w-[7px] rounded-sm"
            style={{
              height: 11 + i * 5,
              backgroundColor: alcanzado
                ? color
                : `color-mix(in srgb, ${color} 14%, transparent)`,
              outline: alcanzado ? "none" : "1px solid var(--border)",
              outlineOffset: -1,
            }}
            initial={quieto || !alcanzado ? false : { scaleY: 0, originY: 1 }}
            animate={{ scaleY: 1 }}
            transition={{ duration: 0.3, delay: i * 0.05 }}
          />
        );
      })}
    </div>
  );
}
