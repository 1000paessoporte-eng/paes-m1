"use client";

import type { ReactNode } from "react";
import { Children } from "react";
import { motion, useReducedMotion } from "framer-motion";

/**
 * La entrada del hero, escalonada en el orden en que se lee.
 *
 * Es UNA secuencia y no cinco animaciones sueltas: el reloj, el titular, la
 * bajada y la acción entran uno detrás de otro. Acompañar el orden de lectura
 * hace que la primera pantalla se sienta armada; animar todo a la vez, o cada
 * cosa por su cuenta, se siente como una página que se cae a pedazos.
 *
 * Es CORTA a propósito: 90 ms entre elemento y 380 ms cada uno, así que a los
 * 700 ms está todo puesto. Una entrada más lenta se ve elegante la primera vez
 * y estorba las siguientes, y esta es una página a la que la gente vuelve.
 *
 * Con `prefers-reduced-motion` no hay entrada: todo aparece ya en su sitio.
 */

const RETARDO_ENTRE_HIJOS = 0.09;
const DURACION = 0.38;

export function EntradaHero({
  children,
  className,
}: {
  children: ReactNode;
  className?: string;
}) {
  const quieto = useReducedMotion();

  if (quieto) return <div className={className}>{children}</div>;

  return (
    <motion.div
      className={className}
      initial="oculto"
      animate="visible"
      variants={{
        visible: { transition: { staggerChildren: RETARDO_ENTRE_HIJOS } },
      }}
    >
      {Children.map(children, (hijo, i) => (
        <motion.div
          key={i}
          // `contents` deja que el hijo herede el layout del contenedor: sin
          // esto cada envoltorio se vuelve un bloque y rompe el `gap` y el
          // centrado del flex de afuera.
          className="contents"
          variants={{
            oculto: { opacity: 0, y: 14 },
            visible: {
              opacity: 1,
              y: 0,
              transition: { duration: DURACION, ease: [0.16, 1, 0.3, 1] },
            },
          }}
        >
          {hijo}
        </motion.div>
      ))}
    </motion.div>
  );
}
