"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { cn } from "@paes-m1/utils";
import { TextoRico } from "@/components/texto-rico";
import { Burbuja } from "@/components/ui/burbuja";
import { gradeDemo, getDemoQuestions, type DemoGradeResult, type DemoQuestion } from "@/lib/api";

const LABELS = ["A", "B", "C", "D", "E"];

type Phase = "loading" | "error" | "ready" | "done";

/**
 * Demo pública sin cuenta: prueba rápido de 5 preguntas, sin login y sin
 * persistir nada (ver apps/api/.../modules/demo). Termina con un CTA fuerte
 * a crear cuenta para guardar el progreso y rendir el ensayo completo.
 */
export function DemoRunner() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [questions, setQuestions] = useState<DemoQuestion[]>([]);
  const [index, setIndex] = useState(0);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [result, setResult] = useState<DemoGradeResult["items"][number] | null>(null);
  const [correctCount, setCorrectCount] = useState(0);

  const load = useCallback(async () => {
    setPhase("loading");
    setIndex(0);
    setSelectedId(null);
    setResult(null);
    setCorrectCount(0);
    try {
      const data = await getDemoQuestions();
      setQuestions(data);
      setPhase(data.length > 0 ? "ready" : "error");
    } catch {
      setPhase("error");
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  const current = questions[index] as DemoQuestion | undefined;

  async function selectAlternative(altId: number) {
    if (!current || result) return;
    setSelectedId(altId);
    try {
      const graded = await gradeDemo([
        { question_id: current.id, selected_alternative_id: altId },
      ]);
      const item = graded.items[0];
      setResult(item);
      if (item.is_correct) setCorrectCount((c) => c + 1);
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
          onClick={load}
          className="btn-glow mt-6 rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
        >
          Reintentar
        </button>
      </div>
    );
  }

  if (phase === "done") {
    const pct = questions.length
      ? Math.round((correctCount / questions.length) * 100)
      : 0;
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
        <span className="text-5xl font-semibold tracking-tight text-accent">{pct}%</span>
        <p className="mt-2 text-sm text-muted">
          {correctCount} de {questions.length} correctas
        </p>
        <p className="mt-6 max-w-sm text-sm text-muted">
          Esto fue solo una prueba de 5 preguntas. Crea una cuenta gratis para
          rendir ensayos completos, guardar tu progreso y ver en qué ejes
          conviene reforzar.
        </p>
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
          <Link
            href="/registro"
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
          >
            Crear cuenta gratis
          </Link>
          <button
            onClick={load}
            className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium hover:bg-surface-hover"
          >
            Probar otras 5 preguntas
          </button>
        </div>
      </div>
    );
  }

  if (!current) return null;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-surface px-4 py-3">
        <div>
          <p className="text-xs font-medium text-muted">Prueba sin cuenta</p>
          <p className="text-sm text-foreground">Competencia Matemática M1</p>
        </div>
        <span className="text-sm text-muted">
          Pregunta <span className="text-foreground">{index + 1}</span> de {questions.length}
        </span>
      </div>

      <div className="rounded-xl border border-border bg-surface p-6">
        <span className="text-xs font-medium text-muted">
          {current.difficulty === "facil"
            ? "Fácil"
            : current.difficulty === "medio"
              ? "Medio"
              : "Difícil"}
        </span>
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
