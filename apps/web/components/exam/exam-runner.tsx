"use client";

import { usePathname, useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { cn } from "@paes-m1/utils";
import { PassagePanel } from "@/components/exam/passage-panel";
import { Burbuja } from "@/components/ui/burbuja";
import { TextoRico } from "@/components/texto-rico";
import { ExamConfigScreen, SUBJECT_LABELS } from "@/components/exam/exam-config";
import { ExamResults } from "@/components/exam/exam-results";
import { LimiteAlcanzado } from "@/components/exam/limite-alcanzado";
import { QuestionNavigator } from "@/components/exam/question-navigator";
import { RelojPregunta } from "@/components/exam/reloj-pregunta";
import {
  ApiError,
  answerExamQuestion,
  getExamReview,
  getExamState,
  startExam,
  submitExam,
  type ExamAttemptSummary,
  type ExamConfig,
  type ExamOptions,
  type ExamQuestion,
  type ExamResult,
  type ExamReview,
  type Repaso,
  type Subject,
} from "@/lib/api";
import { getClientToken, loginHref } from "@/lib/auth";
import { COLOR_PRUEBA } from "@/lib/colores-prueba";
import { formatearReloj } from "@/lib/tiempo";

const STORAGE_KEY = "paes_exam_attempt_id";
const LABELS = ["A", "B", "C", "D", "E"];

type Phase = "config" | "loading" | "in_progress" | "submitted" | "limite";

interface AnswerState {
  selected: number | null;
  flagged: boolean;
}

interface ResumableAttempt {
  attemptId: number;
  subject: Subject;
}

interface ExamRunnerProps {
  optionsBySubject: Record<Subject, ExamOptions>;
  pastAttempts: ExamAttemptSummary[];
  resumable: ResumableAttempt | null;
  repasoBySubject: Record<Subject, Repaso>;
  //: Cuota de ensayos del mes, para avisarle al alumno ANTES de que choque.
  //: Llega desde el servidor para no hacer otra llamada al montar.
  cuota?: { usados: number; limite: number | null; activa: boolean } | null;
}

export function ExamRunner({
  optionsBySubject,
  pastAttempts,
  resumable,
  repasoBySubject,
  cuota,
}: ExamRunnerProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [phase, setPhase] = useState<Phase>("config");
  const [attemptId, setAttemptId] = useState<number | null>(null);
  const [attemptSubject, setAttemptSubject] = useState<Subject>("m1");
  const [questions, setQuestions] = useState<ExamQuestion[]>([]);
  const [deadline, setDeadline] = useState<number>(0);
  //: Milisegundos gastados en la pregunta que está a la vista.
  const [msEnPregunta, setMsEnPregunta] = useState(0);
  //: Duración total concedida al intento, para repartirla entre preguntas.
  const [duracionMs, setDuracionMs] = useState(0);
  const [remainingMs, setRemainingMs] = useState(0);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, AnswerState>>({});
  // El tiempo acumulado por pregunta vive en un ref y no en estado, y no es
  // un detalle: estaba en estado, se asignaba DENTRO del updater de setState y
  // se leía justo después, fuera. Como el updater es asíncrono, lo que viajaba
  // a la API era siempre el valor inicial: las 132 respuestas de producción
  // tenían time_spent_ms = 0. Nadie había medido nunca el ritmo de nadie.
  //
  // Un ref es además la herramienta correcta: este valor no se pinta en
  // ninguna parte, así que no tiene por qué provocar un render.
  const elapsedRef = useRef<Record<number, number>>({});
  const [result, setResult] = useState<ExamResult | null>(null);
  const [review, setReview] = useState<ExamReview | null>(null);
  const [confirmingSubmit, setConfirmingSubmit] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  //: Motivo exacto que devuelve la API al tocar el tope del plan. Se muestra
  //: literal para que el alumno vea el número real, no una frase genérica.
  const [limiteMotivo, setLimiteMotivo] = useState<string | null>(null);

  /** Preguntas cuya respuesta NO alcanzó a llegar al servidor.
   *
   *  El autoguardado era best-effort y su error se tragaba en silencio: si
   *  fallaba la red justo al contestar la 5 y el alumno seguía a la 6, esa
   *  respuesta no se reintentaba nunca. La veía marcada en pantalla --el
   *  estado es local-- y el ensayo se corregía sin ella. Puntaje perdido sin
   *  ningún aviso, que en un celular con señal intermitente no es raro. */
  const pendientesRef = useRef<Set<number>>(new Set());
  const [sinGuardar, setSinGuardar] = useState(0);

  const segmentStartRef = useRef(0);
  const attemptIdRef = useRef<number | null>(null);
  const answersRef = useRef(answers);
  answersRef.current = answers;

  useEffect(() => {
    attemptIdRef.current = attemptId;
  }, [attemptId]);

  const currentQuestion = questions[currentIndex] as ExamQuestion | undefined;

  /**
   * Las preguntas agrupadas en páginas.
   *
   * Una página es un texto con todas sus preguntas, que es como se rinde
   * Competencia Lectora. Las preguntas sin texto asociado —matemática,
   * ciencias, historia sin fuente— quedan cada una en su propia página, o
   * sea que para esas pruebas nada cambia.
   */
  const paginas = useMemo(() => {
    const out: number[][] = [];
    questions.forEach((q, i) => {
      const clave = q.passage?.id ?? null;
      const anterior = i > 0 ? (questions[i - 1].passage?.id ?? null) : null;
      if (clave !== null && clave === anterior) out[out.length - 1].push(i);
      else out.push([i]);
    });
    return out;
  }, [questions]);

  const paginaActual = useMemo(
    () => Math.max(0, paginas.findIndex((p) => p.includes(currentIndex))),
    [paginas, currentIndex]
  );

  /** Manda una respuesta al servidor y anota si no llegó.
   *
   *  Separado de `flush` porque un reintento NO debe volver a sumar tiempo:
   *  reenvía el acumulado que ya se calculó la primera vez. */
  const enviar = useCallback(
    (
      questionId: number,
      selected: number | null,
      flagged: boolean,
      totalMs: number
    ): Promise<void> => {
      const id = attemptIdRef.current;
      if (id == null) return Promise.resolve();
      return answerExamQuestion(
        id,
        questionId,
        selected,
        totalMs,
        flagged,
        getClientToken() ?? undefined
      ).then(
        () => {
          pendientesRef.current.delete(questionId);
          setSinGuardar(pendientesRef.current.size);
        },
        (err) => {
          if (err instanceof ApiError && err.status === 401) {
            router.push(loginHref(pathname));
            return;
          }
          pendientesRef.current.add(questionId);
          setSinGuardar(pendientesRef.current.size);
        }
      );
    },
    [router, pathname]
  );

  /** Reintenta todo lo que quedó sin guardar. */
  const reintentarPendientes = useCallback(async () => {
    const ids = [...pendientesRef.current];
    await Promise.all(
      ids.map((qid) => {
        const estado = answersRef.current[qid];
        return enviar(
          qid,
          estado?.selected ?? null,
          estado?.flagged ?? false,
          elapsedRef.current[qid] ?? 0
        );
      })
    );
  }, [enviar]);

  /** Guarda una respuesta. Los valores se pasan explícitos porque al llamarlo
   *  justo después de un setState el estado todavía no se ha actualizado. */
  const flush = useCallback(
    (questionId: number, selected: number | null, flagged: boolean): Promise<void> => {
      const now = Date.now();
      const delta = now - segmentStartRef.current;
      segmentStartRef.current = now;
      const id = attemptIdRef.current;
      if (id == null) return Promise.resolve();

      const total = (elapsedRef.current[questionId] ?? 0) + Math.max(0, delta);
      elapsedRef.current[questionId] = total;

      return enviar(questionId, selected, flagged, total);
    },
    [enviar]
  );

  const goToQuestion = useCallback(
    (index: number) => {
      if (index < 0 || index >= questions.length || index === currentIndex) return;
      const q = questions[currentIndex];
      if (q) {
        const estado = answersRef.current[q.id];
        flush(q.id, estado?.selected ?? null, estado?.flagged ?? false);
      }
      setCurrentIndex(index);
    },
    [currentIndex, questions, flush]
  );

  /** Salta al primer enunciado de otra página y sube al texto. */
  const irAPagina = useCallback(
    (p: number) => {
      const destino = paginas[p];
      if (!destino) return;
      goToQuestion(destino[0]);
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
    [paginas, goToQuestion]
  );

  // Reintenta solo, mientras rinde. Una caída de señal en el metro dura
  // segundos: si se recupera sola, el alumno nunca se entera de que pasó algo,
  // que es como debe ser. El aviso de la cabecera es para cuando NO se
  // recupera.
  useEffect(() => {
    if (phase !== "in_progress" || sinGuardar === 0) return;
    const t = setInterval(() => {
      void reintentarPendientes();
    }, 15000);
    return () => clearInterval(t);
  }, [phase, sinGuardar, reintentarPendientes]);

  //: Pregunta a la que hay que bajar en cuanto exista en el DOM. Se guarda
  //: en un ref porque al saltar desde la cuadrícula la pregunta puede estar
  //: en otra página y todavía no estar montada cuando se pide el scroll.
  const scrollPendienteRef = useRef<number | null>(null);

  /** Salta a una pregunta concreta desde la cuadrícula y la trae a la vista. */
  const irAPregunta = useCallback(
    (index: number) => {
      scrollPendienteRef.current = index;
      goToQuestion(index);
    },
    [goToQuestion]
  );

  useEffect(() => {
    const objetivo = scrollPendienteRef.current;
    if (objetivo == null) return;
    scrollPendienteRef.current = null;
    document
      .getElementById(`pregunta-${objetivo}`)
      ?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [currentIndex]);

  const selectAlternative = useCallback(
    (altId: number, questionId?: number) => {
      const qid = questionId ?? currentQuestion?.id;
      if (qid == null) return;
      const actual = answersRef.current[qid] ?? { selected: null, flagged: false };
      // Volver a tocar la alternativa marcada la deselecciona: en la PAES
      // dejar en blanco no penaliza, así que debe ser posible retractarse.
      const selected = actual.selected === altId ? null : altId;
      setAnswers((prev) => ({ ...prev, [qid]: { ...actual, selected } }));
      flush(qid, selected, actual.flagged);
    },
    [currentQuestion, flush]
  );

  const toggleFlag = useCallback((questionId?: number) => {
    const qid = questionId ?? currentQuestion?.id;
    if (qid == null) return;
    const actual = answersRef.current[qid] ?? { selected: null, flagged: false };
    const flagged = !actual.flagged;
    setAnswers((prev) => ({ ...prev, [qid]: { ...actual, flagged } }));
    flush(qid, actual.selected, flagged);
  }, [currentQuestion, flush]);

  const loadResult = useCallback(async (id: number) => {
    const token = getClientToken() ?? undefined;
    const res = await submitExam(id, token);
    setResult(res);
    setPhase("submitted");
    // El modal de confirmación cumplió su función: si no se baja acá queda en
    // true para siempre (solo "Seguir" lo bajaba), y reaparece solo al empezar
    // el siguiente ensayo, encima de la pregunta 1.
    setConfirmingSubmit(false);
    localStorage.removeItem(STORAGE_KEY);
    // Mejor esfuerzo: si falla, se muestra el puntaje sin la revisión.
    getExamReview(id, token)
      .then(setReview)
      .catch(() => {});
  }, []);

  const doSubmit = useCallback(async () => {
    const id = attemptIdRef.current;
    if (id == null || submitting) return;
    setSubmitting(true);
    try {
      // Espera a que la última respuesta quede guardada ANTES de enviar el
      // submit — si se disparan en paralelo, el submit puede llegar primero
      // y el answer subsiguiente falla con 409 (intento ya finalizado).
      if (currentQuestion) {
        const estado = answersRef.current[currentQuestion.id];
        await flush(currentQuestion.id, estado?.selected ?? null, estado?.flagged ?? false);
      }

      // Última oportunidad para lo que quedó sin guardar. Si sigue sin subir,
      // NO se envía: corregir el ensayo sin esas respuestas le baja el puntaje
      // por un problema de red, y encima quedaría como si las hubiera omitido.
      await reintentarPendientes();
      if (pendientesRef.current.size > 0) {
        setErrorMsg(
          `No pudimos guardar ${pendientesRef.current.size} ${
            pendientesRef.current.size === 1 ? "respuesta" : "respuestas"
          }. Revisa tu conexión y vuelve a enviar: tus respuestas siguen acá.`
        );
        setConfirmingSubmit(false);
        return;
      }

      await loadResult(id);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push(loginHref(pathname));
        return;
      }
      setErrorMsg("No se pudo enviar el ensayo. Revisa tu conexión e intenta de nuevo.");
    } finally {
      setSubmitting(false);
    }
  }, [currentQuestion, flush, reintentarPendientes, loadResult, router, pathname, submitting]);

  const resumeAttempt = useCallback(async (id: number) => {
    setPhase("loading");
    try {
      const state = await getExamState(id, getClientToken() ?? undefined);
      if (state.status !== "in_progress") {
        localStorage.removeItem(STORAGE_KEY);
        setPhase("config");
        return;
      }
      localStorage.setItem(STORAGE_KEY, String(id));
      setAttemptId(id);
      setAttemptSubject(state.config.subject);
      setQuestions(state.questions);
      setDeadline(
        new Date(state.started_at).getTime() + state.duration_limit_seconds * 1000
      );
      setDuracionMs(state.duration_limit_seconds * 1000);
      const next: Record<number, AnswerState> = {};
      const elap: Record<number, number> = {};
      for (const [qid, ans] of Object.entries(state.answers)) {
        next[Number(qid)] = {
          selected: ans.selected_alternative_id ?? null,
          flagged: ans.flagged ?? false,
        };
        elap[Number(qid)] = ans.time_spent_ms ?? 0;
      }
      setAnswers(next);
      elapsedRef.current = elap;
      setCurrentIndex(0);
      segmentStartRef.current = Date.now();
      setPhase("in_progress");
    } catch {
      localStorage.removeItem(STORAGE_KEY);
      setPhase("config");
    }
  }, []);

  // Resumir un ensayo en curso al montar: primero localStorage (mismo
  // navegador), y si no hay nada, un intento in_progress que el servidor ya
  // sabe que es nuestro (ej. se limpió el localStorage o es otro dispositivo)
  // — así nunca se crean intentos duplicados sin querer.
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    const id = saved ? Number(saved) : null;
    if (id == null || !Number.isFinite(id)) return;
    // Fetch de datos al montar: resumeAttempt marca "loading" antes del await,
    // patrón estándar de carga inicial.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    resumeAttempt(id);
  }, [resumeAttempt]);

  // Advertencia al cerrar/recargar la pestaña con un ensayo en curso.
  useEffect(() => {
    if (phase !== "in_progress") return;
    function onBeforeUnload(e: BeforeUnloadEvent) {
      e.preventDefault();
    }
    window.addEventListener("beforeunload", onBeforeUnload);
    return () => window.removeEventListener("beforeunload", onBeforeUnload);
  }, [phase]);

  // Reset del cronómetro de "tiempo en esta pregunta" al cambiar de pregunta.
  useEffect(() => {
    segmentStartRef.current = Date.now();
  }, [currentIndex]);

  // Al cambiar de pantalla se vuelve arriba: sin esto, la revisión de
  // resultados se abre a media página.
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [phase]);

  // Countdown con auto-envío al llegar a 0. Se calcula contra la hora límite
  // en lugar de restar 1 cada segundo, porque los navegadores ralentizan los
  // intervalos en pestañas inactivas y el conteo se desincronizaría.
  useEffect(() => {
    if (phase !== "in_progress" || deadline === 0) return;
    const tick = () => {
      const left = deadline - Date.now();
      setRemainingMs(Math.max(0, left));
      if (left <= 0) doSubmit();
    };
    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [phase, deadline, doSubmit]);

  // Cuánto lleva el alumno en la pregunta que está mirando.
  //
  // Va aparte del countdown general porque depende de la pregunta actual: si
  // viviera dentro de aquel efecto, cuyas dependencias son otras, leería un
  // índice viejo y el reloj se quedaría marcando la pregunta anterior.
  //
  // El acumulado sale del ref (visitas anteriores a esta misma pregunta) más
  // el segmento en curso. Es exactamente el número que se guarda al responder,
  // así que lo que ve en pantalla es lo que después le cuenta el diagnóstico.
  useEffect(() => {
    if (phase !== "in_progress") return;
    const actual = questions[currentIndex]?.id;
    if (actual == null) return;
    const tick = () =>
      setMsEnPregunta(
        (elapsedRef.current[actual] ?? 0) + Math.max(0, Date.now() - segmentStartRef.current)
      );
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [phase, currentIndex, questions]);

  // Atajos: A-D (o 1-4) para responder, flechas para navegar.
  useEffect(() => {
    if (phase !== "in_progress") return;
    function onKeyDown(e: KeyboardEvent) {
      if (e.target instanceof HTMLInputElement) return;
      if (e.key === "ArrowRight") {
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

  async function handleStart(config: ExamConfig) {
    setPhase("loading");
    setErrorMsg(null);
    setResult(null);
    setReview(null);
    try {
      const data = await startExam(config, getClientToken() ?? undefined);
      localStorage.setItem(STORAGE_KEY, String(data.attempt_id));
      setAttemptId(data.attempt_id);
      setAttemptSubject(data.config.subject);
      setQuestions(data.questions);
      setDeadline(new Date(data.started_at).getTime() + data.duration_limit_seconds * 1000);
      setDuracionMs(data.duration_limit_seconds * 1000);
      setRemainingMs(data.duration_limit_seconds * 1000);
      setCurrentIndex(0);
      setAnswers({});
      elapsedRef.current = {};
      segmentStartRef.current = Date.now();
      setPhase("in_progress");
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push(loginHref(pathname));
        return;
      }
      // 409 con motivo es el tope del plan, no una falla. Mezclarlos hacía que
      // el alumno viera un error técnico donde había una decisión de producto.
      if (err instanceof ApiError && err.status === 409 && err.detail) {
        setLimiteMotivo(err.detail);
        setPhase("limite");
        return;
      }
      setErrorMsg("No se pudo iniciar el ensayo. Verifica que la API esté disponible.");
      setPhase("config");
    }
  }

  const respondidas = useMemo(
    () => Object.values(answers).filter((a) => a.selected != null).length,
    [answers]
  );

  if (phase === "limite") {
    return (
      <LimiteAlcanzado
        motivo={limiteMotivo ?? "Llegaste al límite de ensayos de tu plan."}
        onVolver={() => {
          setLimiteMotivo(null);
          setPhase("config");
        }}
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
    return (
      <ExamResults
        result={result}
        review={review}
        prueba={SUBJECT_LABELS[attemptSubject]}
        onNuevoEnsayo={() => {
          setResult(null);
          setReview(null);
          setAttemptId(null);
          setPhase("config");
          router.refresh();
        }}
      />
    );
  }

  if (phase === "config" || !currentQuestion) {
    return (
      <ExamConfigScreen
        optionsBySubject={optionsBySubject}
        repasoBySubject={repasoBySubject}
        ensayosRendidos={pastAttempts.length}
        cuota={cuota}
        resumable={resumable}
        errorMsg={errorMsg}
        onComenzar={handleStart}
        onContinuar={() => resumable != null && resumeAttempt(resumable.attemptId)}
      />
    );
  }

  // El reloj avisa antes de asustar. Ámbar a los diez minutos, rojo con
  // latido a los cinco: el estudiante alcanza a reorganizarse en vez de
  // descubrir el apuro cuando ya no puede hacer nada. Son umbrales absolutos
  // y no proporcionales porque lo que importa es cuánto queda, no qué
  // fracción: cinco minutos son cinco minutos en un ensayo de 20 o de 65.
  // El último minuto es su propio estado: es el que decide si alcanzas a
  // marcar las que dejaste pendientes, y se veía igual que el minuto cuatro.
  const ultimoMinuto = remainingMs <= 60 * 1000;
  const critico = remainingMs <= 5 * 60 * 1000;
  const aviso = !critico && remainingMs <= 10 * 60 * 1000;
  const sinResponder = questions.length - respondidas;
  const indicesPagina = paginas[paginaActual] ?? [currentIndex];
  const textoPagina = questions[indicesPagina[0]]?.passage ?? null;
  const variasEnLaPagina = indicesPagina.length > 1;

  return (
    <div className="mx-auto max-w-3xl">
      {/* ── Barra superior ──────────────────────────────────────────── */}
      {/* La franja de arriba dice de qué prueba es este ensayo sin ocupar una
          palabra, con el mismo color que usan el titular de la portada, el
          selector y el árbol. Dentro del ensayo el color no puede hacer más
          que esto: lo demás es papel y grafito, porque acá el verde y el rojo
          están reservados para la corrección. */}
      <header
        className="glass sticky top-14 z-20 -mx-4 border-t-2 px-4 sm:-mx-6 sm:px-6"
        style={{ borderTopColor: COLOR_PRUEBA[attemptSubject] }}
      >
        {/* Dos relojes y un contador juntos no se explican solos: quien entra
            por primera vez no tiene cómo saber cuál es cuál. Cada uno lleva su
            etiqueta encima.

            En el teléfono van en su propia fila bajo el número de pregunta:
            con etiquetas ya no caben los cuatro en una sola. */}
        <div className="flex flex-col gap-2 py-3 sm:flex-row sm:items-start sm:gap-3">
          <div className="min-w-0 flex-1">
            <p className="hidden truncate text-xs text-muted sm:block">
              {SUBJECT_LABELS[attemptSubject]}
            </p>
            <p className="font-semibold">
              {variasEnLaPagina
                ? `Texto ${paginaActual + 1} de ${paginas.length} · preguntas ${
                    indicesPagina[0] + 1
                  } a ${indicesPagina[indicesPagina.length - 1] + 1}`
                : `Pregunta ${currentIndex + 1} de ${questions.length}`}
            </p>
          </div>

          <div className="flex items-start gap-2 sm:gap-3">
            <Medidor
              etiqueta="Tiempo restante de la prueba"
              detalle="Cuánto queda para que se cierre el ensayo completo."
            >
              <span
                className={cn(
                  "block rounded-lg px-2.5 py-1 font-mono text-lg font-bold tabular-nums transition-colors duration-700",
                  critico && !ultimoMinuto && "bg-danger/10 text-danger pulso-reloj",
                  ultimoMinuto && "bg-danger/15 text-danger pulso-reloj-final",
                  aviso && "bg-warning/10 text-warning",
                  !critico && !aviso && "bg-surface-hover"
                )}
                role="timer"
                aria-live={critico ? "polite" : "off"}
                aria-label="Tiempo restante del ensayo completo"
              >
                {formatearReloj(remainingMs)}
              </span>
            </Medidor>

            {/* El presupuesto lo calcula el servidor POR PREGUNTA: una difícil
                pesa más que una fácil, y en Lectora la primera de cada texto
                carga con leerlo. Si viniera en cero --un intento anterior a
                esta función-- se cae al reparto plano, que es lo que había. */}
            <Medidor
              etiqueta="Tiempo en esta pregunta"
              detalle="Cuánto llevas en la pregunta que tienes al frente, y cuánto debería tomarte."
            >
              <RelojPregunta
                msGastados={msEnPregunta}
                msPresupuesto={
                  (questions[currentIndex]?.suggested_seconds ||
                    (questions.length > 0 ? duracionMs / questions.length / 1000 : 0)) * 1000
                }
              />
            </Medidor>

            <Medidor
              etiqueta="Preguntas respondidas"
              detalle="Cuántas llevas contestadas del total del ensayo."
            >
              <span className="block rounded-lg border border-border px-2.5 py-1 text-lg font-medium tabular-nums">
                {respondidas}/{questions.length}
              </span>
            </Medidor>
          </div>
        </div>

        {/* Que se sepa mientras pasa, no al enviar. Si se recupera solo, esto
            desaparece y el alumno nunca supo que hubo un problema. */}
        {sinGuardar > 0 && (
          <p
            role="status"
            className="mb-2 rounded-lg border border-warning/40 bg-warning/10 px-3 py-1.5 text-xs text-warning"
          >
            {sinGuardar === 1
              ? "Una respuesta no se ha guardado"
              : `${sinGuardar} respuestas no se han guardado`}
            . Estamos reintentando; sigue respondiendo.
          </p>
        )}

        <div className="-mx-4 h-1 w-[calc(100%+2rem)] bg-surface-hover sm:-mx-6 sm:w-[calc(100%+3rem)]">
          <div
            className="h-full rounded-r-full transition-[width] duration-500 ease-out"
            style={{
              width: `${(respondidas / questions.length) * 100}%`,
              background: "linear-gradient(90deg, var(--accent), var(--accent-2))",
            }}
          />
        </div>
      </header>

      <QuestionNavigator
        items={questions.map((q) => ({
          id: q.id,
          answered: answers[q.id]?.selected != null,
          flagged: answers[q.id]?.flagged ?? false,
        }))}
        currentIndex={currentIndex}
        onSelect={irAPregunta}
      />

      {/* ── Pregunta ────────────────────────────────────────────────── */}
      {/* pb generoso: deja aire para que la pastilla flotante del navegador
          no tape el final del contenido. */}
      <main className="py-6 pb-24">
        {/* El texto va UNA vez, arriba de todas sus preguntas, como en la
            prueba de papel. Antes se repetia encima de cada pregunta y
            obligaba a releerlo nueve veces. */}
        {textoPagina && (
          <div className="mb-5">
            <PassagePanel passage={textoPagina} />
          </div>
        )}

        <div className="space-y-5">
          {indicesPagina.map((idx) => {
            const q = questions[idx];
            if (!q) return null;
            const est = answers[q.id];
            return (
              <article
                key={q.id}
                id={`pregunta-${idx}`}
                className="scroll-mt-32 rounded-xl border border-border bg-surface p-5"
              >
                <div className="mb-3 flex items-start justify-between gap-3">
                  <span className="rounded-full bg-surface-hover px-2.5 py-1 text-xs font-medium text-muted">
                    {variasEnLaPagina
                      ? `Pregunta ${idx + 1}`
                      : q.axis || q.skill_node_name}
                  </span>
                  <button
                    type="button"
                    onClick={() => toggleFlag(q.id)}
                    className={cn(
                      "shrink-0 rounded-lg border px-3 py-1.5 text-xs font-medium transition",
                      est?.flagged
                        ? "border-warning/50 bg-warning/10 text-warning"
                        : "border-border text-muted hover:bg-surface-hover"
                    )}
                  >
                    {/* La estrella rebota al marcarse. Es una microacción que
                        se repite decenas de veces en un ensayo y era muda: el
                        único acuse de recibo era el cambio de color. */}
                    <motion.span
                      key={est?.flagged ? "si" : "no"}
                      initial={{ scale: est?.flagged ? 0.6 : 1 }}
                      animate={{ scale: 1 }}
                      transition={{ type: "spring", stiffness: 500, damping: 15 }}
                      className="inline-block"
                    >
                      {est?.flagged ? "★ Marcada" : "☆ Marcar"}
                    </motion.span>
                  </button>
                </div>

                {/* La segunda oportunidad. Con miles de preguntas sorteadas al
                    azar, reencontrarse con una que uno falló es la mejor
                    ocasión de aprender que da la plataforma, y pasaba
                    completamente desapercibida.

                    Va ANTES del enunciado y no después: sirve para leer con
                    más cuidado, no para lamentarse. Y no dice qué se respondió
                    ni cuál era la correcta —eso sería regalar la respuesta—,
                    solo que en algún momento esta pregunta se le escapó. */}
                {q.fallada_antes && (
                  <p className="mb-3 flex items-center gap-2 rounded-lg border border-accent-warm/40 bg-accent-warm/5 px-3 py-2 text-sm text-accent-warm-strong">
                    <svg
                      width="15"
                      height="15"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                      className="shrink-0"
                    >
                      <path d="M3 12a9 9 0 1 0 3-6.7L3 8" />
                      <path d="M3 3v5h5" />
                    </svg>
                    <span>
                      <strong className="font-semibold">Ya te equivocaste en esta pregunta.</strong>{" "}
                      Léela con calma: es tu oportunidad de corregirlo.
                    </span>
                  </p>
                )}

                <TextoRico texto={q.stem} className="text-lg" />

                <div className="mt-5 space-y-2">
                  {q.alternatives.map((alt, i) => {
                    const elegida = est?.selected === alt.id;
                    return (
                      <button
                        key={alt.id}
                        type="button"
                        onClick={() => selectAlternative(alt.id, q.id)}
                        aria-pressed={elegida}
                        className={cn(
                          // `active:scale` es el acuse de recibo del toque: en
                          // móvil no hay hover, y sin esto la única señal de que
                          // el dedo acertó llega cuando ya se pintó la
                          // alternativa.
                          "flex w-full items-center gap-3 rounded-lg border p-3 text-left transition duration-150 active:scale-[0.99]",
                          // La señal de "elegida" la da la burbuja, no la fila:
                          // en un cartón de respuestas lo que se rellena es el
                          // círculo.
                          elegida
                            ? "border-grafito bg-surface"
                            : "border-border bg-background hover:border-border-strong hover:bg-surface-hover"
                        )}
                      >
                        <Burbuja letra={LABELS[i]} marcada={elegida} />
                        <TextoRico texto={alt.text} inline />
                      </button>
                    );
                  })}
                </div>
              </article>
            );
          })}
        </div>
        {/* ── Navegación ────────────────────────────────────────────── */}
        <nav className="mt-5 flex items-center gap-3">
          <button
            type="button"
            onClick={() => irAPagina(paginaActual - 1)}
            disabled={paginaActual === 0}
            className="rounded-lg border border-border px-4 py-2.5 font-medium transition hover:bg-surface-hover disabled:opacity-40"
          >
            Anterior
          </button>

          {paginaActual < paginas.length - 1 ? (
            <button
              type="button"
              onClick={() => irAPagina(paginaActual + 1)}
              className="btn-glow flex-1 rounded-lg px-4 py-2.5 font-semibold text-accent-foreground"
            >
              {variasEnLaPagina ? "Siguiente texto" : "Siguiente"}
            </button>
          ) : (
            <button
              type="button"
              onClick={() => setConfirmingSubmit(true)}
              className="flex-1 rounded-lg bg-success px-4 py-2.5 font-semibold text-on-fill transition hover:opacity-90"
            >
              Terminar ensayo
            </button>
          )}
        </nav>

        <div className="mt-6 flex justify-between text-sm">
          <button
            type="button"
            onClick={() => setConfirmingSubmit(true)}
            className="flex items-center gap-2 rounded-lg border border-border bg-surface px-4 py-2 text-sm font-medium text-muted transition hover:border-danger/50 hover:bg-danger/5 hover:text-danger"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="5" y="5" width="14" height="14" rx="2" />
            </svg>
            Terminar antes
          </button>
        </div>

        {errorMsg && (
          <p className="mt-4 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">
            {errorMsg}
          </p>
        )}

        <p className="mt-4 text-center text-xs text-muted">
          Atajos: teclas A-D para responder, flechas ← → para navegar.
        </p>
      </main>

      {/* ── Confirmación de término ─────────────────────────────────── */}
      {confirmingSubmit && (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-foreground/40 p-4">
          <div className="w-full max-w-sm rounded-xl border border-border bg-background p-5">
            <h2 className="text-lg font-bold">¿Terminar el ensayo?</h2>
            <p className="mt-2 text-sm text-muted">
              {sinResponder > 0 ? (
                <>
                  Te quedan{" "}
                  <strong className="text-foreground">
                    {sinResponder} {sinResponder === 1 ? "pregunta" : "preguntas"}
                  </strong>{" "}
                  sin responder. En la PAES las respuestas incorrectas no
                  descuentan, así que conviene contestarlas todas.
                </>
              ) : (
                "Respondiste todas las preguntas. Al terminar verás tu puntaje y las explicaciones."
              )}
            </p>
            <div className="mt-5 flex gap-2">
              <button
                type="button"
                onClick={() => setConfirmingSubmit(false)}
                disabled={submitting}
                className="flex-1 rounded-lg border border-border px-4 py-2.5 font-medium hover:bg-surface-hover disabled:opacity-60"
              >
                Seguir
              </button>
              <button
                type="button"
                onClick={doSubmit}
                disabled={submitting}
                className="flex-1 rounded-lg bg-success px-4 py-2.5 font-semibold text-on-fill transition hover:opacity-90 disabled:opacity-60"
              >
                {submitting ? "Enviando…" : "Terminar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


/** Un número de la cabecera con su nombre debajo.
 *
 *  Existe porque tres medidores juntos y sin nombre no se entienden: quien
 *  entra por primera vez no tiene cómo saber si "2:09" es lo que queda, lo que
 *  lleva o lo que debería. El nombre se ve siempre y no es un tooltip: en un
 *  teléfono no hay dónde posar el dedo para descubrirlo.
 *
 *  Va DEBAJO del número, no encima. Son nombres de largo distinto y en un
 *  teléfono se parten en dos líneas; con la etiqueta arriba, cada reloj
 *  arrancaba a una altura distinta y la cabecera quedaba en escalera.
 *
 *  `detalle` es la frase completa, para quien pase el cursor o use lector de
 *  pantalla. El nombre corto responde "qué es"; el detalle, "para qué sirve". */
function Medidor({
  etiqueta,
  detalle,
  children,
}: {
  etiqueta: string;
  detalle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center gap-1" title={detalle}>
      {children}
      <span className="max-w-[6.5rem] text-center text-[10px] leading-tight font-medium text-muted">
        {etiqueta}
      </span>
    </div>
  );
}
