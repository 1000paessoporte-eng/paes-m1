"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { agendarEnsayo, borrarEnsayoProgramado, type EnsayoProgramado, type Subject } from "@/lib/api";
import { getClientToken } from "@/lib/auth";
import { COLOR_PRUEBA, NOMBRE_CORTO } from "@/lib/colores-prueba";

/**
 * Los ensayos que el profesor deja agendados.
 *
 * No bloquea ni obliga: es una fecha y un compromiso. Un ensayo que se cierra
 * a una hora exacta necesitaría manejar zonas horarias, cortes de luz y
 * reclamos, y para un curso de treinta personas la lista de quién cumplió
 * resuelve el mismo problema sin nada de eso.
 */

const PRUEBAS: Subject[] = ["lectora", "m1", "m2", "ciencias", "historia"];

const FECHA_LARGA = new Intl.DateTimeFormat("es-CL", {
  weekday: "long",
  day: "numeric",
  month: "long",
});

/** Hoy, en ISO, para el mínimo del campo de fecha. */
function hoyISO(): string {
  return new Date().toISOString().slice(0, 10);
}

/** La fecha llega como "2026-09-12" y hay que leerla como día local.
 *
 * `new Date("2026-09-12")` la interpreta como medianoche UTC, que en Chile es
 * el día ANTERIOR a las 21:00: el ensayo del viernes aparecía como jueves. */
function comoFechaLocal(iso: string): Date {
  const [a, m, d] = iso.split("-").map(Number);
  return new Date(a, m - 1, d);
}

export function AgendaEnsayos({
  ensayos,
  puedeAgendar,
}: {
  ensayos: EnsayoProgramado[];
  puedeAgendar: boolean;
}) {
  const router = useRouter();
  const quieto = useReducedMotion();
  const [abierto, setAbierto] = useState(false);
  const [titulo, setTitulo] = useState("");
  const [subject, setSubject] = useState<Subject>("m1");
  const [fecha, setFecha] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // El día de hoy se fija UNA vez, al montar. Leer el reloj en cada render
  // daría un valor distinto cada vez, y React lo prohíbe con razón: nada de lo
  // que se dibuja acá cambia porque pasen tres segundos.
  const [hoy] = useState(hoyISO);

  async function agendar(e: React.FormEvent) {
    e.preventDefault();
    setEnviando(true);
    setError(null);
    try {
      await agendarEnsayo({ titulo, subject, fecha }, getClientToken() ?? undefined);
      setTitulo("");
      setFecha("");
      setAbierto(false);
      router.refresh();
    } catch {
      setError("No pudimos agendar el ensayo. Intenta de nuevo.");
    } finally {
      setEnviando(false);
    }
  }

  async function borrar(id: number) {
    try {
      await borrarEnsayoProgramado(id, getClientToken() ?? undefined);
      router.refresh();
    } catch {
      setError("No pudimos borrar ese ensayo.");
    }
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-sm font-semibold tracking-wide text-muted uppercase">
          Ensayos del curso
        </h2>
        {puedeAgendar && (
          <button
            type="button"
            onClick={() => setAbierto((v) => !v)}
            className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium hover:border-border-strong"
          >
            {abierto ? "Cancelar" : "Agendar uno"}
          </button>
        )}
      </div>

      <AnimatePresence initial={false}>
        {abierto && (
          <motion.form
            onSubmit={agendar}
            initial={quieto ? { opacity: 0 } : { opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={quieto ? { opacity: 0 } : { opacity: 0, height: 0 }}
            transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden"
          >
            <div className="mt-3 space-y-3 rounded-2xl border border-border bg-surface p-5">
              <div>
                <label htmlFor="titulo-ensayo" className="text-sm font-medium">
                  Cómo lo van a reconocer
                </label>
                <input
                  id="titulo-ensayo"
                  value={titulo}
                  onChange={(e) => setTitulo(e.target.value)}
                  maxLength={160}
                  placeholder="Ensayo 1 de M1"
                  className="mt-1.5 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:border-accent focus:outline-none"
                />
              </div>

              <fieldset>
                <legend className="text-sm font-medium">Prueba</legend>
                <div className="mt-1.5 flex flex-wrap gap-2">
                  {PRUEBAS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setSubject(s)}
                      aria-pressed={subject === s}
                      className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors ${
                        subject === s ? "text-foreground" : "border-border text-muted"
                      }`}
                      style={
                        subject === s
                          ? {
                              borderColor: COLOR_PRUEBA[s],
                              backgroundColor: `color-mix(in srgb, ${COLOR_PRUEBA[s]} 12%, transparent)`,
                            }
                          : undefined
                      }
                    >
                      {NOMBRE_CORTO[s]}
                    </button>
                  ))}
                </div>
              </fieldset>

              <div>
                <label htmlFor="fecha-ensayo" className="text-sm font-medium">
                  Para cuándo
                </label>
                <input
                  id="fecha-ensayo"
                  type="date"
                  value={fecha}
                  min={hoy}
                  onChange={(e) => setFecha(e.target.value)}
                  className="mt-1.5 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:border-accent focus:outline-none"
                />
              </div>

              <button
                type="submit"
                disabled={titulo.trim().length < 2 || !fecha || enviando}
                className="btn-glow w-full rounded-lg px-4 py-2.5 text-sm font-medium text-accent-foreground disabled:cursor-not-allowed disabled:opacity-40"
              >
                {enviando ? "Agendando…" : "Agendar"}
              </button>
            </div>
          </motion.form>
        )}
      </AnimatePresence>

      {error && (
        <p role="alert" className="mt-3 text-sm text-danger">
          {error}
        </p>
      )}

      {ensayos.length === 0 ? (
        <p className="mt-3 rounded-2xl border border-dashed border-border p-6 text-sm text-muted">
          {puedeAgendar
            ? "No hay ensayos agendados. El primero le da al curso una fecha concreta a la que llegar."
            : "Tu profesor todavía no agenda ensayos."}
        </p>
      ) : (
        <ul className="mt-3 divide-y divide-border rounded-2xl border border-border bg-surface">
          <AnimatePresence initial={false}>
            {ensayos.map((e) => {
              const dia = comoFechaLocal(e.fecha);
              const pasado = dia < comoFechaLocal(hoy);
              return (
                <motion.li
                  key={e.id}
                  layout={!quieto}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.24 }}
                  className="flex items-center gap-3 p-3"
                >
                  {/* La franja de color dice de qué prueba es sin leer nada:
                      es el mismo código de color del árbol y del selector. */}
                  <span
                    aria-hidden
                    className="h-9 w-1 shrink-0 rounded-full"
                    style={{ backgroundColor: COLOR_PRUEBA[e.subject] }}
                  />
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-medium">{e.titulo}</p>
                    <p className="text-xs text-muted">
                      {NOMBRE_CORTO[e.subject]} · {FECHA_LARGA.format(dia)}
                      {pasado && " · ya pasó"}
                    </p>
                  </div>

                  {e.rendido_por != null && (
                    <span className="shrink-0 text-xs tabular-nums text-muted">
                      {e.rendido_por === 0
                        ? "nadie aún"
                        : e.rendido_por === 1
                          ? "1 lo rindió"
                          : `${e.rendido_por} lo rindieron`}
                    </span>
                  )}

                  {e.lo_rendi != null &&
                    (e.lo_rendi ? (
                      <span className="shrink-0 text-xs font-medium text-success">
                        Rendido
                      </span>
                    ) : (
                      <a
                        href={`/examen?subject=${e.subject}`}
                        className="shrink-0 rounded-lg border border-border px-3 py-1.5 text-xs font-medium hover:border-border-strong"
                      >
                        Rendirlo
                      </a>
                    ))}

                  {puedeAgendar && (
                    <button
                      type="button"
                      onClick={() => borrar(e.id)}
                      aria-label={`Borrar ${e.titulo}`}
                      className="shrink-0 rounded-lg px-2 py-1 text-xs text-muted hover:text-danger"
                    >
                      Borrar
                    </button>
                  )}
                </motion.li>
              );
            })}
          </AnimatePresence>
        </ul>
      )}
    </div>
  );
}
