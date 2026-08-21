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
 *
 * NO lleva `whitespace-nowrap`. Lo llevaba, y en un teléfono de 390px el
 * titular medía 440: "Competencia Lectora" no cabe en una línea a ese tamaño y
 * salía cortado por los dos lados. Era lo PRIMERO que veía cualquiera que
 * llegara desde el teléfono, que es de donde va a llegar la publicidad.
 *
 * Dejarlas envolver no reintroduce el salto que el nowrap evitaba: el ancho y
 * el alto los sigue fijando el duplicado invisible de la palabra más larga, y
 * ninguna otra ocupa más líneas que ella.
 */

const INTERVALO_MS = 2400;

export interface PruebaRotativa {
  palabra: string;
  /** El token de color de esa prueba. */
  color: string;
}

export function TituloRotativo({ palabras }: { palabras: PruebaRotativa[] }) {
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
  const masLarga = palabras.reduce(
    (a, b) => (a.palabra.length >= b.palabra.length ? a : b),
    palabras[0]
  ).palabra;

  return (
    <span className="relative inline-grid align-bottom">
      <span aria-hidden className="invisible col-start-1 row-start-1">
        {masLarga}
      </span>
      <span className="col-start-1 row-start-1 overflow-hidden">
        <AnimatePresence mode="wait" initial={false}>
          <motion.span
            key={palabras[i].palabra}
            className="inline-block"
            /* Cada prueba se dice en SU color, el mismo del árbol y del
               selector de ensayo. Antes el titular llevaba el degradado de
               marca, que no significaba nada; ahora el color del titular es
               un dato: te está mostrando las cinco pruebas y su código de
               color al mismo tiempo. */
            style={{ color: palabras[i].color }}
            initial={quieto ? false : { y: "0.9em", opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={quieto ? undefined : { y: "-0.9em", opacity: 0 }}
            transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
          >
            {palabras[i].palabra}
          </motion.span>
        </AnimatePresence>
      </span>
    </span>
  );
}
