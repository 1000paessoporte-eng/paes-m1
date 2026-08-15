"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

/**
 * Aparición al entrar en pantalla.
 *
 * El movimiento es corto (12px) y rápido a propósito: en una página de estudio
 * la animación tiene que acompañar la lectura, no hacerse notar. Cualquier
 * cosa más larga que medio segundo se vuelve una espera.
 *
 * `once` evita que el bloque vuelva a animarse cada vez que el estudiante
 * sube y baja la página, que es lo que convierte una animación agradable en
 * una molestia.
 */
export function Reveal({
  children,
  delay = 0,
  className,
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
}) {
  const quieto = useReducedMotion();

  if (quieto) return <div className={className}>{children}</div>;

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.45, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  );
}
