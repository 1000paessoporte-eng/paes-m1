"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";

/**
 * Palabra que se va reemplazando dentro del título del hero.
 *
 * Existe para decir varias cosas en el espacio de una: la plataforma cubre
 * cinco pruebas y el titular no alcanza a nombrarlas todas sin volverse una
 * lista. Rotarlas también muestra, sin decirlo, que esto no es solo
 * matemática.
 *
 * La primera palabra se pinta en el servidor, así que el titular está completo
 * y legible aunque el JavaScript no llegue nunca. Para quien pidió menos
 * movimiento, se queda fija en esa primera.
 */

const INTERVALO_MS = 2400;

export function TituloRotativo({ palabras }: { palabras: string[] }) {
  const quieto = useReducedMotion();
  const [i, setI] = useState(0);

  useEffect(() => {
    if (quieto || palabras.length < 2) return;
    const id = setInterval(
      () => setI((v) => (v + 1) % palabras.length),
      INTERVALO_MS
    );
    return () => clearInterval(id);
  }, [quieto, palabras.length]);

  // El ancho lo fija la palabra más larga, medida con un duplicado invisible:
  // sin esto el resto del título se corre en cada cambio y el bloque "salta".
  const masLarga = palabras.reduce((a, b) => (a.length >= b.length ? a : b), "");

  return (
    <span className="relative inline-grid align-bottom">
      <span aria-hidden className="invisible col-start-1 row-start-1 whitespace-nowrap">
        {masLarga}
      </span>
      <span className="col-start-1 row-start-1 overflow-hidden">
        <AnimatePresence mode="wait" initial={false}>
          <motion.span
            key={palabras[i]}
            className="texto-marca inline-block whitespace-nowrap"
            initial={quieto ? false : { y: "0.9em", opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={quieto ? undefined : { y: "-0.9em", opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            {palabras[i]}
          </motion.span>
        </AnimatePresence>
      </span>
    </span>
  );
}
