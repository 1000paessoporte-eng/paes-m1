"use client";

import { useState } from "react";
import type { Onboarding } from "@/lib/api";
import { guardarOnboarding } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

/**
 * Lo que el estudiante respondió en el cuestionario, editable.
 *
 * Va en el perfil porque una respuesta que no se puede cambiar es una trampa:
 * quien en marzo dijo que rendía solo M1 y en agosto agrega Ciencias tiene que
 * poder decirlo, y las horas de estudio cambian con las pruebas del colegio.
 *
 * Sin esta pantalla, el cuestionario sería un formulario de una sola vez cuyas
 * respuestas envejecen sin que nadie las pueda corregir.
 */

const PRUEBAS = [
  { id: "lectora", label: "Competencia Lectora" },
  { id: "m1", label: "Matemática M1" },
  { id: "m2", label: "Matemática M2" },
  { id: "ciencias", label: "Ciencias" },
  { id: "historia", label: "Historia y Cs. Sociales" },
] as const;

const CURSOS = [
  { id: "tercero", label: "3° medio" },
  { id: "cuarto", label: "4° medio" },
  { id: "egresado", label: "Ya egresé" },
] as const;

export function MisDatos({ inicial }: { inicial: Onboarding }) {
  const [pruebas, setPruebas] = useState<string[]>(inicial.pruebas_objetivo ?? []);
  const [curso, setCurso] = useState<string | null>(inicial.curso ?? null);
  const [primeraVez, setPrimeraVez] = useState<boolean | null>(
    inicial.primera_vez ?? null
  );
  const [puntaje, setPuntaje] = useState(
    inicial.puntaje_anterior ? String(inicial.puntaje_anterior) : ""
  );
  const [horas, setHoras] = useState(
    inicial.horas_semana != null ? String(inicial.horas_semana) : ""
  );
  const [guardando, setGuardando] = useState(false);
  const [guardado, setGuardado] = useState(false);

  async function guardar() {
    setGuardando(true);
    setGuardado(false);
    try {
      await guardarOnboarding(
        {
          pruebas_objetivo: pruebas,
          curso,
          primera_vez: primeraVez,
          puntaje_anterior: puntaje ? Number(puntaje) : null,
          horas_semana: horas ? Number(horas) : null,
        },
        getClientToken() ?? undefined
      );
      setGuardado(true);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <section className="card-panel p-5" aria-labelledby="h-datos">
      <h2 id="h-datos" className="font-semibold tracking-tight">
        Mi preparación
      </h2>
      <p className="mt-1 text-xs leading-relaxed text-muted">
        Con esto la plataforma decide qué prueba abrir y de qué tamaño hacerte el
        plan de estudio. Puedes cambiarlo cuando quieras.
      </p>

      <fieldset className="mt-4">
        <legend className="text-xs font-medium text-muted">
          Pruebas que voy a rendir
        </legend>
        <div className="mt-2 flex flex-wrap gap-2">
          {PRUEBAS.map((p) => {
            const activa = pruebas.includes(p.id);
            return (
              <button
                key={p.id}
                type="button"
                aria-pressed={activa}
                onClick={() =>
                  setPruebas((a) =>
                    a.includes(p.id) ? a.filter((x) => x !== p.id) : [...a, p.id]
                  )
                }
                className={
                  "rounded-full border px-3 py-1.5 text-xs font-medium transition " +
                  (activa
                    ? "border-accent bg-accent text-accent-foreground"
                    : "border-border hover:border-border-strong")
                }
              >
                {p.label}
              </button>
            );
          })}
        </div>
        {pruebas.length > 0 && (
          <p className="mt-2 text-xs text-muted">
            El árbol y los ensayos abren en{" "}
            {PRUEBAS.find((p) => p.id === pruebas[0])?.label}.
          </p>
        )}
      </fieldset>

      <fieldset className="mt-4">
        <legend className="text-xs font-medium text-muted">Curso</legend>
        <div className="mt-2 flex flex-wrap gap-2">
          {CURSOS.map((c) => (
            <button
              key={c.id}
              type="button"
              aria-pressed={curso === c.id}
              onClick={() => setCurso(c.id)}
              className={
                "rounded-full border px-3 py-1.5 text-xs font-medium transition " +
                (curso === c.id
                  ? "border-accent bg-accent text-accent-foreground"
                  : "border-border hover:border-border-strong")
              }
            >
              {c.label}
            </button>
          ))}
        </div>
      </fieldset>

      <fieldset className="mt-4">
        <legend className="text-xs font-medium text-muted">
          ¿Ya habías rendido la PAES?
        </legend>
        <div className="mt-2 flex flex-wrap items-center gap-2">
          {[
            { v: true, label: "Es mi primera vez" },
            { v: false, label: "Ya la rendí antes" },
          ].map((o) => (
            <button
              key={String(o.v)}
              type="button"
              aria-pressed={primeraVez === o.v}
              onClick={() => setPrimeraVez(o.v)}
              className={
                "rounded-full border px-3 py-1.5 text-xs font-medium transition " +
                (primeraVez === o.v
                  ? "border-accent bg-accent text-accent-foreground"
                  : "border-border hover:border-border-strong")
              }
            >
              {o.label}
            </button>
          ))}
          {primeraVez === false && (
            <input
              inputMode="numeric"
              value={puntaje}
              onChange={(e) => setPuntaje(e.target.value.replace(/\D/g, "").slice(0, 4))}
              placeholder="Puntaje anterior"
              aria-label="Tu mejor puntaje anterior"
              className="w-36 rounded-lg border border-border bg-background px-3 py-1.5 text-sm tabular-nums"
            />
          )}
        </div>
      </fieldset>

      <label className="mt-4 block">
        <span className="block text-xs font-medium text-muted">
          Horas de estudio por semana
        </span>
        <input
          inputMode="numeric"
          value={horas}
          onChange={(e) => setHoras(e.target.value.replace(/\D/g, "").slice(0, 2))}
          placeholder="5"
          className="mt-1 w-24 rounded-lg border border-border bg-background px-3 py-2 tabular-nums"
        />
        <span className="mt-1 block text-xs text-muted">
          Dimensiona el plan de Mi meta: con menos horas se proponen menos temas,
          pero el ensayo se mantiene.
        </span>
      </label>

      <div className="mt-5 flex items-center gap-3">
        <button
          type="button"
          onClick={guardar}
          disabled={guardando}
          className="rounded-lg border border-border px-4 py-2 text-sm font-medium transition-colors hover:bg-surface-hover disabled:opacity-50"
        >
          {guardando ? "Guardando…" : "Guardar"}
        </button>
        {guardado && <span className="text-sm text-success">Guardado</span>}
      </div>
    </section>
  );
}
