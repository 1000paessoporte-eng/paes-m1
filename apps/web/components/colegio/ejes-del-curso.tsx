"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { EjeDelCurso } from "@/lib/api";

/**
 * Dónde falla el curso completo.
 *
 * Es el dato que un profesor no puede sacar de una lista de puntajes: treinta
 * alumnos con 600 puntos pueden estar fallando todos en el mismo eje, y eso
 * decide qué se pasa la clase del lunes. Por eso va ordenado de PEOR a mejor:
 * lo primero que se lee es lo primero que hay que enseñar.
 */

/** Bajo esto, el eje se marca como el que hay que atacar. */
const UMBRAL_FLOJO = 50;

export function EjesDelCurso({ ejes }: { ejes: EjeDelCurso[] }) {
  const quieto = useReducedMotion();

  if (ejes.length === 0) {
    return (
      <div>
        <h2 className="text-sm font-semibold tracking-wide text-muted uppercase">
          El curso por eje
        </h2>
        <div className="mt-3 rounded-2xl border border-dashed border-border p-6">
          <p className="text-sm font-medium">Sin datos todavía</p>
          <p className="mt-1 text-sm text-muted">
            Cuando tu curso rinda ensayos, acá vas a ver en qué eje del temario
            les va peor.
          </p>
        </div>
      </div>
    );
  }

  const ordenados = [...ejes].sort((a, b) => a.porcentaje - b.porcentaje);
  const peor = ordenados[0];

  return (
    <div>
      <h2 className="text-sm font-semibold tracking-wide text-muted uppercase">
        El curso por eje
      </h2>
      {peor.porcentaje < UMBRAL_FLOJO && (
        <p className="mt-1 text-sm">
          Donde más pierden puntos es{" "}
          <strong>{peor.nombre.toLowerCase()}</strong>: aciertan{" "}
          {peor.porcentaje}% de {peor.respuestas} respuestas.
        </p>
      )}

      <ul className="mt-3 space-y-3 rounded-2xl border border-border bg-surface p-5">
        {ordenados.map((eje, i) => (
          <li key={eje.eje}>
            <div className="flex items-baseline justify-between gap-3">
              <p className="text-sm">{eje.nombre}</p>
              <p className="shrink-0 text-xs tabular-nums">
                <strong className="text-sm">{eje.porcentaje}%</strong>
                <span className="text-muted"> de {eje.respuestas}</span>
              </p>
            </div>
            <span className="mt-1.5 block h-2 rounded-full bg-surface-hover">
              <motion.span
                className="block h-full rounded-full"
                style={{
                  // Verde y rojo acá SÍ son estado --acertar o no-- así que el
                  // color de prueba no corresponde.
                  backgroundColor:
                    eje.porcentaje < UMBRAL_FLOJO ? "var(--danger)" : "var(--success)",
                }}
                initial={quieto ? false : { width: 0 }}
                animate={{ width: `${Math.max(2, eje.porcentaje)}%` }}
                transition={{
                  duration: 0.55,
                  delay: quieto ? 0 : i * 0.06,
                  ease: [0.16, 1, 0.3, 1],
                }}
              />
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
