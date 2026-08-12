"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { cn } from "@paes-m1/utils";
import {
  ApiError,
  answerExamQuestion,
  getExamReview,
  getExamState,
  startExam,
  submitExam,
  type ExamAttemptSummary,
  type ExamQuestion,
  type ExamResult,
  type NodeDiagnosis,
} from "@/lib/api";
import { getClientToken } from "@/lib/auth";

const STORAGE_KEY = "paes_exam_attempt_id";
const LABELS = ["A", "B", "C", "D", "E"];

type Phase = "idle" | "loading" | "in_progress" | "submitted" | "error";

function formatClock(ms: number): string {
  const totalSeconds = Math.max(0, Math.floor(ms / 1000));
  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;
  return [h, m, s].map((v) => String(v).padStart(2, "0")).join(":");
}

interface ExamRunnerProps {
  pastAttempts: ExamAttemptSummary[];
  resumableAttemptId: number | null;
}

export function ExamRunner({ pastAttempts, resumableAttemptId }: ExamRunnerProps) {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>("idle");
  const [attemptId, setAttemptId] = useState<number | null>(null);
  const [questions, setQuestions] = useState<ExamQuestion[]>([]);
  const [deadline, setDeadline] = useState<number>(0);
  const [remainingMs, setRemainingMs] = useState(0);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selections, setSelections] = useState<Record<number, number | null>>({});
  const [, setElapsedByQuestion] = useState<Record<number, number>>({});
  const [result, setResult] = useState<ExamResult | null>(null);
  const [weakNodes, setWeakNodes] = useState<NodeDiagnosis[] | null>(null);
  const [confirmingSubmit, setConfirmingSubmit] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const segmentStartRef = useRef(0);
  const attemptIdRef = useRef<number | null>(null);

  useEffect(() => {
    attemptIdRef.current = attemptId;
  }, [attemptId]);

  const currentQuestion = questions[currentIndex] as ExamQuestion | undefined;

  const flush = useCallback(
    (questionId: number, selectedAlternativeId: number | null): Promise<void> => {
      const now = Date.now();
      const delta = now - segmentStartRef.current;
      segmentStartRef.current = now;
      const id = attemptIdRef.current;
      if (id == null) return Promise.resolve();

      let total = 0;
      setElapsedByQuestion((prev) => {
        total = (prev[questionId] ?? 0) + Math.max(0, delta);
        return { ...prev, [questionId]: total };
      });

      return answerExamQuestion(
        id,
        questionId,
        selectedAlternativeId,
        total,
        getClientToken() ?? undefined
      ).then(
        () => {},
        (err) => {
          // Autosave best-effort: si falla, el próximo flush reintenta con el tiempo acumulado.
          if (err instanceof ApiError && err.status === 401) router.push("/login");
        }
      );
    },
    [router]
  );

  const goToQuestion = useCallback(
    (index: number) => {
      if (index < 0 || index >= questions.length || index === currentIndex) return;
      const q = questions[currentIndex];
      if (q) flush(q.id, selections[q.id] ?? null);
      setCurrentIndex(index);
    },
    [currentIndex, questions, selections, flush]
  );

  const selectAlternative = useCallback(
    (altId: number) => {
      if (!currentQuestion) return;
      setSelections((prev) => ({ ...prev, [currentQuestion.id]: altId }));
      flush(currentQuestion.id, altId);
    },
    [currentQuestion, flush]
  );

  const doSubmit = useCallback(async () => {
    const id = attemptIdRef.current;
    if (id == null || submitting) return;
    setSubmitting(true);
    try {
      // Espera a que la última respuesta quede guardada ANTES de enviar el
      // submit — si se disparan en paralelo, el submit puede llegar primero
      // y el answer subsiguiente falla con 409 (intento ya finalizado).
      if (currentQuestion) {
        await flush(currentQuestion.id, selections[currentQuestion.id] ?? null);
      }
      const token = getClientToken() ?? undefined;
      const res = await submitExam(id, token);
      setResult(res);
      setPhase("submitted");
      localStorage.removeItem(STORAGE_KEY);
      // Mejor esfuerzo: si falla, el resumen de nodos débiles simplemente no se muestra.
      getExamReview(id, token)
        .then((review) => setWeakNodes(review.node_diagnosis.slice(0, 3)))
        .catch(() => {});
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push("/login");
        return;
      }
      setErrorMsg("No se pudo enviar el examen. Revisa tu conexión e intenta de nuevo.");
    } finally {
      setSubmitting(false);
    }
  }, [currentQuestion, selections, flush, router, submitting]);

  const resumeAttempt = useCallback(async (id: number) => {
    setPhase("loading");
    try {
      const state = await getExamState(id, getClientToken() ?? undefined);
      if (state.status !== "in_progress") {
        localStorage.removeItem(STORAGE_KEY);
        setPhase("idle");
        return;
      }
      localStorage.setItem(STORAGE_KEY, String(id));
      setAttemptId(id);
      setQuestions(state.questions);
      setDeadline(
        new Date(state.started_at).getTime() + state.duration_limit_seconds * 1000
      );
      const sel: Record<number, number | null> = {};
      const elap: Record<number, number> = {};
      for (const [qid, ans] of Object.entries(state.answers)) {
        sel[Number(qid)] = ans.selected_alternative_id ?? null;
        elap[Number(qid)] = ans.time_spent_ms ?? 0;
      }
      setSelections(sel);
      setElapsedByQuestion(elap);
      setPhase("in_progress");
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      setPhase("idle");
    }
  }, []);

  // Resumir un intento en curso al montar: primero localStorage (mismo
  // navegador), y si no hay nada, un intento in_progress que el servidor
  // ya sabe que es nuestro (ej. se limpió el localStorage o es otro
  // dispositivo) — así nunca se crean intentos duplicados sin querer.
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    const id = saved ? Number(saved) : resumableAttemptId;
    if (id == null || !Number.isFinite(id)) return;
    // Fetch de datos al montar: resumeAttempt marca "loading" antes del
    // await, patrón estándar de carga inicial (no una lectura de estado
    // externo que deba evitarse en un efecto).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    resumeAttempt(id);
  }, [resumableAttemptId, resumeAttempt]);

  // Advertencia al cerrar/recargar la pestaña con un examen en curso —
  // el autosave por pregunta ya cubre la mayoría de los casos, esto es
  // una segunda red de seguridad para no perder la respuesta actual.
  useEffect(() => {
    if (phase !== "in_progress") return;
    function onBeforeUnload(e: BeforeUnloadEvent) {
      e.preventDefault();
    }
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [phase]);

  // Reset del cronómetro de "tiempo en esta pregunta" al entrar a una nueva pregunta.
  useEffect(() => {
    segmentStartRef.current = Date.now();
  }, [currentIndex]);

  // Countdown de 2h20m, con auto-submit al llegar a 0.
  useEffect(() => {
    if (phase !== "in_progress" || deadline === 0) return;
    const tick = () => {
      const left = deadline - Date.now();
      setRemainingMs(Math.max(0, left));
      if (left <= 0) {
        doSubmit();
      }
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [phase, deadline, doSubmit]);

  // Atajos de teclado: ← → para navegar, 1-4/A-D para responder, Enter para avanzar.
  useEffect(() => {
    if (phase !== "in_progress") return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "ArrowRight" || e.key === "Enter") {
        e.preventDefault();
        goToQuestion(currentIndex + 1);
      } else if (e.key === "ArrowLeft") {
        e.preventDefault();
        goToQuestion(currentIndex - 1);
      } else if (currentQuestion) {
        const digit = Number(e.key);
        let altIndex = -1;
        if (digit >= 1 && digit <= currentQuestion.alternatives.length) altIndex = digit - 1;
        else {
          const letterIndex = LABELS.indexOf(e.key.toUpperCase());
          if (letterIndex >= 0 && letterIndex < currentQuestion.alternatives.length)
            altIndex = letterIndex;
        }
        if (altIndex >= 0) {
          e.preventDefault();
          selectAlternative(currentQuestion.alternatives[altIndex].id);
        }
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [phase, currentIndex, currentQuestion, goToQuestion, selectAlternative]);

  async function handleStart() {
    setPhase("loading");
    setErrorMsg(null);
    setResult(null);
    setWeakNodes(null);
    try {
      const data = await startExam(getClientToken() ?? undefined);
      localStorage.setItem(STORAGE_KEY, String(data.attempt_id));
      setAttemptId(data.attempt_id);
      setQuestions(data.questions);
      setDeadline(new Date(data.started_at).getTime() + data.duration_limit_seconds * 1000);
      setRemainingMs(data.duration_limit_seconds * 1000);
      setCurrentIndex(0);
      setSelections({});
      setElapsedByQuestion({});
      segmentStartRef.current = Date.now();
      setPhase("in_progress");
    } catch {
      setErrorMsg("No se pudo iniciar el examen. Verifica que la API esté disponible.");
      setPhase("error");
    }
  }

  async function handlePrimaryAction() {
    if (resumableAttemptId != null) {
      await resumeAttempt(resumableAttemptId);
    } else {
      await handleStart();
    }
  }

  const answeredCount = useMemo(
    () => Object.values(selections).filter((v) => v != null).length,
    [selections]
  );

  if (phase === "idle" || phase === "error") {
    return (
      <StartScreen
        onStart={handlePrimaryAction}
        errorMsg={errorMsg}
        pastAttempts={pastAttempts}
        resumable={resumableAttemptId != null}
      />
    );
  }

  if (phase === "loading") {
    return (
      <div className="flex flex-1 items-center justify-center py-24 text-sm text-muted">
        Cargando…
      </div>
    );
  }

  if (phase === "submitted" && result) {
    return <ResultScreen result={result} weakNodes={weakNodes} />;
  }

  if (!currentQuestion) return null;

  const low = remainingMs < 5 * 60 * 1000;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-border bg-surface px-4 py-3">
        <span className="text-sm text-muted">
          Pregunta <span className="text-foreground">{currentIndex + 1}</span> de{" "}
          {questions.length} · {answeredCount} respondidas
        </span>
        <span
          className={cn(
            "font-mono text-lg font-semibold tabular-nums",
            low ? "text-danger" : "text-foreground"
          )}
        >
          {formatClock(remainingMs)}
        </span>
        {confirmingSubmit ? (
          <div className="flex items-center gap-2 text-sm">
            <span className="text-muted">¿Enviar y finalizar?</span>
            <button
              onClick={doSubmit}
              disabled={submitting}
              className="rounded-md bg-danger px-3 py-1.5 font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "Enviando…" : "Sí, finalizar"}
            </button>
            <button
              onClick={() => setConfirmingSubmit(false)}
              disabled={submitting}
              className="rounded-md border border-border px-3 py-1.5 text-muted hover:bg-surface-hover disabled:cursor-not-allowed disabled:opacity-60"
            >
              Cancelar
            </button>
          </div>
        ) : (
          <button
            onClick={() => setConfirmingSubmit(true)}
            className="rounded-lg border border-border px-3 py-1.5 text-sm font-medium hover:bg-surface-hover"
          >
            Finalizar examen
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_220px]">
        <div className="rounded-xl border border-border bg-surface p-6">
          <span className="text-xs font-medium text-muted">
            {currentQuestion.difficulty === "facil"
              ? "Fácil"
              : currentQuestion.difficulty === "medio"
                ? "Medio"
                : "Difícil"}
          </span>
          <p className="mt-2 text-base leading-relaxed text-foreground">
            {currentQuestion.stem}
          </p>

          <div className="mt-6 flex flex-col gap-2.5">
            {currentQuestion.alternatives.map((alt, i) => {
              const selected = selections[currentQuestion.id] === alt.id;
              return (
                <button
                  key={alt.id}
                  onClick={() => selectAlternative(alt.id)}
                  className={cn(
                    "flex items-start gap-3 rounded-lg border px-4 py-3 text-left text-sm transition-colors",
                    selected
                      ? "border-accent bg-accent/10 text-foreground"
                      : "border-border bg-background text-foreground hover:border-border-strong hover:bg-surface-hover"
                  )}
                >
                  <span
                    className={cn(
                      "flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[11px] font-medium",
                      selected
                        ? "border-accent bg-accent text-accent-foreground"
                        : "border-border-strong text-muted"
                    )}
                  >
                    {LABELS[i]}
                  </span>
                  <span>{alt.text}</span>
                </button>
              );
            })}
          </div>

          <div className="mt-6 flex items-center justify-between">
            <button
              onClick={() => goToQuestion(currentIndex - 1)}
              disabled={currentIndex === 0}
              className="rounded-lg border border-border px-4 py-2 text-sm font-medium hover:bg-surface-hover disabled:pointer-events-none disabled:opacity-40"
            >
              ← Anterior
            </button>
            <span className="hidden text-xs text-muted sm:inline">
              Atajos: ← → para navegar · 1-4 para responder · Enter para avanzar
            </span>
            <button
              onClick={() => goToQuestion(currentIndex + 1)}
              disabled={currentIndex === questions.length - 1}
              className="btn-glow rounded-lg px-4 py-2 text-sm font-medium text-accent-foreground disabled:pointer-events-none disabled:opacity-40"
            >
              Siguiente →
            </button>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-surface p-4">
          <p className="text-xs font-medium text-muted">Navegador</p>
          <div className="mt-3 grid grid-cols-6 gap-1.5 lg:grid-cols-5">
            {questions.map((q, i) => {
              const answered = selections[q.id] != null;
              const active = i === currentIndex;
              return (
                <button
                  key={q.id}
                  onClick={() => goToQuestion(i)}
                  className={cn(
                    "flex h-8 w-8 items-center justify-center rounded-md text-xs font-medium transition-colors",
                    active
                      ? "bg-accent text-accent-foreground"
                      : answered
                        ? "bg-success/15 text-success hover:bg-success/25"
                        : "bg-surface-hover text-muted hover:text-foreground"
                  )}
                >
                  {i + 1}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

const ATTEMPT_DATE_FMT = new Intl.DateTimeFormat("es-CL", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

function StartScreen({
  onStart,
  errorMsg,
  pastAttempts,
  resumable,
}: {
  onStart: () => void;
  errorMsg: string | null;
  pastAttempts: ExamAttemptSummary[];
  resumable: boolean;
}) {
  return (
    <div className="mx-auto flex max-w-lg flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10 text-accent">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="13" r="8" />
          <path d="M12 9v4l3 2M9 2h6M12 2v2" />
        </svg>
      </div>
      <h1 className="mt-5 text-xl font-semibold">Modo Examen Focus</h1>
      <p className="mt-2 max-w-sm text-sm text-muted">
        Simulacro cronometrado de 2 horas 20 minutos, con todas las preguntas
        del banco actual. Tu progreso se guarda automáticamente: puedes recargar
        la página sin perder tus respuestas.
      </p>
      <ul className="mt-5 flex flex-col gap-1.5 text-left text-xs text-muted">
        <li>← → para moverte entre preguntas</li>
        <li>1-4 (o A-D) para elegir una alternativa</li>
        <li>Enter para avanzar a la siguiente</li>
      </ul>
      {resumable && (
        <p className="mt-4 rounded-lg border border-accent/40 bg-accent/10 px-3 py-2 text-xs text-foreground">
          Tienes un simulacro en curso sin finalizar. Al continuar retomas
          justo donde quedaste.
        </p>
      )}
      {errorMsg && (
        <p className="mt-4 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-xs text-danger">
          {errorMsg}
        </p>
      )}
      <button onClick={onStart} className="btn-glow mt-6 rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground">
        {resumable ? "Continuar simulacro" : "Comenzar simulacro"}
      </button>

      {pastAttempts.length > 0 && (
        <div className="mt-10 w-full text-left">
          <p className="text-xs font-medium text-muted">Simulacros anteriores</p>
          <div className="mt-2 flex flex-col gap-1.5">
            {pastAttempts.slice(0, 5).map((a) => {
              const pct = a.total_questions
                ? Math.round((a.correct / a.total_questions) * 100)
                : 0;
              return (
                <Link
                  key={a.attempt_id}
                  href={`/feedback?attempt=${a.attempt_id}`}
                  className="flex items-center justify-between rounded-lg border border-border bg-background px-3 py-2 text-xs transition-colors hover:border-border-strong hover:bg-surface-hover"
                >
                  <span className="text-muted" suppressHydrationWarning>
                    {ATTEMPT_DATE_FMT.format(new Date(a.started_at))}
                  </span>
                  <span className="font-medium text-foreground">
                    {a.correct}/{a.total_questions} · {pct}%
                  </span>
                </Link>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

function ResultScreen({
  result,
  weakNodes,
}: {
  result: ExamResult;
  weakNodes: NodeDiagnosis[] | null;
}) {
  const pct = result.total_questions
    ? Math.round((result.correct / result.total_questions) * 100)
    : 0;
  return (
    <div className="mx-auto flex max-w-lg flex-col items-center rounded-2xl border border-border bg-surface px-6 py-16 text-center">
      <span className="text-5xl font-semibold tracking-tight text-gradient">{pct}%</span>
      <p className="mt-2 text-sm text-muted">
        {result.correct} de {result.total_questions} correctas ·{" "}
        {result.answered} respondidas
      </p>
      <p className="mt-1 text-xs text-muted">
        Tiempo usado: {formatClock(result.elapsed_seconds * 1000)}
      </p>

      {weakNodes && weakNodes.length > 0 && (
        <div className="mt-8 w-full text-left">
          <p className="text-xs font-medium text-muted">Tus nodos más débiles</p>
          <div className="mt-2 flex flex-col gap-1.5">
            {weakNodes.map((n) => (
              <div
                key={n.skill_node_id}
                className="flex items-center justify-between rounded-lg border border-border bg-background px-3 py-2 text-xs"
              >
                <span className="text-foreground">{n.skill_node_name}</span>
                <span className="text-muted">
                  {n.correct}/{n.total} · {Math.round(n.accuracy * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
        <Link
          href={`/feedback?attempt=${result.attempt_id}`}
          className="btn-glow rounded-lg px-5 py-2.5 text-sm font-medium text-accent-foreground"
        >
          Ver diagnóstico completo
        </Link>
        <Link
          href="/arbol"
          className="rounded-lg border border-border px-5 py-2.5 text-sm font-medium hover:bg-surface-hover"
        >
          Ir al Árbol de Habilidades
        </Link>
      </div>
    </div>
  );
}
