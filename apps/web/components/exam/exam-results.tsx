"use client";

import Link from "next/link";
import { useState } from "react";
import { cn } from "@paes-m1/utils";
import { CompartirResultado } from "@/components/exam/compartir-resultado";
import { FiguraPregunta } from "@/components/exam/figura-pregunta";
import { Resolucion } from "@/components/exam/resolucion";
import { TextoRico } from "@/components/texto-rico";
import type { BreakdownItem, ExamResult, ExamReview, ReviewQuestion } from "@/lib/api";
import { formatearTiempo } from "@/lib/tiempo";
import { NumeroAnimado } from "@/components/motion/numero-animado";
import { BarraProgreso } from "@/components/ui/barra-progreso";

/** El piso de la escala PAES. Un puntaje nunca baja de acá. */
const PUNTAJE_MINIMO = 100;
const PUNTAJE_MAXIMO = 1000;

/** Dónde cae un puntaje dentro de la escala, en porcentaje. */
function porcentajeEnLaEscala(puntaje: number | null | undefined): number {
  if (puntaje == null) return 0;
  const acotado = Math.min(PUNTAJE_MAXIMO, Math.max(PUNTAJE_MINIMO, puntaje));
  return ((acotado - PUNTAJE_MINIMO) / (PUNTAJE_MAXIMO - PUNTAJE_MINIMO)) * 100;
}

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

/**
 * El tema concreto al que mandar al alumno cuando termina el ensayo.
 *
 * Un eje ("Geometría") no es accionable: agrupa varios temas y no tiene página
 * propia. Un nodo sí —tiene lección y tiene práctica—, y es lo que convierte
 * "te fue mal en Geometría" en algo que se puede pulsar.
 *
 * Se elige el de peor porcentaje, y a igual porcentaje el que tuvo MÁS
 * preguntas: entre dos temas al 0%, el de tres preguntas dice más que el de
 * una. Quedan fuera los temas donde no se falló nada: mandar a reforzar algo
 * que salió perfecto es ruido.
 *
 * `evidencia` distingue los dos casos, porque la pantalla no puede afirmar lo
 * mismo con una pregunta que con cinco. En un ensayo Relámpago de 10 preguntas
 * repartidas entre dieciséis temas, casi todos los temas traen una sola.
 */
function temaParaReforzar(
  items: BreakdownItem[]
): { item: BreakdownItem; code: string; evidencia: "sola" | "varias" } | null {
  const candidatos = items
    .filter((d) => d.code != null && d.correct < d.total)
    .sort((a, b) => a.percentage - b.percentage || b.total - a.total);

  const peor = candidatos[0];
  if (!peor || peor.code == null) return null;
  return { item: peor, code: peor.code, evidencia: peor.total >= 2 ? "varias" : "sola" };
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
  const tema = temaParaReforzar(result.by_node);

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
      {/* Terminar un ensayo es el momento del producto: son dos horas y veinte
          de trabajo y el número que sale decide cómo se siente el resto del
          día. Aparecía de golpe, sin ceremonia. Ahora el puntaje sube por la
          escala y las cifras lo acompañan.

          Sube DESDE 100 y no desde 0: la escala PAES empieza en 100, así que
          contar desde cero muestra durante un segundo puntajes que no existen. */}
      {/* SIN RESPUESTAS NO HAY PUNTAJE QUE MOSTRAR.
          El puntaje de un ensayo vacío es 100: el piso de la escala, no una
          medición de nadie. Presentarlo en rojo y a 60 px como "Puntaje
          estimado · Por reforzar" le dice a alguien que abandonó que rinde
          en el mínimo, que es exactamente lo que sus cero respuestas NO
          demuestran. En producción el 62% de los ensayos entregados estaban
          así, y hasta ahora todos entraban al historial. */}
      {result.answered === 0 ? (
        <section className="rounded-2xl border border-border bg-surface p-6 text-center">
          <p className="font-display text-2xl font-bold">
            Este ensayo quedó sin responder
          </p>
          <p className="mx-auto mt-2 max-w-md text-sm text-muted">
            No hay puntaje que estimar con cero respuestas, así que este ensayo
            no entra en tu progreso. Las {result.total_questions} preguntas
            siguen abajo con su resolución, por si quieres mirarlas.
          </p>
        </section>
      ) : (
      <section className="rounded-2xl border border-border bg-surface p-6 text-center">
        <p className="text-sm text-muted">Puntaje estimado</p>
        <p className={cn("font-display mt-1 text-6xl font-bold", nivel.clase)}>
          <NumeroAnimado
            valor={result.estimated_score ?? PUNTAJE_MINIMO}
            desde={PUNTAJE_MINIMO}
            duracion={1.4}
          />
        </p>
        <p className={cn("mt-1 font-semibold", nivel.clase)}>{nivel.etiqueta}</p>

        {/* La escala entera, dibujada. "780" no significa nada para quien no
            sabe que el máximo es 1000: verlo sobre el rango lo ubica sin una
            palabra de explicación. */}
        <div className="mx-auto mt-4 max-w-sm">
          <BarraProgreso
            porcentaje={porcentajeEnLaEscala(result.estimated_score)}
            color="var(--color-prueba-actual, var(--accent))"
            etiqueta={`Puntaje ${result.estimated_score ?? "—"} en la escala de 100 a 1000`}
            alCargar
          />
          <div className="mt-1.5 flex justify-between text-[11px] text-muted tabular-nums">
            <span>100</span>
            <span>1000</span>
          </div>
        </div>

        <p className="mt-4 text-sm text-muted">
          {result.correct} de {result.total_questions} correctas ({logro}%)
        </p>

        <div className="mt-5 grid grid-cols-3 gap-2 text-sm">
          <div className="rounded-lg bg-success/10 p-3">
            <p className="font-display text-2xl font-bold text-success">
              <NumeroAnimado valor={result.correct} duracion={1} />
            </p>
            <p className="text-success">correctas</p>
          </div>
          <div className="rounded-lg bg-danger/10 p-3">
            <p className="font-display text-2xl font-bold text-danger">
              <NumeroAnimado valor={result.incorrect} duracion={1} />
            </p>
            <p className="text-danger">incorrectas</p>
          </div>
          <div className="rounded-lg bg-surface-hover p-3">
            <p className="font-display text-2xl font-bold">
              <NumeroAnimado valor={result.omitted} duracion={1} />
            </p>
            <p className="text-muted">omitidas</p>
          </div>
        </div>

        <p className="mt-4 text-sm text-muted">
          Tiempo usado: {formatearTiempo(result.elapsed_seconds)} de{" "}
          {formatearTiempo(result.duration_limit_seconds)}
        </p>

        {/* En el ensayo oficial importa tanto el puntaje como haber aguantado
            sentado: la prueba real son dos horas y media sin levantarse. Las
            salidas no descuentan nada; se muestran porque son el dato que
            avisa cómo va a ser ese día. */}
        {result.oficial && (
          <p className="mt-2 text-sm text-muted">
            Ensayo oficial ·{" "}
            {result.salidas === 0 ? (
              <strong className="text-foreground">
                no saliste de la página en todo el ensayo
              </strong>
            ) : (
              <>
                saliste de la página{" "}
                <strong className="text-foreground">
                  {result.salidas} {result.salidas === 1 ? "vez" : "veces"}
                </strong>
                , {formatearTiempo(result.segundos_fuera)} fuera
              </>
            )}
          </p>
        )}

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
      )}

      {/* ── Sugerencia de refuerzo ──────────────────────────────────────
          El ensayo terminaba acá en un consejo que el alumno tenía que
          ejecutar a mano ("puedes armar un ensayo filtrando por ese eje"). Es
          el momento de más información y más ganas de todo el producto, y la
          única salida era volver al historial. Ahora el eje da el diagnóstico
          y el tema da el siguiente paso, con las dos puertas que ese tema
          tiene: la teoría y la práctica.

          Nada de eso aplica sin respuestas: con cero, TODOS los ejes marcan
          0% y el bloque "diagnosticaba" los tres primeros de la lista, que es
          consejo sacado de ninguna evidencia. */}
      {result.answered > 0 && (debiles.length > 0 || tema) && (
        <section className="mt-5 rounded-xl border border-warning/40 bg-warning/10 p-4">
          <h2 className="font-semibold text-warning">Qué conviene reforzar</h2>

          {debiles.length > 0 && (
            <p className="mt-1 text-sm">
              Tu rendimiento fue más bajo en{" "}
              {debiles.map((d, i) => (
                <span key={d.name}>
                  {i > 0 && (i === debiles.length - 1 ? " y " : ", ")}
                  <strong>{d.name}</strong> ({d.percentage}%)
                </span>
              ))}
              .
            </p>
          )}

          {tema && (
            <div className="mt-3 rounded-lg border border-warning/30 bg-surface p-3">
              <p className="text-sm">
                {/* Con una sola pregunta no se puede hablar de "tu tema más
                    débil": se dice lo que pasó, que es un hecho, y el alumno
                    decide. Con dos o más, el porcentaje ya significa algo. */}
                {tema.evidencia === "sola" ? (
                  <>
                    Se te escapó la pregunta de <strong>{tema.item.name}</strong>.
                  </>
                ) : (
                  <>
                    Donde peor te fue es <strong>{tema.item.name}</strong>:{" "}
                    {tema.item.correct} de {tema.item.total} preguntas.
                  </>
                )}
              </p>
              <div className="mt-3 flex flex-col gap-2 sm:flex-row">
                <Link
                  href={`/aprender/${tema.code}`}
                  className="flex-1 rounded-lg border border-border px-4 py-2 text-center text-sm font-medium transition hover:bg-surface-hover"
                >
                  Estudiar la teoría
                </Link>
                <Link
                  href={`/practicar/${tema.code}`}
                  className="flex-1 rounded-lg bg-warning px-4 py-2 text-center text-sm font-semibold text-on-fill transition hover:opacity-90"
                >
                  Practicar este tema →
                </Link>
              </div>
            </div>
          )}
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

      <div className="mt-8 flex flex-col gap-3 sm:flex-row">
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
  // Solo la que se marcó y estaba mal: en la correcta no hay error que
  // explicar, y en las que no se tocaron el alumno nunca pensó nada.
  const elegidaIncorrecta = pregunta.alternatives.find((a) => a.selected && !a.is_correct);

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

        {pregunta.image_url && <FiguraPregunta src={pregunta.image_url} />}

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
          <Resolucion
            explicacion={pregunta.explanation}
            respuestaCorrecta={correcta?.text}
            errorPropio={elegidaIncorrecta?.distractor_justification}
          />
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
        {ordenar(items).map((item, i) => (
          <li key={item.name}>
            <div className="mb-1 flex items-baseline justify-between gap-2 text-sm">
              <span className="truncate">{item.name}</span>
              <span className="shrink-0 text-muted tabular-nums">
                {item.correct}/{item.total}
              </span>
            </div>
            {/* Se llenan al entrar, una detrás de otra: el orden ya es
                significativo --el eje más flojo va primero-- y verlas crecer
                en ese orden es la lectura que queremos que haga. */}
            <BarraProgreso
              porcentaje={item.percentage}
              color={
                item.percentage >= 70
                  ? "var(--success)"
                  : item.percentage >= 40
                    ? "var(--warning)"
                    : "var(--danger)"
              }
              etiqueta={`${item.name}: ${item.correct} de ${item.total}`}
              delay={i * 0.08}
              alCargar
            />
          </li>
        ))}
      </ul>
    </section>
  );
}
