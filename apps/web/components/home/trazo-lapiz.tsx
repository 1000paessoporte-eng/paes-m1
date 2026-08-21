"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useEffect, useState } from "react";
import { COLOR_PRUEBA } from "@/lib/colores-prueba";
import type { Subject } from "@/lib/api";

/**
 * El subrayado a lápiz que se dibuja solo bajo el titular, una y otra vez,
 * cambiando de color por cada prueba PAES.
 *
 * Reemplaza a la palabra que rotaba dentro del titular. Hacía dos cosas: se
 * movía --que es lo que hace que un titular se mire-- y decía sin decirlo que
 * acá están las cinco pruebas y no solo matemática. Pero para no saltar tenía
 * que reservar el ancho de la palabra más larga, y en un teléfono eso dejaba
 * una línea en blanco bajo el título.
 *
 * Esto hace el mismo trabajo sin tocar el texto: el trazo recorre los cinco
 * colores de prueba, así que el código de color del producto se enseña en el
 * primer segundo, y como no cambia ni una letra no hay nada que se reacomode.
 *
 * El trazo NO es una línea recta. Es una curva con altibajos de un par de
 * píxeles, como sale cuando uno subraya rápido con un lápiz: una recta
 * perfecta se leería como un borde de CSS, que es justo lo que no queremos.
 *
 * Para quien pidió menos movimiento se dibuja una sola vez, en grafito, y se
 * queda quieto.
 */

/** Las cinco pruebas, en el orden en que las rinde casi todo el mundo. */
const PRUEBAS: Subject[] = ["lectora", "m1", "m2", "ciencias", "historia"];

/** Cuánto dura cada color antes de que el trazo se borre y vuelva a salir. */
const MS_POR_PRUEBA = 2600;

/** El trazo, en un lienzo que se estira al ancho del texto que subraya. */
const CAMINO = "M1,7.5 C48,3.4 96,10.6 148,6.2 C200,2 252,9.8 300,5.4 C334,2.6 366,7 399,4.6";

export function TrazoLapiz({ className = "" }: { className?: string }) {
  const quieto = useReducedMotion();
  const [i, setI] = useState(0);

  useEffect(() => {
    if (quieto) return;
    const id = setInterval(() => setI((v) => (v + 1) % PRUEBAS.length), MS_POR_PRUEBA);
    return () => clearInterval(id);
  }, [quieto]);

  const color = quieto ? "var(--grafito)" : COLOR_PRUEBA[PRUEBAS[i]];

  return (
    <svg
      aria-hidden
      viewBox="0 0 400 12"
      preserveAspectRatio="none"
      className={`pointer-events-none absolute -bottom-1 left-0 h-[0.38em] w-full ${className}`}
    >
      <motion.path
        // La clave cambia con la prueba: cada color vuelve a dibujarse desde
        // cero en vez de teñir el trazo que ya estaba.
        key={quieto ? "fijo" : PRUEBAS[i]}
        d={CAMINO}
        fill="none"
        stroke={color}
        strokeWidth={7}
        strokeLinecap="round"
        vectorEffect="non-scaling-stroke"
        initial={quieto ? { pathLength: 1, opacity: 1 } : { pathLength: 0, opacity: 0.9 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 0.55, ease: [0.65, 0, 0.35, 1] }}
      />
    </svg>
  );
}
