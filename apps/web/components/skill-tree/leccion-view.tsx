"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import { getSkillNode, type Lesson } from "@/lib/api";
import { getClientToken } from "@/lib/auth";
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
/** Un tema vecino en el índice, para seguir leyendo. */
export interface LeccionVecina {
  node_code: string;
  node_name: string;
  /** El eje al que pertenece. El índice avanza por nivel del árbol y no por
   *  eje, así que sin esto "el tema siguiente" parece un salto arbitrario. */
  axis_label: string;
}

export function LeccionView({
  leccion,
  anterior,
  siguiente,
}: {
  leccion: Lesson;
  anterior?: LeccionVecina | null;
  siguiente?: LeccionVecina | null;
}) {
  const quieto = useReducedMotion();
  const total = leccion.example_steps.length;
  const [visibles, setVisibles] = useState(1);

  // La sesión se lee acá y no en el servidor a propósito: sin eso la página
  // tendría que consultar la cookie al renderizar, y una página que lee la
  // cookie no se puede prerenderizar. Estas lecciones existen sobre todo
  // para quien llega de Google sin cuenta, así que se sirven estáticas y lo
  // único que depende de la sesión —el botón de practicar y el atajo de saltar
  // los pasos— se resuelve en el navegador.
  const [conSesion, setConSesion] = useState(false);

  useEffect(() => {
    const token = getClientToken();
    if (!token) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setConSesion(true);
    // Quien ya practicó este nodo viene de vuelta: se le muestra todo.
    let vigente = true;
    getSkillNode(leccion.node_code, token)
      .then((nodo) => {
        if (vigente && nodo.attempts > 0) setVisibles(total);
      })
      .catch(() => {
        // Que no se pueda saber si ya practicó no es motivo para romper la
        // lección: se queda con el paso a paso, que es el comportamiento
        // normal de quien la lee por primera vez.
      });
    return () => {
      vigente = false;
    };
  }, [leccion.node_code, total]);

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
          {/* La teoría en serif: junto con los textos de Lectora, son los dos
              lugares del producto donde se lee de corrido. */}
          <div className="font-lectura text-[1.02rem] leading-[1.65]">
            <TextoRico texto={leccion.theory} />
          </div>
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
      {/* Leer no basta: el paso siguiente es responder. Con sesión se va
          derecho al tema; sin ella hay que crear cuenta, y la promesa dice
          exactamente eso para que nadie llegue al login por sorpresa. */}
      <section className="card-panel mt-5 flex flex-wrap items-center justify-between gap-4 p-6">
        <div>
          <h2 className="font-semibold tracking-tight">
            Ahora practica lo que acabas de leer
          </h2>
          <p className="mt-1 text-sm text-muted">
            {conSesion
              ? "Preguntas de este mismo tema, una a una y con corrección inmediata."
              : "Preguntas de este mismo tema, una a una y con corrección inmediata. Crear la cuenta es gratis y toma un minuto."}
          </p>
        </div>
        <Link
          href={
            conSesion
              ? `/practicar/${leccion.node_code}`
              : `/registro?next=/practicar/${leccion.node_code}`
          }
          className="btn-glow shrink-0 rounded-lg px-5 py-2.5 text-sm font-semibold text-accent-foreground"
        >
          Practicar este tema →
        </Link>
      </section>

      {/* Las lecciones no se enlazaban entre sí: se terminaba una y el único
          camino era volver al índice. Para quien estudia, el paso natural es
          el tema que sigue en el árbol; para Google, veinte páginas sueltas
          sin enlaces internos valen menos que veinte encadenadas.

          El orden es el del índice, que ya viene por prueba y por posición en
          el árbol: el "siguiente" es el que de verdad viene después. */}
      {(anterior || siguiente) && (
        <nav
          aria-label="Otras lecciones"
          className="mt-10 grid gap-3 border-t border-border pt-6 sm:grid-cols-2"
        >
          {anterior ? (
            <Link
              href={`/aprender/${anterior.node_code}`}
              className="rounded-xl border border-border p-4 transition hover:bg-surface-hover"
            >
              <span className="text-xs text-muted">← Tema anterior</span>
              <span className="mt-0.5 block font-medium">{anterior.node_name}</span>
              <span className="mt-0.5 block text-xs text-muted">{anterior.axis_label}</span>
            </Link>
          ) : (
            <span />
          )}
          {siguiente && (
            <Link
              href={`/aprender/${siguiente.node_code}`}
              className="rounded-xl border border-border p-4 text-right transition hover:bg-surface-hover sm:col-start-2"
            >
              <span className="text-xs text-muted">Tema siguiente →</span>
              <span className="mt-0.5 block font-medium">{siguiente.node_name}</span>
              <span className="mt-0.5 block text-xs text-muted">{siguiente.axis_label}</span>
            </Link>
          )}
        </nav>
      )}

      <p className="mt-6 text-center text-sm">
        <Link
          href={conSesion ? "/arbol" : "/aprender"}
          className="text-muted underline-offset-4 hover:text-foreground hover:underline"
        >
          {conSesion ? "← Volver al árbol" : "← Ver todas las lecciones"}
        </Link>
      </p>
    </article>
  );
}
