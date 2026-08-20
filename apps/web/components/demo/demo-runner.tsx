"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { cn } from "@paes-m1/utils";
import { CapturaCorreo } from "@/components/demo/captura-correo";
import { PassagePanel } from "@/components/exam/passage-panel";
import { TextoRico } from "@/components/texto-rico";
import { Burbuja } from "@/components/ui/burbuja";
import {
  gradeDemo,
  getDemoQuestions,
  type DemoGradeResult,
  type DemoQuestion,
  type Subject,
} from "@/lib/api";

const LABELS = ["A", "B", "C", "D", "E"];

/** Las cinco pruebas, en el orden en que las rinde un postulante. */
const PRUEBAS: { id: Subject; nombre: string; corto: string }[] = [
  { id: "lectora", nombre: "Competencia Lectora", corto: "Lectora" },
  { id: "m1", nombre: "Competencia Matemática M1", corto: "M1" },
  { id: "m2", nombre: "Competencia Matemática M2", corto: "M2" },
  { id: "ciencias", nombre: "Ciencias", corto: "Ciencias" },
  { id: "historia", nombre: "Historia y Cs. Sociales", corto: "Historia" },
];

type Phase = "loading" | "error" | "ready" | "done";

/**
 * Demo pública sin cuenta: prueba rápida de 5 preguntas, sin login y sin
 * persistir nada (ver apps/api/.../modules/demo).
 *
 * Termina con un desglose por eje y no solo con un porcentaje. Antes cerraba
 * con "3 de 5 correctas" y un botón de registro: quien se iba en ese punto se
 * iba sin haber recibido nada, y saber en qué eje falló es justamente lo que
 * vino a buscar. Debajo del desglose se puede dejar el correo sin crear cuenta.
 */
export function DemoRunner({ inicial = "m1" }: { inicial?: Subject }) {
  const [subject, setSubject] = useState<Subject>(inicial);
  const [phase, setPhase] = useState<Phase>("loading");
  const [questions, setQuestions] = useState<DemoQuestion[]>([]);
  const [index, setIndex] = useState(0);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [result, setResult] = useState<DemoGradeResult["items"][number] | null>(null);
  // Se guarda el acierto de CADA pregunta, no solo el total: con el total no se
  // puede decir en qué eje se falló, que es lo único accionable de una demo.
  const [aciertos, setAciertos] = useState<Record<number, boolean>>({});

  const load = useCallback(async (prueba: Subject) => {
    setPhase("loading");
    setIndex(0);
    setSelectedId(null);
    setResult(null);
    setAciertos({});
    try {
      const data = await getDemoQuestions(prueba);
      setQuestions(data);
      setPhase(data.length > 0 ? "ready" : "error");
    } catch {
      setPhase("error");
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load(subject);
  }, [load, subject]);

  const current = questions[index] as DemoQuestion | undefined;
  const correctCount = Object.values(aciertos).filter(Boolean).length;

  async function selectAlternative(altId: number) {
    if (!current || result) return;
    setSelectedId(altId);
    try {
      const graded = await gradeDemo([
        { question_id: current.id, selected_alternative_id: altId },
      ]);
      const item = graded.items[0];
      setResult(item);
      setAciertos((previos) => ({ ...previos, [current.id]: item.is_correct }));
    } catch {
      setPhase("error");
    }
  }

  function next() {
    if (index + 1 >= questions.length) {
      setPhase("done");
      return;
    }
    setIndex((i) => i + 1);
    setSelectedId(null);
    setResult(null);
  }

  if (phase === "loading") {
    return (
      <div className="flex flex-1 items-center justify-center py-24 text-sm text-muted">
        Cargando…
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div className="mx-auto flex max-w-md flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
        <h1 className="text-lg font-semibold">No se pudo cargar la demo</h1>
        <p className="mt-2 text-sm text-muted">
          Verifica que la API esté disponible e intenta de nuevo.
        </p>
        <button
          onClick={() => load(subject)}
          className="btn-glow mt-6 rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (phase === "done") {
    return (
      <ResultadoDemo
        questions={questions}
        aciertos={aciertos}
        correctCount={correctCount}
        subject={subject}
        onRepetir={() => load(subject)}
      />
    );
  }

  if (!current) return null;

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6">
      <SelectorPrueba subject={subject} onCambiar={setSubject} />

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-surface px-4 py-3">
        <div>
          <p className="text-xs font-medium text-muted">Prueba sin cuenta</p>
          {/* El rótulo sale de la pregunta, no de una constante: antes decía
              "Competencia Matemática M1" siempre, incluso cuando el sorteo
              devolvía una pregunta de otra prueba. */}
          <p className="text-sm text-foreground">
            {PRUEBAS.find((p) => p.id === subject)?.nombre ?? current.node_name}
          </p>
        </div>
        <span className="text-sm text-muted">
          Pregunta <span className="text-foreground">{index + 1}</span> de {questions.length}
        </span>
      </div>

      {/* La pregunta de lectora no se puede contestar sin su texto. */}
      {current.passage && <PassagePanel passage={current.passage} />}

      <div className="rounded-xl border border-border bg-surface p-6">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-medium text-muted">
            {current.difficulty === "facil"
              ? "Fácil"
              : current.difficulty === "medio"
                ? "Medio"
                : "Difícil"}
          </span>
          <span className="text-xs text-muted">·</span>
          <span className="text-xs text-muted">{current.axis_label}</span>
        </div>
        <p className="mt-2 text-base leading-relaxed text-foreground">{current.stem}</p>

        <div className="mt-6 flex flex-col gap-2.5">
          {current.alternatives.map((alt, i) => {
            const isSelected = selectedId === alt.id;
            const isCorrectAlt = result && alt.id === result.correct_alternative_id;
            const isWrongSelected = result && isSelected && !result.is_correct;
            return (
              <button
                key={alt.id}
                onClick={() => selectAlternative(alt.id)}
                disabled={!!result}
                className={cn(
                  "flex items-start gap-3 rounded-lg border px-4 py-3 text-left text-sm transition-colors",
                  isCorrectAlt
                    ? "border-success/50 bg-success/10 text-foreground"
                    : isWrongSelected
                      ? "border-danger/50 bg-danger/10 text-foreground"
                      : isSelected
                        ? "border-accent bg-accent/10 text-foreground"
                        : "border-border bg-background text-foreground",
                  !result && "hover:border-border-strong hover:bg-surface-hover",
                  result && !isCorrectAlt && !isWrongSelected && "opacity-60"
                )}
              >
                {/* Mientras el estudiante elige, la burbuja de grafito: es el
                    gesto del cartón de respuestas. Una vez corregido manda el
                    verde o el rojo, porque ahí el color ES la información y no
                    la marca. */}
                {isCorrectAlt || isWrongSelected ? (
                  <span
                    aria-hidden
                    className={cn(
                      "flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[11px] font-bold",
                      isCorrectAlt
                        ? "border-success bg-success text-on-fill"
                        : "border-danger bg-danger text-on-fill"
                    )}
                  >
                    {LABELS[i]}
                  </span>
                ) : (
                  <Burbuja letra={LABELS[i]} marcada={isSelected} tamano="chica" />
                )}
                <span>{alt.text}</span>
              </button>
            );
          })}
        </div>

        {result && (
          <div
            className={cn(
              "mt-4 rounded-lg border px-4 py-3 text-sm",
              result.is_correct
                ? "border-success/40 bg-success/5 text-success"
                : "border-danger/40 bg-danger/5 text-danger"
            )}
          >
            <p className="font-medium">{result.is_correct ? "¡Correcto!" : "Incorrecto"}</p>
          </div>
        )}

        {result?.explanation && (
          <div className="mt-3 rounded-lg border border-border bg-surface-hover px-4 py-3 text-sm">
            <h3 className="mb-2 font-semibold">Cómo se resuelve</h3>
            <TextoRico texto={result.explanation} className="text-foreground" />
          </div>
        )}

        <div className="mt-6 flex items-center justify-end">
          <button
            onClick={next}
            disabled={!result}
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground disabled:pointer-events-none disabled:opacity-40"
          >
            {index + 1 === questions.length ? "Ver resultado" : "Siguiente →"}
          </button>
        </div>
      </div>
    </div>
  );
}

/** Elegir la prueba antes de partir: la demo ya no es solo de matemática. */
function SelectorPrueba({
  subject,
  onCambiar,
}: {
  subject: Subject;
  onCambiar: (s: Subject) => void;
}) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-xs font-medium text-muted">Prueba:</span>
      {PRUEBAS.map((prueba) => (
        <button
          key={prueba.id}
          onClick={() => onCambiar(prueba.id)}
          aria-pressed={subject === prueba.id}
          className={cn(
            "rounded-full border px-3 py-1.5 text-xs font-medium transition-colors",
            subject === prueba.id
              ? "border-accent bg-accent/10 text-accent"
              : "border-border bg-surface text-muted hover:bg-surface-hover"
          )}
        >
          {prueba.corto}
        </button>
      ))}
    </div>
  );
}

type ResumenEje = { eje: string; correctas: number; total: number };

/**
 * Desglose por eje: correctas sobre total en cada uno.
 *
 * Con cinco preguntas no da para un puntaje, y decir uno sería inventarlo. Lo
 * que sí es honesto es decir dónde se falló, que además es lo que hace útil
 * volver.
 */
function resumirPorEje(
  questions: DemoQuestion[],
  aciertos: Record<number, boolean>
): ResumenEje[] {
  const porEje = new Map<string, ResumenEje>();
  for (const q of questions) {
    if (!(q.id in aciertos)) continue;
    const fila = porEje.get(q.axis_label) ?? { eje: q.axis_label, correctas: 0, total: 0 };
    fila.total += 1;
    if (aciertos[q.id]) fila.correctas += 1;
    porEje.set(q.axis_label, fila);
  }
  // Lo flojo primero: es lo que hay que mirar.
  return [...porEje.values()].sort(
    (a, b) => a.correctas / a.total - b.correctas / b.total
  );
}

function ResultadoDemo({
  questions,
  aciertos,
  correctCount,
  subject,
  onRepetir,
}: {
  questions: DemoQuestion[];
  aciertos: Record<number, boolean>;
  correctCount: number;
  subject: Subject;
  onRepetir: () => void;
}) {
  const respondidas = Object.keys(aciertos).length;
  const pct = respondidas ? Math.round((correctCount / respondidas) * 100) : 0;
  const porEje = resumirPorEje(questions, aciertos);
  const flojo = porEje.find((e) => e.correctas < e.total);
  const nombrePrueba = PRUEBAS.find((p) => p.id === subject)?.nombre ?? "la prueba";

  return (
    <div className="mx-auto flex w-full max-w-lg flex-col gap-6">
      <div className="flex flex-col items-center rounded-2xl border border-border bg-surface px-6 py-10 text-center">
        <span className="text-5xl font-semibold tracking-tight text-accent">{pct}%</span>
        <p className="mt-2 text-sm text-muted">
          {correctCount} de {respondidas} correctas en {nombrePrueba}
        </p>
      </div>

      <div className="rounded-2xl border border-border bg-surface p-6">
        <h2 className="text-sm font-semibold text-foreground">Cómo te fue por eje</h2>
        <p className="mt-1 text-xs text-muted">
          Cinco preguntas no alcanzan para estimar un puntaje —eso necesita un
          ensayo completo—, pero sí muestran dónde mirar primero.
        </p>

        <dl className="mt-5 flex flex-col gap-3">
          {porEje.map((eje) => {
            const proporcion = eje.correctas / eje.total;
            return (
              <div key={eje.eje}>
                <div className="mb-1 flex items-center justify-between text-xs">
                  <dt className="text-foreground">{eje.eje}</dt>
                  <dd className="text-muted tabular-nums">
                    {eje.correctas}/{eje.total}
                  </dd>
                </div>
                <div className="h-1.5 w-full overflow-hidden rounded-full bg-surface-hover">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${Math.max(proporcion * 100, 3)}%`,
                      background:
                        proporcion === 1 ? "var(--success)" : "var(--accent-warm)",
                    }}
                  />
                </div>
              </div>
            );
          })}
        </dl>

        {flojo && (
          <p className="mt-5 rounded-lg border border-border bg-background px-4 py-3 text-sm text-muted">
            Donde más se te escapó fue en{" "}
            <strong className="text-foreground">{flojo.eje}</strong>. Con una
            cuenta puedes practicar ese eje solo, con corrección inmediata y la
            lección del tema.
          </p>
        )}
      </div>

      <div className="flex flex-col gap-4 rounded-2xl border border-accent/40 bg-accent/5 p-6">
        <div>
          <h2 className="font-semibold">Esto fue una muestra de 5 preguntas</h2>
          <p className="mt-1.5 text-sm text-muted">
            Un ensayo completo va cronometrado como la prueba real y termina con
            tu puntaje estimado en escala 100-1000, el desglose por eje y
            dificultad, y la resolución de cada ejercicio.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <Link
            href="/registro"
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
          >
            Crear cuenta gratis
          </Link>
          <button
            onClick={onRepetir}
            className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium hover:bg-surface-hover"
          >
            Probar otras 5
          </button>
        </div>
      </div>

      <div className="rounded-2xl border border-border bg-surface p-6">
        <CapturaCorreo source="demo" />
      </div>
    </div>
  );
}
