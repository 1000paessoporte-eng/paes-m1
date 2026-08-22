"use client";

import { motion, useReducedMotion } from "framer-motion";
import { useState } from "react";
import type { AlumnoDelCurso } from "@/lib/api";

/**
 * El avance de cada alumno del curso.
 *
 * Ordenable por lo que el profesor realmente quiere saber, que casi nunca es
 * el orden alfabético: quién no ha entrado, quién va más abajo, quién no
 * practica. Por eso el orden inicial es por ÚLTIMA ACTIVIDAD ascendente --los
 * que llevan más tiempo sin aparecer arriba--, y no por nombre: una lista
 * alfabética esconde justo a los que hay que ir a buscar.
 */

type Criterio = "actividad" | "nombre" | "puntaje" | "ensayos";

const FECHA = new Intl.DateTimeFormat("es-CL", { day: "2-digit", month: "short" });

function ordenar(alumnos: AlumnoDelCurso[], criterio: Criterio): AlumnoDelCurso[] {
  const copia = [...alumnos];
  switch (criterio) {
    case "nombre":
      return copia.sort((a, b) => a.nombre.localeCompare(b.nombre, "es"));
    case "puntaje":
      // Sin puntaje va al final: "todavía no rinde" no es "va mal".
      return copia.sort(
        (a, b) => (b.mejor_puntaje ?? -1) - (a.mejor_puntaje ?? -1)
      );
    case "ensayos":
      return copia.sort((a, b) => b.ensayos - a.ensayos);
    default:
      // Los que nunca rindieron van primero: son los que hay que ir a buscar.
      // `dias_sin_rendir` lo cuenta la API, para no leer el reloj en render.
      return copia.sort(
        (a, b) =>
          (b.dias_sin_rendir ?? Number.MAX_SAFE_INTEGER) -
          (a.dias_sin_rendir ?? Number.MAX_SAFE_INTEGER)
      );
  }
}

export function TablaAlumnos({ alumnos }: { alumnos: AlumnoDelCurso[] }) {
  const quieto = useReducedMotion();
  const [criterio, setCriterio] = useState<Criterio>("actividad");

  if (alumnos.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-border p-8 text-center">
        <p className="text-sm font-medium">Todavía no entra nadie</p>
        <p className="mt-1 text-sm text-muted">
          En cuanto tus alumnos usen el código, van a aparecer acá con su avance.
        </p>
      </div>
    );
  }

  const lista = ordenar(alumnos, criterio);
  // El máximo del curso fija la escala de las barras: comparar contra 1000
  // dejaría todas las barras cortas e iguales.
  const tope = Math.max(...lista.map((a) => a.mejor_puntaje ?? 0), 1);

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-sm font-semibold tracking-wide text-muted uppercase">
          Tu curso · {alumnos.length}{" "}
          {alumnos.length === 1 ? "alumno" : "alumnos"}
        </h2>
        <div className="flex gap-1 rounded-lg border border-border p-0.5 text-xs">
          {(
            [
              ["actividad", "Sin entrar"],
              ["puntaje", "Puntaje"],
              ["ensayos", "Ensayos"],
              ["nombre", "Nombre"],
            ] as const
          ).map(([valor, etiqueta]) => (
            <button
              key={valor}
              type="button"
              onClick={() => setCriterio(valor)}
              className={`rounded-md px-2.5 py-1 transition-colors ${
                criterio === valor
                  ? "bg-surface-hover font-medium text-foreground"
                  : "text-muted hover:text-foreground"
              }`}
            >
              {etiqueta}
            </button>
          ))}
        </div>
      </div>

      <ul className="mt-3 divide-y divide-border rounded-2xl border border-border bg-surface">
        {lista.map((a) => (
          <motion.li
            key={a.user_id}
            // `layout` hace que al cambiar el orden las filas SE MUEVAN a su
            // nuevo lugar en vez de reaparecer barajadas: el profesor sigue
            // con la vista al alumno que estaba mirando.
            layout={!quieto}
            transition={{ type: "spring", stiffness: 320, damping: 34 }}
            className="flex items-center gap-3 p-3"
          >
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{a.nombre}</p>
              <p className="truncate text-xs text-muted">{a.email}</p>
            </div>

            <div className="hidden w-32 shrink-0 sm:block">
              {a.mejor_puntaje != null ? (
                <>
                  <p className="text-right text-xs tabular-nums">
                    <strong className="text-sm">{a.mejor_puntaje}</strong>
                    {a.promedio != null && (
                      <span className="text-muted"> · prom. {a.promedio}</span>
                    )}
                  </p>
                  <span className="mt-1 block h-1 rounded-full bg-surface-hover">
                    <motion.span
                      className="block h-full rounded-full bg-accent-2"
                      initial={quieto ? false : { scaleX: 0 }}
                      animate={{ scaleX: 1 }}
                      style={{
                        transformOrigin: "left",
                        width: `${Math.max(4, (a.mejor_puntaje / tope) * 100)}%`,
                      }}
                      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    />
                  </span>
                </>
              ) : (
                <p className="text-right text-xs text-muted">sin ensayos</p>
              )}
            </div>

            <div className="w-20 shrink-0 text-right text-xs tabular-nums">
              <p>
                {a.ensayos} {a.ensayos === 1 ? "ensayo" : "ensayos"}
              </p>
              <p className="text-muted">
                {a.ultimo_ensayo ? FECHA.format(new Date(a.ultimo_ensayo)) : "—"}
              </p>
            </div>
          </motion.li>
        ))}
      </ul>
    </div>
  );
}
