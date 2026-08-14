"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { cn } from "@paes-m1/utils";
import type { ExamConfig, ExamOptions, Pace, Repaso, Subject } from "@/lib/api";
import { diasHastaPaes } from "@/lib/paes-fecha";

/**
 * Formatos de ensayo. 65 es la prueba oficial completa, 34 la mitad y 20 un
 * ensayo corto de entrenamiento.
 */
const FORMATOS = [
  { cantidad: 65, nombre: "Completo", detalle: "La prueba oficial entera" },
  { cantidad: 34, nombre: "Medio", detalle: "La mitad de la prueba" },
  { cantidad: 20, nombre: "Corto", detalle: "Para una sesión rápida" },
] as const;

/**
 * Pruebas PAES. Competencia Lectora, M1 y M2 ya tienen banco; las demás se muestran
 * para que quede claro que la plataforma las va a cubrir, pero deshabilitadas
 * hasta que tengan contenido.
 */
const PRUEBAS: { id: Subject | "historia" | "ciencias"; nombre: string; disponible: boolean }[] = [
  { id: "lectora", nombre: "Competencia Lectora", disponible: true },
  { id: "m1", nombre: "Competencia Matemática M1", disponible: true },
  { id: "m2", nombre: "Competencia Matemática M2", disponible: true },
  { id: "historia", nombre: "Historia y Ciencias Sociales", disponible: false },
  { id: "ciencias", nombre: "Ciencias", disponible: false },
];

export const SUBJECT_LABELS: Record<Subject, string> = {
  lectora: "Competencia Lectora",
  m1: "Competencia Matemática M1",
  m2: "Competencia Matemática M2",
};

const RITMOS: Pace[] = ["oficial", "exigente", "relajado"];

const DESCRIPCION_RITMO: Record<Pace, string> = {
  oficial: "Misma proporción de tiempo que la prueba real",
  exigente: "20% menos de tiempo, para entrenar bajo presión",
  relajado: "25% más de tiempo, para estudiar con calma",
};

const FACTOR_RITMO: Record<Pace, number> = {
  oficial: 1,
  exigente: 0.8,
  relajado: 1.25,
};

/** Formatea una duración en segundos de forma legible ("1 h 37 min"). */
function formatearDuracionLarga(segundos: number): string {
  const totalMin = Math.round(segundos / 60);
  const h = Math.floor(totalMin / 60);
  const m = totalMin % 60;
  if (h === 0) return `${m} min`;
  if (m === 0) return `${h} h`;
  return `${h} h ${m} min`;
}

interface Props {
  optionsBySubject: Record<Subject, ExamOptions>;
  repasoBySubject: Record<Subject, Repaso>;
  ensayosRendidos: number;
  resumable: { attemptId: number; subject: Subject } | null;
  errorMsg: string | null;
  onComenzar: (config: ExamConfig) => void;
  onContinuar: () => void;
}

export function ExamConfigScreen({
  optionsBySubject,
  repasoBySubject,
  ensayosRendidos,
  resumable,
  errorMsg,
  onComenzar,
  onContinuar,
}: Props) {
  const [subject, setSubject] = useState<Subject>("m1");
  const [cantidad, setCantidad] = useState(20);
  const [ritmo, setRitmo] = useState<Pace>("oficial");
  const [ejes, setEjes] = useState<string[]>([]);
  const dias = diasHastaPaes();

  const options = optionsBySubject[subject];
  const repaso = repasoBySubject[subject];

  const maxDisponible = useMemo(() => {
    if (ejes.length === 0) return options.total_available;
    return options.axes
      .filter((a) => ejes.includes(a.axis))
      .reduce((acc, a) => acc + a.available, 0);
  }, [ejes, options]);

  // Si el banco filtrado tiene menos preguntas de las pedidas, el ensayo usa
  // todas las que haya. Se refleja en pantalla para que no sea una sorpresa.
  const cantidadEfectiva = Math.max(1, Math.min(cantidad, maxDisponible));
  const hayFormatoDisponible = FORMATOS.some((f) => f.cantidad <= maxDisponible);
  const duracion = Math.round(
    options.seconds_per_question * cantidadEfectiva * FACTOR_RITMO[ritmo]
  );
  const segPregunta = options.seconds_per_question;

  function alternarEje(eje: string) {
    setEjes((actuales) =>
      actuales.includes(eje) ? actuales.filter((e) => e !== eje) : [...actuales, eje]
    );
  }

  return (
    <div className="mx-auto max-w-3xl">
      <header className="mb-10">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="text-sm font-medium text-accent">
            Preparación PAES · Admisión 2027
          </p>
          {dias !== null && (
            <span className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted">
              Faltan <strong className="text-foreground">{dias}</strong>{" "}
              {dias === 1 ? "día" : "días"} para la PAES
            </span>
          )}
        </div>
        <h1 className="mt-1 text-3xl font-bold tracking-tight sm:text-4xl">
          Modo Ensayo
        </h1>
        <p className="mt-3 text-muted">
          Arma un ensayo a tu medida, con el tiempo proporcional al de la prueba
          real. Al terminar obtienes puntaje estimado, resumen por eje y la
          explicación de cada respuesta.
        </p>
      </header>

      {repaso.has_data && (
        <div className="mb-8 flex flex-wrap items-center justify-between gap-3 rounded-xl border border-accent/40 bg-accent/5 p-4">
          <div>
            <p className="text-sm font-medium">Ensayo de repaso</p>
            <p className="mt-0.5 text-sm text-muted">
              Enfocado en donde peor rindes:{" "}
              <strong className="text-foreground">
                {repaso.axis_labels.join(" y ")}
              </strong>
              .
            </p>
          </div>
          <button
            type="button"
            onClick={() =>
              onComenzar({
                subject,
                question_count: 20,
                pace: "oficial",
                axes: repaso.axes,
              })
            }
            className="btn-glow shrink-0 rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground"
          >
            Empezar ahora
          </button>
        </div>
      )}

      {resumable && (
        <div className="mb-8 rounded-xl border border-accent/40 bg-accent/5 p-4">
          <p className="text-sm">
            Tienes un ensayo de{" "}
            <strong>{SUBJECT_LABELS[resumable.subject]}</strong> en curso sin
            finalizar. Al continuar retomas justo donde quedaste
            {resumable.subject !== subject && ", y vuelves a esa prueba"}.
          </p>
          <button
            type="button"
            onClick={onContinuar}
            className="btn-glow mt-3 rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground"
          >
            Continuar ensayo de {SUBJECT_LABELS[resumable.subject]}
          </button>
        </div>
      )}

      {errorMsg && (
        <p className="mb-6 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">
          {errorMsg}
        </p>
      )}

      {/* ── Prueba ──────────────────────────────────────────────────── */}
      <section className="mb-8">
        <h2 className="mb-1 text-sm font-semibold tracking-wide text-muted uppercase">
          1. Prueba
        </h2>
        <p className="mb-3 text-sm text-muted">
          Vamos a cubrir las cinco pruebas PAES. Hoy Competencia Matemática M1
          y M2 tienen ensayos disponibles.
        </p>
        <div className="flex flex-wrap gap-2">
          {PRUEBAS.map((prueba) => {
            const activa = prueba.disponible && prueba.id === subject;
            return (
              <button
                key={prueba.id}
                type="button"
                disabled={!prueba.disponible}
                aria-pressed={activa}
                title={prueba.disponible ? undefined : "Próximamente"}
                onClick={() => {
                  if (prueba.disponible) {
                    setSubject(prueba.id as Subject);
                    setEjes([]);
                  }
                }}
                className={cn(
                  "rounded-full border px-3.5 py-1.5 text-sm transition disabled:cursor-not-allowed",
                  activa
                    ? "border-accent bg-accent text-accent-foreground"
                    : prueba.disponible
                      ? "border-border bg-surface hover:border-border-strong"
                      : "border-border bg-surface text-muted opacity-60"
                )}
              >
                {prueba.nombre}
                {!prueba.disponible && (
                  <span className="ml-1.5 text-xs">· Próximamente</span>
                )}
              </button>
            );
          })}
        </div>
      </section>

      {/* ── Ejes temáticos ──────────────────────────────────────────── */}
      <section className="mb-8">
        <h2 className="mb-1 text-sm font-semibold tracking-wide text-muted uppercase">
          2. Ejes temáticos
        </h2>
        <p className="mb-3 text-sm text-muted">
          Sin selección se incluyen todos, repartidos proporcionalmente.
        </p>
        <div className="flex flex-wrap gap-2">
          {options.axes.map((eje) => {
            const activo = ejes.includes(eje.axis);
            return (
              <button
                key={eje.axis}
                type="button"
                onClick={() => alternarEje(eje.axis)}
                disabled={eje.available === 0}
                aria-pressed={activo}
                className={cn(
                  "rounded-full border px-3.5 py-1.5 text-sm transition disabled:cursor-not-allowed disabled:opacity-40",
                  activo
                    ? "border-accent bg-accent text-accent-foreground"
                    : "border-border bg-surface hover:border-border-strong"
                )}
              >
                {eje.label}
                <span className={activo ? "opacity-80" : "text-muted"}>
                  {" "}
                  ({eje.available})
                </span>
              </button>
            );
          })}
        </div>
      </section>

      {/* ── Formato del ensayo ──────────────────────────────────────── */}
      <section className="mb-8">
        <h2 className="mb-3 text-sm font-semibold tracking-wide text-muted uppercase">
          3. ¿Cuántas preguntas?
        </h2>
        <div className="grid gap-2 sm:grid-cols-3">
          {FORMATOS.map((f) => {
            const alcanza = f.cantidad <= maxDisponible;
            return (
              <button
                key={f.cantidad}
                type="button"
                onClick={() => setCantidad(f.cantidad)}
                disabled={!alcanza}
                aria-pressed={cantidad === f.cantidad}
                className={cn(
                  "rounded-lg border p-3 text-left transition disabled:cursor-not-allowed disabled:opacity-50",
                  cantidad === f.cantidad && alcanza
                    ? "border-accent bg-accent/5 ring-1 ring-accent"
                    : "border-border bg-surface hover:border-border-strong"
                )}
              >
                <span className="flex items-baseline gap-1.5">
                  <span className="text-2xl font-bold tabular-nums">{f.cantidad}</span>
                  <span className="text-sm font-semibold">{f.nombre}</span>
                </span>
                <span className="mt-0.5 block text-xs text-muted">
                  {alcanza
                    ? f.detalle
                    : `Faltan ${f.cantidad - maxDisponible} preguntas en el banco`}
                </span>
              </button>
            );
          })}
        </div>

        {/* Con pocos ejes elegidos ningún formato alcanza; igual debe poder
            rendirse un ensayo con lo que haya. */}
        {!hayFormatoDisponible && maxDisponible > 0 && (
          <button
            type="button"
            onClick={() => setCantidad(maxDisponible)}
            aria-pressed={cantidad === maxDisponible}
            className={cn(
              "mt-2 w-full rounded-lg border p-3 text-left transition",
              cantidad === maxDisponible
                ? "border-accent bg-accent/5 ring-1 ring-accent"
                : "border-border bg-surface hover:border-border-strong"
            )}
          >
            <span className="flex items-baseline gap-1.5">
              <span className="text-2xl font-bold tabular-nums">{maxDisponible}</span>
              <span className="text-sm font-semibold">Todas las disponibles</span>
            </span>
            <span className="mt-0.5 block text-xs text-muted">
              Es lo que hay en el banco con los ejes que elegiste
            </span>
          </button>
        )}
      </section>

      {/* ── Ritmo ───────────────────────────────────────────────────── */}
      <section className="mb-8">
        <h2 className="mb-3 text-sm font-semibold tracking-wide text-muted uppercase">
          4. Ritmo
        </h2>
        <div className="grid gap-2 sm:grid-cols-3">
          {RITMOS.map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setRitmo(r)}
              aria-pressed={ritmo === r}
              className={cn(
                "rounded-lg border p-3 text-left text-sm transition",
                ritmo === r
                  ? "border-accent bg-accent/5"
                  : "border-border bg-surface hover:border-border-strong"
              )}
            >
              <span className="block font-semibold capitalize">{r}</span>
              <span className="mt-0.5 block text-xs text-muted">
                {DESCRIPCION_RITMO[r]}
              </span>
            </button>
          ))}
        </div>
      </section>

      {/* ── Resumen y comienzo ──────────────────────────────────────── */}
      <div className="rounded-xl border border-border bg-surface p-5">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <span className="text-muted">
            {cantidadEfectiva} preguntas de{" "}
            <strong className="text-foreground">
              {PRUEBAS.find((p) => p.id === subject)?.nombre}
            </strong>
          </span>
          <span className="text-2xl font-bold tabular-nums">
            {formatearDuracionLarga(duracion)}
          </span>
        </div>
        <p className="mt-1 text-sm text-muted">
          La prueba oficial da {Math.floor(segPregunta / 60)} min{" "}
          {Math.round(segPregunta % 60)} s por pregunta
          {ritmo !== "oficial" && ", y este ritmo lo ajusta"}.
        </p>

        <button
          type="button"
          onClick={() =>
            onComenzar({
              subject,
              question_count: cantidadEfectiva,
              pace: ritmo,
              axes: ejes,
            })
          }
          className="btn-glow mt-4 w-full rounded-lg px-4 py-3 font-semibold text-accent-foreground"
        >
          Comenzar ensayo
        </button>
      </div>

      {ensayosRendidos > 0 && (
        <Link
          href="/historial"
          className="mt-4 block rounded-lg border border-border px-4 py-2.5 text-center text-sm font-medium transition hover:bg-surface-hover"
        >
          Ver mi progreso ({ensayosRendidos}{" "}
          {ensayosRendidos === 1 ? "ensayo rendido" : "ensayos rendidos"})
        </Link>
      )}

      <footer className="mt-10 border-t border-border pt-6 text-xs leading-relaxed text-muted">
        <p>
          El puntaje mostrado es una estimación referencial: el puntaje real
          depende de la forma rendida y del proceso de admisión.
        </p>
      </footer>
    </div>
  );
}
