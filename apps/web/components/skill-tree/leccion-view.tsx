"use client";

import Link from "next/link";
import { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import type { Lesson } from "@/lib/api";
import { TextoRico } from "@/components/texto-rico";

/**
 * La parte de "aprender" de un nodo del árbol.
 *
 * El orden de la página es el orden en que se aprende: primero para qué sirve,
 * después las propiedades, después un ejercicio resuelto y al final la práctica.
 *
 * Los pasos del ejemplo se revelan de a uno. No es un adorno: leer una
 * resolución completa de corrido da la sensación de haber entendido sin haber
 * pensado nada. Obligar a avanzar paso a paso deja el espacio para anticipar
 * qué viene, que es donde se aprende. Igual está el botón para verlos todos,
 * porque quien vuelve a repasar no necesita el ejercicio de nuevo.
 */
export function LeccionView({
  leccion,
  yaPracticado,
}: {
  leccion: Lesson;
  yaPracticado: boolean;
}) {
  const quieto = useReducedMotion();
  const total = leccion.example_steps.length;
  // Quien ya practicó este nodo viene de vuelta: se le muestra todo.
  const [visibles, setVisibles] = useState(yaPracticado ? total : 1);

  const faltan = total - visibles;

  return (
    <article className="mx-auto w-full max-w-3xl">
      <header>
        <p className="text-xs font-medium tracking-wide text-accent uppercase">
          Aprender
        </p>
        <h1 className="mt-1 text-2xl font-bold tracking-tight sm:text-3xl">
          {leccion.node_name}
        </h1>
        <p className="mt-3 text-base leading-relaxed text-muted">{leccion.intro}</p>
      </header>

      {/* ── Propiedades ─────────────────────────────────────────────── */}
      <section className="card-panel mt-8 p-6" aria-labelledby="h-teoria">
        <h2 id="h-teoria" className="text-lg font-semibold tracking-tight">
          Lo que hay que saber
        </h2>
        <div className="mt-4 leading-relaxed">
          <TextoRico texto={leccion.theory} />
        </div>
      </section>

      {/* ── Ejemplo resuelto ────────────────────────────────────────── */}
      <section className="card-panel mt-5 p-6" aria-labelledby="h-ejemplo">
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <h2 id="h-ejemplo" className="text-lg font-semibold tracking-tight">
            Ejemplo resuelto
          </h2>
          <span className="text-xs tabular-nums text-muted">
            {visibles} de {total} pasos
          </span>
        </div>

        <div className="mt-4 rounded-xl border border-accent/30 bg-accent/5 p-4">
          <TextoRico texto={leccion.example_statement} />
        </div>

        <ol className="mt-5 flex flex-col gap-4">
          {leccion.example_steps.slice(0, visibles).map((paso, i) => (
            <motion.li
              key={i}
              initial={quieto ? false : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
              className="flex gap-3"
            >
              <span
                className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-accent text-sm font-bold text-accent-foreground"
                aria-hidden
              >
                {i + 1}
              </span>
              <div className="min-w-0 flex-1">
                <div className="leading-relaxed">
                  <TextoRico texto={paso.accion} />
                </div>
                {/* El porqué es la mitad que enseña: sin él, el paso es una
                    receta que se copia y se olvida. */}
                <div className="mt-2 border-l-2 border-border pl-3 text-sm text-muted">
                  <span className="font-medium text-foreground">Por qué: </span>
                  <TextoRico texto={paso.porque} inline />
                </div>
              </div>
            </motion.li>
          ))}
        </ol>

        {faltan > 0 && (
          <div className="mt-5 flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={() => setVisibles((v) => v + 1)}
              className="btn-glow rounded-lg px-4 py-2 text-sm font-semibold text-accent-foreground"
            >
              Ver el paso siguiente
            </button>
            <button
              type="button"
              onClick={() => setVisibles(total)}
              className="text-sm text-muted underline-offset-4 hover:text-foreground hover:underline"
            >
              Mostrar los {faltan} que faltan
            </button>
          </div>
        )}
      </section>

      {/* ── Error típico ────────────────────────────────────────────── */}
      {leccion.common_error && (
        <section
          className="mt-5 rounded-xl border border-warning/40 bg-warning/10 p-5"
          aria-labelledby="h-error"
        >
          <h2 id="h-error" className="text-sm font-semibold text-warning">
            El error más común
          </h2>
          <div className="mt-2 text-sm leading-relaxed">
            <TextoRico texto={leccion.common_error} />
          </div>
        </section>
      )}

      {/* ── A practicar ─────────────────────────────────────────────── */}
      <section className="card-panel mt-5 flex flex-wrap items-center justify-between gap-4 p-6">
        <div>
          <h2 className="font-semibold tracking-tight">
            Ahora practica lo que acabas de leer
          </h2>
          <p className="mt-1 text-sm text-muted">
            Preguntas de este mismo tema, una a una y con corrección inmediata.
          </p>
        </div>
        <Link
          href={`/practicar/${leccion.node_code}`}
          className="btn-warm shrink-0 rounded-lg px-5 py-2.5 text-sm font-semibold text-on-fill"
        >
          Practicar este tema →
        </Link>
      </section>

      <p className="mt-6 text-center text-sm">
        <Link
          href="/arbol"
          className="text-muted underline-offset-4 hover:text-foreground hover:underline"
        >
          ← Volver al árbol
        </Link>
      </p>
    </article>
  );
}
