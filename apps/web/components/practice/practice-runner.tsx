"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { cn } from "@paes-m1/utils";
import { Resolucion } from "@/components/exam/resolucion";
import { Burbuja } from "@/components/ui/burbuja";
import {
  answerPractice,
  ApiError,
  getPracticeQuestions,
  type PracticeAnswerResult,
  type PracticeQuestion,
} from "@/lib/api";
import { getClientToken, loginHref } from "@/lib/auth";
import { AvisoDesbloqueo } from "@/components/skill-tree/aviso-desbloqueo";
import { NumeroAnimado } from "@/components/motion/numero-animado";

const LABELS = ["A", "B", "C", "D", "E"];

/**
 * Bajo este porcentaje, la sesión manda a la teoría antes que a más ejercicios.
 *
 * Es el mismo umbral con el que el árbol desbloquea un nodo (75%): por debajo
 * de eso el tema no está, y seguir haciendo ejercicios es practicar el error.
 */
const UMBRAL_TEORIA = 75;

type Phase = "loading" | "locked" | "error" | "ready" | "done";

export function PracticeRunner({ code }: { code: string }) {
  const router = useRouter();
  const pathname = usePathname();
  const [phase, setPhase] = useState<Phase>("loading");
  const [nodeName, setNodeName] = useState("");
  const [tieneLeccion, setTieneLeccion] = useState(false);
  const [questions, setQuestions] = useState<PracticeQuestion[]>([]);
  const [index, setIndex] = useState(0);
  const [answered, setAnswered] = useState<PracticeAnswerResult | null>(null);
  // Mientras la corrección viaja. Sin esto, entre el clic y la respuesta no
  // cambiaba nada: la alternativa quedaba marcada, "Siguiente" seguía
  // apagado y no había ninguna señal de que la aplicación estuviera haciendo
  // algo. Medido en local, un arranque en frío de la API tardó 13,8 segundos
  // en ese POST. Catorce segundos sin respuesta se leen como "se colgó", y lo
  // que hace el alumno es volver a tocar.
  const [corrigiendo, setCorrigiendo] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [sessionCorrect, setSessionCorrect] = useState(0);
  const [unlockedThisSession, setUnlockedThisSession] = useState<string[]>([]);
  /** Lo que se acaba de abrir, para avisarlo EN EL MOMENTO y no al final. */
  const [reciénAbiertos, setReciénAbiertos] = useState<string[]>([]);
  const [lastResult, setLastResult] = useState<PracticeAnswerResult | null>(null);

  const load = useCallback(async () => {
    setPhase("loading");
    setIndex(0);
    setAnswered(null);
    setSelectedId(null);
    setSessionCorrect(0);
    setUnlockedThisSession([]);
    try {
      const data = await getPracticeQuestions(code, getClientToken() ?? undefined);
      setNodeName(data.node_name);
      setTieneLeccion(data.has_lesson);
      setQuestions(data.questions);
      setPhase(data.questions.length > 0 ? "ready" : "error");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push(loginHref(pathname));
        return;
      }
      if (err instanceof ApiError && err.status === 403) {
        setPhase("locked");
        return;
      }
      setPhase("error");
    }
  }, [code, router, pathname]);

  useEffect(() => {
    // Fetch de datos al montar: load() marca "loading" antes del await,
    // patrón estándar de carga inicial (no una lectura de estado externo).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    load();
  }, [load]);

  const current = questions[index] as PracticeQuestion | undefined;

  async function selectAlternative(altId: number) {
    if (!current || answered || corrigiendo) return;
    setSelectedId(altId);
    setCorrigiendo(true);
    try {
      const res = await answerPractice(code, current.id, altId, getClientToken() ?? undefined);
      setAnswered(res);
      setLastResult(res);
      if (res.is_correct) setSessionCorrect((c) => c + 1);
      if (res.newly_unlocked.length > 0) {
        setUnlockedThisSession((prev) => [
          ...prev,
          ...res.newly_unlocked.filter((n) => !prev.includes(n)),
        ]);
        setReciénAbiertos(res.newly_unlocked);
      }
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) router.push(loginHref(pathname));
    } finally {
      setCorrigiendo(false);
    }
  }

  function next() {
    if (index + 1 >= questions.length) {
      setPhase("done");
      return;
    }
    setIndex((i) => i + 1);
    setAnswered(null);
    setSelectedId(null);
  }

  if (phase === "loading") {
    return (
      <div className="flex flex-1 items-center justify-center py-24 text-sm text-muted">
        Cargando…
      </div>
    );
  }

  if (phase === "locked") {
    return (
      <div className="mx-auto flex max-w-md flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-surface-hover text-muted">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="5" y="11" width="14" height="9" rx="2" />
            <path d="M8 11V7a4 4 0 0 1 8 0v4" />
          </svg>
        </div>
        <h1 className="mt-4 text-lg font-semibold">Este nodo todavía está bloqueado</h1>
        <p className="mt-2 text-sm text-muted">
          Mejora tu acierto en sus prerequisitos para desbloquearlo.
        </p>
        <Link
          href="/arbol"
          className="btn-glow mt-6 rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
        >
          Volver al Árbol de Habilidades
        </Link>
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div className="mx-auto flex max-w-md flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
        <h1 className="text-lg font-semibold">No se pudo cargar la práctica</h1>
        <p className="mt-2 text-sm text-muted">
          Verifica que la API esté disponible e intenta de nuevo.
        </p>
        <Link
          href="/arbol"
          className="mt-6 rounded-lg border border-border px-5 py-2.5 text-sm font-medium hover:bg-surface-hover"
        >
          Volver al Árbol de Habilidades
        </Link>
      </div>
    );
  }

  if (phase === "done") {
    const pct = questions.length
      ? Math.round((sessionCorrect / questions.length) * 100)
      : 0;
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
        <AvisoDesbloqueo nodos={reciénAbiertos} />
        <span className="font-display text-5xl font-semibold tracking-tight">
          <NumeroAnimado valor={pct} duracion={1} sufijo="%" />
        </span>
        <p className="mt-2 text-sm text-muted">
          {sessionCorrect} de {questions.length} correctas en esta ronda de{" "}
          {nodeName}
        </p>
        {lastResult && (
          <p className="mt-1 text-xs text-muted">
            Progreso acumulado en este nodo: {Math.round(lastResult.node_accuracy * 100)}% ·{" "}
            {lastResult.node_attempts} respuestas en total
          </p>
        )}

        {unlockedThisSession.length > 0 && (
          <div className="mt-6 w-full rounded-xl border border-accent/40 bg-accent/10 px-4 py-3 text-left">
            <p className="text-xs font-medium text-accent">¡Desbloqueaste nuevos nodos!</p>
            <p className="mt-1 text-sm text-foreground">
              {unlockedThisSession.join(" · ")}
            </p>
          </div>
        )}

        {/* Antes esto terminaba en "de nuevo" o "volver al árbol": dos formas
            de quedarse donde estaba. Lo que sigue después de practicar un tema
            depende de cómo le fue, y decirlo es la diferencia entre una sesión
            suelta y un plan. */}
        {pct < UMBRAL_TEORIA && tieneLeccion && (
          <div className="mt-6 w-full rounded-xl border border-accent-warm/40 bg-accent-warm/5 px-4 py-3 text-left">
            <p className="text-sm font-semibold text-accent-warm-strong">
              Menos de {UMBRAL_TEORIA}% en {nodeName}
            </p>
            <p className="mt-1 text-sm text-muted">
              Antes de seguir ejercitando conviene volver a la teoría: repetir
              ejercicios sin entender el método fija el error, no lo corrige.
            </p>
            <Link
              href={`/aprender/${code}`}
              className="mt-2 inline-flex text-sm font-semibold text-accent-warm-strong hover:underline"
            >
              Leer la lección de este tema →
            </Link>
          </div>
        )}

        <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={load}
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
          >
            Practicar de nuevo
          </button>
          <Link
            href="/examen"
            className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium hover:bg-surface-hover"
          >
            Medirme en un ensayo
          </Link>
          <Link
            href="/arbol"
            className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium hover:bg-surface-hover"
          >
            Volver al árbol
          </Link>
        </div>
      </div>
    );
  }

  if (!current) return null;

  return (
    <div className="flex flex-col gap-6">
      <AvisoDesbloqueo nodos={reciénAbiertos} />
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-surface px-4 py-3">
        <div>
          <p className="text-xs font-medium text-muted">Practicando</p>
          <p className="text-sm text-foreground">{nodeName}</p>
        </div>
        <span className="text-sm text-muted">
          Pregunta <span className="text-foreground">{index + 1}</span> de {questions.length}
        </span>
      </div>

      <div className="rounded-xl border border-border bg-surface p-6">
        <span className="text-xs font-medium text-muted">
          {current.difficulty === "facil" ? "Fácil" : current.difficulty === "medio" ? "Medio" : "Difícil"}
        </span>
        <p className="mt-2 text-base leading-relaxed text-foreground">{current.stem}</p>

        <div className="mt-6 flex flex-col gap-2.5">
          {current.alternatives.map((alt, i) => {
            const isSelected = selectedId === alt.id;
            const isCorrectAlt = answered && alt.id === answered.correct_alternative_id;
            const isWrongSelected = answered && isSelected && !answered.is_correct;
            return (
              <button
                key={alt.id}
                onClick={() => selectAlternative(alt.id)}
                disabled={!!answered || corrigiendo}
                className={cn(
                  "flex items-start gap-3 rounded-lg border px-4 py-3 text-left text-sm transition-colors",
                  isCorrectAlt
                    ? "border-success/50 bg-success/10 text-foreground"
                    : isWrongSelected
                      ? "border-danger/50 bg-danger/10 text-foreground"
                      : isSelected
                        ? "border-accent bg-accent/10 text-foreground"
                        : "border-border bg-background text-foreground",
                  !answered && "hover:border-border-strong hover:bg-surface-hover",
                  answered && !isCorrectAlt && !isWrongSelected && "opacity-60"
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

        {answered && (
          <div
            className={cn(
              "mt-4 rounded-lg border px-4 py-3 text-sm",
              answered.is_correct
                ? "border-success/40 bg-success/5 text-success"
                : "border-danger/40 bg-danger/5 text-danger"
            )}
          >
            <p className="font-medium">
              {answered.is_correct ? "¡Correcto!" : "Incorrecto"}
            </p>
          </div>
        )}

        {/* La señal de que la corrección viene en camino. Ocupa el mismo
            lugar donde va a aparecer, así que no hay salto cuando llega. */}
        {corrigiendo && (
          <p
            role="status"
            className="mt-3 rounded-xl border border-border bg-surface px-4 py-3 text-sm text-muted"
          >
            Corrigiendo tu respuesta…
          </p>
        )}

        {answered && (
          <Resolucion
            explicacion={answered.explanation}
            errorPropio={answered.distractor_justification}
          />
        )}

        {answered && answered.newly_unlocked.length > 0 && (
          <div className="mt-3 rounded-lg border border-accent/40 bg-accent/10 px-4 py-3 text-sm text-foreground">
            ¡Desbloqueaste: {answered.newly_unlocked.join(" · ")}!
          </div>
        )}

        <div className="mt-6 flex items-center justify-end">
          <button
            onClick={next}
            disabled={!answered}
            className="btn-glow rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground disabled:pointer-events-none disabled:opacity-40"
          >
            {index + 1 === questions.length ? "Finalizar" : "Siguiente →"}
          </button>
        </div>
      </div>
    </div>
  );
}
