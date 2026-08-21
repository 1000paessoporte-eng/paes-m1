"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { motion, useReducedMotion } from "framer-motion";

/**
 * Una sección que existe y todavía no tiene datos de este estudiante.
 *
 * Reemplaza al cartel de "Próximamente" que se usaba acá: la analítica está
 * construida y funcionando, así que anunciarla como algo que aún no existe le
 * dice al estudiante algo falso sobre el producto y le quita la razón para
 * volver. Lo que falta no es la función, son sus datos — y de eso se sale
 * haciendo algo, así que el estado vacío trae el botón para hacerlo.
 */
export function EstadoVacio({
  title,
  description,
  icon,
  accion,
}: {
  title: string;
  description: string;
  icon: ReactNode;
  accion?: { href: string; label: string };
}) {
  return (
    <div className="flex flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10 text-accent">
        {icon}
      </div>
      <h1 className="mt-5 text-xl font-semibold">{title}</h1>
      <p className="mt-2 max-w-md text-sm leading-relaxed text-muted">{description}</p>
      {/* La fila de burbujas que se rellenan al llegar.
          El estado vacío era texto quieto sobre una caja: correcto y sin
          ninguna vida. Estas son las mismas burbujas del cartón de respuestas
          que el alumno va a rellenar adentro, así que la pantalla que dice
          "todavía no hay nada" muestra exactamente qué es lo que falta hacer.
          Se rellenan UNA VEZ al entrar y se quedan quietas: un bucle acá sería
          un anuncio parpadeando. */}
      <BurbujasVacias />

      {accion && (
        <Link
          href={accion.href}
          className="btn-glow mt-6 rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground"
        >
          {accion.label}
        </Link>
      )}
    </div>
  );
}

/**
 * Cinco burbujas del cartón de respuestas que se rellenan al llegar.
 *
 * Es la marca puesta donde el producto todavía no tiene nada que mostrar: en
 * vez de un cartel quieto, la pantalla enseña el gesto que el alumno va a
 * repetir cientos de veces adentro.
 *
 * Se rellenan una sola vez, de izquierda a derecha, y se quedan. Un bucle acá
 * sería un anuncio parpadeando en una pantalla que ya está diciendo que no
 * pasa nada.
 */
function BurbujasVacias() {
  const quieto = useReducedMotion();
  const letras = ["A", "B", "C", "D", "E"];

  return (
    <div className="mt-7 flex gap-2" aria-hidden>
      {letras.map((letra, i) => (
        <motion.span
          key={letra}
          className="burbuja flex h-7 w-7 items-center justify-center rounded-full text-xs font-medium text-muted"
          initial={quieto ? false : { opacity: 0, scale: 0.7 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3, delay: 0.15 + i * 0.07, ease: [0.16, 1, 0.3, 1] }}
        >
          {letra}
        </motion.span>
      ))}
    </div>
  );
}
