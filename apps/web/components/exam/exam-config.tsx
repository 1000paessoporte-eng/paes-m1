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
 * Las cinco pruebas PAES. Todas tienen banco, aunque de tamaños muy distintos:
 * matemática es la más grande y las otras tres van creciendo.
 */
const PRUEBAS: { id: Subject; nombre: string; disponible: boolean }[] = [
  { id: "lectora", nombre: "Competencia Lectora", disponible: true },
  { id: "m1", nombre: "Competencia Matemática M1", disponible: true },
  { id: "m2", nombre: "Competencia Matemática M2", disponible: true },
  { id: "historia", nombre: "Historia y Ciencias Sociales", disponible: true },
  { id: "ciencias", nombre: "Ciencias", disponible: true },
];

export const SUBJECT_LABELS: Record<Subject, string> = {
  lectora: "Competencia Lectora",
  m1: "Competencia Matemática M1",
  m2: "Competencia Matemática M2",
  ciencias: "Ciencias",
  historia: "Historia y Ciencias Sociales",
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

/**
 * Un paso de la configuración: número, título y su contenido.
 *
 * Existe para que los cuatro pasos se vean iguales y ocupen lo mismo. Antes
 * cada sección repetía su encabezado con clases propias y ninguno quedaba
 * alineado con el siguiente.
 */
function Paso({
  numero,
  titulo,
  ayuda,
  children,
}: {
  numero: number;
  titulo: string;
  ayuda?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mb-6">
      <div className="mb-3 flex items-baseline gap-2">
        <span
          className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-surface-hover text-xs font-bold tabular-nums text-muted"
          aria-hidden
        >
          {numero}
        </span>
        <h2 className="font-semibold tracking-tight">{titulo}</h2>
        {ayuda && <span className="text-xs text-muted">{ayuda}</span>}
      </div>
      {children}
    </section>
  );
}

interface Props {
  optionsBySubject: Record<Subject, ExamOptions>;
  repasoBySubject: Record<Subject, Repaso>;
  ensayosRendidos: number;
  //: Cuota del mes cuando el plan la tiene. `null` = sin límite.
  cuota?: { usados: number; limite: number | null; activa: boolean } | null;
  resumable: { attemptId: number; subject: Subject } | null;
  errorMsg: string | null;
  onComenzar: (config: ExamConfig) => void;
  onContinuar: () => void;
}

export function ExamConfigScreen({
  optionsBySubject,
  repasoBySubject,
  ensayosRendidos,
  cuota,
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
    // El pb en móvil reserva el alto de la barra de resumen, que va fija
    // sobre el contenido. En escritorio la barra no es fija y no hace falta.
    <div className="mx-auto max-w-3xl pb-36 sm:pb-0">
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
      {/* Cada chip trae su cantidad de preguntas disponibles: sin ese número
          hay que elegir una prueba, mirar más abajo y volver, para descubrir
          que su banco no alcanzaba. */}
      <Paso numero={1} titulo="¿Qué prueba?">
        <div className="flex flex-wrap gap-2">
          {PRUEBAS.map((prueba) => {
            const activa = prueba.disponible && prueba.id === subject;
            const disponibles = optionsBySubject[prueba.id].total_available;
            return (
              <button
                key={prueba.id}
                type="button"
                disabled={!prueba.disponible}
                aria-pressed={activa}
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
                    : "border-border bg-surface hover:border-border-strong"
                )}
              >
                {prueba.nombre}
                <span className={activa ? "opacity-80" : "text-muted"}>
                  {" "}
                  ({disponibles})
                </span>
              </button>
            );
          })}
        </div>
      </Paso>

      {/* ── Ejes temáticos ──────────────────────────────────────────── */}
      <Paso
        numero={2}
        titulo="¿Qué temas?"
        ayuda="Elige uno o varios para reforzar algo puntual."
      >
        <div className="flex flex-wrap gap-2">
          {/* "Todos" es un botón y no la ausencia de selección: el estado por
              defecto tiene que verse elegido, no vacío. */}
          <button
            type="button"
            onClick={() => setEjes([])}
            aria-pressed={ejes.length === 0}
            className={cn(
              "rounded-full border px-3.5 py-1.5 text-sm font-medium transition",
              ejes.length === 0
                ? "border-accent bg-accent text-accent-foreground"
                : "border-border bg-surface hover:border-border-strong"
            )}
          >
            Todos los temas
            <span className={ejes.length === 0 ? "opacity-80" : "text-muted"}>
              {" "}
              ({options.total_available})
            </span>
          </button>
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
      </Paso>

      {/* ── Formato del ensayo ──────────────────────────────────────── */}
      <Paso numero={3} titulo="¿Cuántas preguntas?">
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
                    ? `${f.detalle} · ${formatearDuracionLarga(
                        options.seconds_per_question * f.cantidad * FACTOR_RITMO[ritmo]
                      )}`
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
              Es lo que hay en el banco con los temas que elegiste ·{" "}
              {formatearDuracionLarga(
                options.seconds_per_question * maxDisponible * FACTOR_RITMO[ritmo]
              )}
            </span>
          </button>
        )}
      </Paso>

      {/* ── Tiempo ──────────────────────────────────────────────────── */}
      {/* El estudiante elige TIEMPO, no "ritmo": cada opción muestra los
          minutos que va a durar su ensayo, que es la decisión real. El nombre
          del ritmo pasa a ser la explicación, no la etiqueta. */}
      <Paso numero={4} titulo="¿Con cuánto tiempo?">
        <div className="grid gap-2 sm:grid-cols-3">
          {RITMOS.map((r) => {
            const minutos = formatearDuracionLarga(
              options.seconds_per_question * cantidadEfectiva * FACTOR_RITMO[r]
            );
            return (
              <button
                key={r}
                type="button"
                onClick={() => setRitmo(r)}
                aria-pressed={ritmo === r}
                className={cn(
                  "rounded-lg border p-3 text-left text-sm transition",
                  ritmo === r
                    ? "border-accent bg-accent/5 ring-1 ring-accent"
                    : "border-border bg-surface hover:border-border-strong"
                )}
              >
                <span className="flex items-baseline gap-2">
                  <span className="text-lg font-bold tabular-nums">{minutos}</span>
                  <span className="text-xs font-semibold capitalize text-muted">
                    {r}
                  </span>
                </span>
                <span className="mt-0.5 block text-xs text-muted">
                  {DESCRIPCION_RITMO[r]}
                </span>
              </button>
            );
          })}
        </div>
      </Paso>

      {/* ── Resumen y comienzo ──────────────────────────────────────── */}
      {/* Pegado al borde inferior: el resumen cambia con cada elección, y si
          hay que bajar hasta el final para verlo, nadie relaciona lo que tocó
          con lo que salió. */}
      {/* Fija solo en móvil: ahí la pantalla es corta y el resumen queda
          fuera de vista mientras se elige. En escritorio todo entra junto y
          una barra flotante solo taparía opciones. */}
      <div className="glass fixed inset-x-0 bottom-0 z-20 border-t border-border px-4 py-4 sm:static sm:mt-2 sm:rounded-xl sm:border sm:bg-surface sm:px-5">
        <div className="flex items-baseline justify-between gap-3">
          {/* En móvil el resumen va en una línea. El nombre largo de la prueba
              se omite ahí: ya está elegido y visible más arriba, y en dos
              líneas la barra crecía tanto que tapaba las opciones. */}
          <span className="min-w-0 truncate text-sm text-muted sm:text-base">
            <strong className="text-foreground tabular-nums">
              {cantidadEfectiva}
            </strong>{" "}
            preguntas
            <span className="hidden sm:inline">
              {" "}
              de{" "}
              <strong className="text-foreground">
                {PRUEBAS.find((p) => p.id === subject)?.nombre}
              </strong>
            </span>
            {ejes.length > 0 && (
              <span>
                {" "}
                · {ejes.length} {ejes.length === 1 ? "tema" : "temas"}
              </span>
            )}
          </span>
          <span className="shrink-0 text-xl font-bold tabular-nums sm:text-2xl">
            {formatearDuracionLarga(duracion)}
          </span>
        </div>
        {/* El detalle de la razón oficial se oculta en móvil: es contexto
            útil, no la decisión, y ahí compite por el espacio del botón. */}
        <p className="mt-1 hidden text-sm text-muted sm:block">
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
          className="btn-glow mt-2.5 w-full rounded-lg px-4 py-3 font-semibold text-accent-foreground sm:mt-3"
        >
          Comenzar ensayo
        </button>
      </div>

      {cuota?.limite != null && (() => {
        const restantes = Math.max(0, cuota.limite - cuota.usados);
        const sinCupo = restantes === 0;
        return (
          <div
            className={
              "mt-4 rounded-lg border p-3 text-center text-xs leading-relaxed " +
              (sinCupo
                ? "border-accent-warm/40 bg-accent-warm/5"
                : "border-border")
            }
          >
            {sinCupo ? (
              <>
                <strong className="text-accent-warm-strong">
                  Usaste tus {cuota.limite} ensayos de este mes.
                </strong>{" "}
                {cuota.activa ? (
                  <>
                    Con el plan Pro son ilimitados.{" "}
                    <Link href="/planes" className="font-medium text-accent hover:underline">
                      Ver planes
                    </Link>
                  </>
                ) : (
                  "Por ahora puedes seguir rindiendo igual."
                )}
              </>
            ) : (
              <>
                Te quedan <strong>{restantes}</strong> de {cuota.limite} ensayos
                este mes en el plan Gratis.
              </>
            )}
          </div>
        );
      })()}

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
