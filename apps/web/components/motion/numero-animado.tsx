"use client";

import { animate, useInView, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

/**
 * Número que sube hasta su valor cuando aparece en pantalla.
 *
 * Se usa para puntajes y totales del panel. El conteo no es decoración: hace
 * que el ojo se detenga en la cifra que cambió, que es justo lo que el
 * estudiante viene a mirar.
 *
 * El valor final se escribe igual en el HTML del servidor, así que quien tenga
 * el JavaScript caído o el movimiento desactivado ve el número correcto de
 * entrada. La animación solo ocurre encima.
 */
export function NumeroAnimado({
  valor,
  duracion = 1,
  sufijo = "",
  className,
}: {
  valor: number;
  duracion?: number;
  sufijo?: string;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const visible = useInView(ref, { once: true, margin: "-30px" });
  const quieto = useReducedMotion();

  // Arranca ya en el valor final: si nunca se anima (movimiento reducido, o el
  // bloque no llega a entrar en pantalla), la cifra que se ve es la correcta.
  const [mostrado, setMostrado] = useState(valor);

  // Si la prop cambia, el estado se ajusta durante el render y no en un
  // efecto. Es el patrón que recomienda React para estado derivado: un efecto
  // acá provoca un render de más con la cifra vieja en pantalla.
  const [valorPrevio, setValorPrevio] = useState(valor);
  if (valor !== valorPrevio) {
    setValorPrevio(valor);
    setMostrado(valor);
  }

  useEffect(() => {
    if (quieto || !visible) return;
    // `animate` actualiza en cada cuadro, fuera del ciclo de render.
    const controles = animate(0, valor, {
      duration: duracion,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => setMostrado(Math.round(v)),
    });
    return () => controles.stop();
  }, [valor, visible, quieto, duracion]);

  return (
    <span ref={ref} className={className}>
      {mostrado.toLocaleString("es-CL")}
      {sufijo}
    </span>
  );
}
