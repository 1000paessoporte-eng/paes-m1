"use client";

import Link from "next/link";
import { useState } from "react";
import { cn } from "@paes-m1/utils";
import { CompartirResultado } from "@/components/exam/compartir-resultado";
import { TextoRico } from "@/components/texto-rico";
import type { BreakdownItem, ExamResult, ExamReview, ReviewQuestion } from "@/lib/api";
import { formatearTiempo } from "@/lib/tiempo";

type Filtro = "todas" | "incorrectas" | "omitidas";

/**
 * Clasifica un puntaje en una etiqueta cualitativa, para dar contexto
 * inmediato al número.
 */
function nivelDePuntaje(puntaje: number): { etiqueta: string; clase: string } {
  if (puntaje >= 900) return { etiqueta: "Excelente", clase: "text-success" };
  if (puntaje >= 750) return { etiqueta: "Muy bueno", clase: "text-success" };
  if (puntaje >= 600) return { etiqueta: "Bueno", clase: "text-accent" };
  if (puntaje >= 450) return { etiqueta: "Suficiente", clase: "text-warning" };
  return { etiqueta: "Por reforzar", clase: "text-danger" };
}

/** Ejes con peor desempeño, para sugerir qué reforzar. Solo grupos con al
 *  menos 2 preguntas: un único error no permite concluir nada. */
function ejesDebiles(items: BreakdownItem[]): BreakdownItem[] {
  return items
    .filter((d) => d.total >= 2 && d.percentage < 60)
    .sort((a, b) => a.percentage - b.percentage);
}

interface Props {
  result: ExamResult;
  review: ExamReview | null;
  onNuevoEnsayo: () => void;
  /** Cómo se llama la prueba rendida. Va en la imagen que se comparte. */
  prueba: string;
}

export function ExamResults({ result, review, onNuevoEnsayo, prueba }: Props) {
  const [expandidas, setExpandidas] = useState<Set<number>>(new Set());
  const [filtro, setFiltro] = useState<Filtro>("todas");

  const nivel = nivelDePuntaje(result.estimated_score);
  const logro = result.total_questions
    ? Math.round((result.correct / result.total_questions) * 100)
    : 0;
  const debiles = ejesDebiles(result.by_axis);

  const preguntas = review?.questions ?? [];
  const preguntasFiltradas = preguntas.filter((p) => {
    if (filtro === "incorrectas") return p.answered_correctly === false;
    if (filtro === "omitidas") return p.answered_correctly === null;
    return true;
  });

  function alternar(id: number) {
    setExpandidas((prev) => {
      const nuevo = new Set(prev);
      if (nuevo.has(id)) nuevo.delete(id);
      else nuevo.add(id);
      return nuevo;
    });
  }

  return (
    <div className="mx-auto max-w-3xl">
      {/* ── Puntaje ─────────────────────────────────────────────────── */}
      <section className="rounded-2xl border border-border bg-surface p-6 text-center">
        <p className="text-sm text-muted">Puntaje estimado</p>
        <p className={cn("mt-1 text-6xl font-bold tabular-nums", nivel.clase)}>
          {result.estimated_score}
        </p>
        <p className={cn("mt-1 font-semibold", nivel.clase)}>{nivel.etiqueta}</p>
        <p className="mt-3 text-sm text-muted">
          {result.correct} de {result.total_questions} correctas ({logro}%)
        </p>

        <div className="mt-5 grid grid-cols-3 gap-2 text-sm">
          <div className="rounded-lg bg-success/10 p-3">
            <p className="text-2xl font-bold tabular-nums text-success">{result.correct}</p>
            <p className="text-success">correctas</p>
          </div>
          <div className="rounded-lg bg-danger/10 p-3">
            <p className="text-2xl font-bold tabular-nums text-danger">{result.incorrect}</p>
            <p className="text-danger">incorrectas</p>
          </div>
          <div className="rounded-lg bg-surface-hover p-3">
            <p className="text-2xl font-bold tabular-nums">{result.omitted}</p>
            <p className="text-muted">omitidas</p>
          </div>
        </div>

        <p className="mt-4 text-sm text-muted">
          Tiempo usado: {formatearTiempo(result.elapsed_seconds)} de{" "}
          {formatearTiempo(result.duration_limit_seconds)}
        </p>

        {/* Terminar un ensayo es el único momento del producto que da ganas de
            mostrarle a alguien. La imagen se arma en el navegador: el puntaje
            es dato privado y no tiene por qué existir en una URL. */}
        <div className="mt-5 flex justify-center">
          <CompartirResultado
            puntaje={result.estimated_score}
            prueba={prueba}
            correctas={result.correct}
            total={result.total_questions}
            ejes={result.by_axis}
          />
        </div>
      </section>

      {/* ── Sugerencia de refuerzo ──────────────────────────────────── */}
      {debiles.length > 0 && (
        <section className="mt-5 rounded-xl border border-warning/40 bg-warning/10 p-4">
          <h2 className="font-semibold text-warning">Qué conviene reforzar</h2>
          <p className="mt-1 text-sm">
            Tu rendimiento fue más bajo en{" "}
            {debiles.map((d, i) => (
              <span key={d.name}>
                {i > 0 && (i === debiles.length - 1 ? " y " : ", ")}
                <strong>{d.name}</strong> ({d.percentage}%)
              </span>
            ))}
            . Puedes armar un ensayo filtrando solo por{" "}
            {debiles.length === 1 ? "ese eje" : "esos ejes"}.
          </p>
        </section>
      )}

      {/* ── Desgloses ───────────────────────────────────────────────── */}
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        <Desglose titulo="Por eje temático" items={result.by_axis} />
        <Desglose titulo="Por dificultad" items={result.by_difficulty} />
      </div>

      {result.by_node.length > 0 && (
        <div className="mt-4">
          <Desglose titulo="Por nodo del árbol de habilidades" items={result.by_node} />
        </div>
      )}

      {/* ── Revisión pregunta a pregunta ────────────────────────────── */}
      {preguntas.length > 0 && (
        <section className="mt-8">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-lg font-bold">Revisión de respuestas</h2>
            <button
              type="button"
              onClick={() => setExpandidas(new Set(preguntas.map((p) => p.id)))}
              className="text-sm text-accent underline-offset-2 hover:underline"
            >
              Ver todas las resoluciones
            </button>
          </div>

          <div className="mb-4 flex flex-wrap gap-2">
            {(
              [
                ["todas", `Todas (${preguntas.length})`],
                ["incorrectas", `Incorrectas (${result.incorrect})`],
                ["omitidas", `Omitidas (${result.omitted})`],
              ] as [Filtro, string][]
            ).map(([valor, etiqueta]) => (
              <button
                key={valor}
                type="button"
                onClick={() => setFiltro(valor)}
                aria-pressed={filtro === valor}
                className={cn(
                  "rounded-full border px-3 py-1.5 text-sm transition",
                  filtro === valor
                    ? "border-accent bg-accent text-accent-foreground"
                    : "border-border text-muted hover:bg-surface-hover"
                )}
              >
                {etiqueta}
              </button>
            ))}
          </div>

          {preguntasFiltradas.length === 0 && (
            <p className="rounded-lg bg-surface p-4 text-center text-sm text-muted">
              No hay preguntas en esta categoría. ¡Buen trabajo!
            </p>
          )}

          <ol className="space-y-3">
            {preguntasFiltradas.map((pregunta) => (
              <RevisionItem
                key={pregunta.id}
                pregunta={pregunta}
                numero={preguntas.indexOf(pregunta) + 1}
                abierta={expandidas.has(pregunta.id)}
                onAlternar={() => alternar(pregunta.id)}
              />
            ))}
          </ol>
        </section>
      )}

      {/* El momento de mandar a repasar es este, no el panel de mañana: acaba
          de ver cuáles falló y todavía se acuerda de por qué. La cola se arma
          sola al abrir /repaso, así que el enlace basta: no hay nada que
          registrar acá.

          Cuenta las FALLADAS, no las omitidas: al repaso solo entran las que
          respondió mal, que son las que tienen un error que corregir. */}
      {result.incorrect > 0 && (
        <Link
          href="/repaso"
          className="mt-8 flex items-center gap-3 rounded-xl border border-accent/40 bg-accent/5 p-4 transition hover:bg-accent/10"
        >
          <span className="text-2xl font-bold text-accent tabular-nums">
            {result.incorrect}
          </span>
          <span className="min-w-0 flex-1 text-sm">
            <strong className="block">
              {result.incorrect === 1
                ? "La que fallaste ya está en tu repaso"
                : "Las que fallaste ya están en tu repaso"}
            </strong>
            <span className="text-muted">
              Vuelven con esperas cada vez más largas hasta que te salgan sin
              pensarlo.
            </span>
          </span>
          <span aria-hidden="true" className="shrink-0 text-accent">
            →
          </span>
        </Link>
      )}

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={onNuevoEnsayo}
          className="btn-glow flex-1 rounded-lg px-4 py-3 font-semibold text-accent-foreground"
        >
          Hacer otro ensayo
        </button>
        <Link
          href="/historial"
          className="flex-1 rounded-lg border border-border px-4 py-3 text-center font-medium transition hover:bg-surface-hover"
        >
          Ver mi progreso
        </Link>
      </div>
    </div>
  );
}

function RevisionItem({
  pregunta,
  numero,
  abierta,
  onAlternar,
}: {
  pregunta: ReviewQuestion;
  numero: number;
  abierta: boolean;
  onAlternar: () => void;
}) {
  const acertada = pregunta.answered_correctly === true;
  const omitida = pregunta.answered_correctly === null;
  const correcta = pregunta.alternatives.find((a) => a.is_correct);

  return (
    <li className="overflow-hidden rounded-xl border border-border bg-surface">
      <div className="p-4">
        <div className="mb-2 flex items-center gap-2">
          <span
            className={cn(
              "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold text-on-fill",
              acertada ? "bg-success" : omitida ? "bg-border-strong" : "bg-danger"
            )}
            aria-label={acertada ? "Correcta" : omitida ? "Omitida" : "Incorrecta"}
          >
            {acertada ? "✓" : omitida ? "–" : "✗"}
          </span>
          <span className="text-sm font-medium text-muted">Pregunta {numero}</span>
          <span className="ml-auto rounded-full bg-surface-hover px-2 py-0.5 text-xs text-muted">
            {pregunta.skill_node_name}
          </span>
        </div>

        <TextoRico texto={pregunta.stem} />

        <div className="mt-3 space-y-1.5">
          {pregunta.alternatives.map((alt) => (
            <div
              key={alt.id}
              className={cn(
                "flex items-center gap-2.5 rounded-lg border p-2.5 text-sm",
                alt.is_correct
                  ? "border-success/50 bg-success/10"
                  : alt.selected
                    ? "border-danger/50 bg-danger/10"
                    : "border-border"
              )}
            >
              <span
                className={cn(
                  "flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-xs font-bold",
                  alt.is_correct
                    ? "bg-success text-on-fill"
                    : alt.selected
                      ? "bg-danger text-on-fill"
                      : "bg-surface-hover text-muted"
                )}
              >
                {alt.label}
              </span>
              <TextoRico texto={alt.text} inline />
              {alt.selected && !alt.is_correct && (
                <span className="ml-auto shrink-0 text-xs font-medium text-danger">
                  tu respuesta
                </span>
              )}
              {alt.is_correct && (
                <span className="ml-auto shrink-0 text-xs font-medium text-success">
                  correcta
                </span>
              )}
            </div>
          ))}
        </div>

        <button
          type="button"
          onClick={onAlternar}
          aria-expanded={abierta}
          className="mt-3 w-full rounded-lg border border-accent/30 bg-accent/5 px-3 py-2 text-sm font-medium text-accent transition hover:bg-accent/10"
        >
          {abierta ? "Ocultar resolución" : "Ver cómo se resuelve"}
        </button>

        {abierta && (
          <div className="mt-3 rounded-lg border border-border bg-surface-hover p-4 text-sm">
            <h3 className="mb-2 font-semibold">
              Cómo se resuelve
              {correcta && (
                <span className="ml-2 font-normal text-muted">
                  Respuesta: {correcta.text}
                </span>
              )}
            </h3>
            {pregunta.explanation ? (
              <TextoRico texto={pregunta.explanation} className="text-foreground" />
            ) : (
              <p className="text-muted">
                Esta pregunta todavía no tiene desarrollo escrito.
              </p>
            )}
          </div>
        )}
      </div>
    </li>
  );
}

// El backend agrupa en un diccionario, así que el orden en que llegan los
// grupos depende de en qué posición cayeron las preguntas del ensayo: la
// dificultad salía "Difícil, Fácil, Medio" y los ejes en cualquier orden. Se
// fija acá el orden con el que la gente los lee, y lo desconocido (los nodos
// del árbol, que son decenas) conserva el orden recibido.
const ORDEN_CONOCIDO = [
  "Fácil",
  "Medio",
  "Difícil",
  "Números",
  "Álgebra y Funciones",
  "Geometría",
  "Probabilidad y Estadística",
];

function ordenar(items: BreakdownItem[]): BreakdownItem[] {
  return [...items].sort((a, b) => {
    const ia = ORDEN_CONOCIDO.indexOf(a.name);
    const ib = ORDEN_CONOCIDO.indexOf(b.name);
    if (ia < 0 && ib < 0) return 0;
    return (ia < 0 ? ORDEN_CONOCIDO.length : ia) - (ib < 0 ? ORDEN_CONOCIDO.length : ib);
  });
}

function Desglose({ titulo, items }: { titulo: string; items: BreakdownItem[] }) {
  return (
    <section className="rounded-xl border border-border bg-surface p-4">
      <h2 className="mb-3 text-sm font-semibold">{titulo}</h2>
      <ul className="space-y-2.5">
        {ordenar(items).map((item) => (
          <li key={item.name}>
            <div className="mb-1 flex items-baseline justify-between gap-2 text-sm">
              <span className="truncate">{item.name}</span>
              <span className="shrink-0 text-muted tabular-nums">
                {item.correct}/{item.total}
              </span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-surface-hover">
              <div
                className={cn(
                  "h-full rounded-full",
                  item.percentage >= 70
                    ? "bg-success"
                    : item.percentage >= 40
                      ? "bg-warning"
                      : "bg-danger"
                )}
                style={{ width: `${item.percentage}%` }}
              />
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
