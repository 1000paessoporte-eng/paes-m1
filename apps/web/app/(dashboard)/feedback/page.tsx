import Link from "next/link";
import { cn } from "@paes-m1/utils";
import { getExamReview, listExamAttempts, type ReviewQuestion } from "@/lib/api";
import { ComingSoon } from "@/components/coming-soon";

const DATE_FMT = new Intl.DateTimeFormat("es-CL", {
  day: "2-digit",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

type Filter = "todas" | "incorrectas" | "sin-responder";

function matchesFilter(q: ReviewQuestion, filter: Filter): boolean {
  if (filter === "incorrectas") return q.answered_correctly === false;
  if (filter === "sin-responder") return q.answered_correctly === null;
  return true;
}

export default async function SmartFeedbackPage({
  searchParams,
}: PageProps<"/feedback">) {
  const sp = await searchParams;
  const attempts = (await listExamAttempts()).filter((a) => a.status === "submitted");

  if (attempts.length === 0) {
    return (
      <ComingSoon
        title="Smart Feedback"
        description="Aún no has completado ningún simulacro. Termina un examen en Modo Focus para ver aquí la autopsia del error de cada pregunta."
        icon={
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9" />
            <circle cx="12" cy="12" r="5" />
            <circle cx="12" cy="12" r="1" fill="currentColor" />
          </svg>
        }
      />
    );
  }

  const rawAttempt = Array.isArray(sp.attempt) ? sp.attempt[0] : sp.attempt;
  const selectedId = Number(rawAttempt) || attempts[0].attempt_id;
  const filter: Filter = (["todas", "incorrectas", "sin-responder"] as const).includes(
    (Array.isArray(sp.filter) ? sp.filter[0] : sp.filter) as Filter
  )
    ? ((Array.isArray(sp.filter) ? sp.filter[0] : sp.filter) as Filter)
    : "todas";

  const review = await getExamReview(selectedId);
  const questions = review.questions.filter((q) => matchesFilter(q, filter));

  const FILTERS: { key: Filter; label: string }[] = [
    { key: "todas", label: "Todas" },
    { key: "incorrectas", label: "Incorrectas" },
    { key: "sin-responder", label: "Sin responder" },
  ];

  return (
    <div>
      <h1 className="text-2xl font-semibold">Smart Feedback</h1>
      <p className="mt-1 text-sm text-muted">
        Autopsia del error: diagnóstico por sub-eje y justificación de cada
        distractor.
      </p>

      {/* Selector de intento */}
      <div className="mt-6 flex flex-wrap gap-2">
        {attempts.map((a) => {
          const pct = a.total_questions
            ? Math.round((a.correct / a.total_questions) * 100)
            : 0;
          const active = a.attempt_id === selectedId;
          return (
            <Link
              key={a.attempt_id}
              href={`/feedback?attempt=${a.attempt_id}`}
              className={cn(
                "rounded-lg border px-3 py-2 text-xs transition-colors",
                active
                  ? "border-accent bg-accent/10 text-foreground"
                  : "border-border bg-surface text-muted hover:border-border-strong hover:text-foreground"
              )}
            >
              {DATE_FMT.format(new Date(a.started_at))} · {pct}%
            </Link>
          );
        })}
      </div>

      {/* Diagnóstico por eje */}
      <div className="mt-8 rounded-xl border border-border bg-surface p-5">
        <h2 className="text-sm font-medium text-foreground">
          Diagnóstico por sub-eje temático
        </h2>
        <p className="mt-1 text-xs text-muted">
          Ordenado de más débil a más fuerte. Refuerza estos nodos en el Árbol
          de Habilidades.
        </p>
        <div className="mt-4 flex flex-col gap-2.5">
          {review.node_diagnosis.map((n) => {
            const pct = Math.round(n.accuracy * 100);
            const weak = n.accuracy < 0.75;
            return (
              <div key={n.skill_node_id} className="flex items-center gap-3">
                <span className="w-56 shrink-0 text-xs text-foreground sm:w-72">
                  {n.skill_node_name}
                </span>
                <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-surface-hover">
                  <div
                    className={cn(
                      "h-full rounded-full",
                      weak ? "bg-danger" : "bg-success"
                    )}
                    style={{ width: `${pct}%` }}
                  />
                </div>
                <span className="w-16 shrink-0 text-right text-xs text-muted">
                  {n.correct}/{n.total} · {pct}%
                </span>
              </div>
            );
          })}
        </div>
        <Link
          href="/arbol"
          className="mt-4 inline-block text-xs font-medium text-accent hover:underline"
        >
          Ir al Árbol de Habilidades →
        </Link>
      </div>

      {/* Filtro de preguntas */}
      <div className="mt-8 flex items-center gap-1">
        {FILTERS.map((f) => (
          <Link
            key={f.key}
            href={`/feedback?attempt=${selectedId}${f.key === "todas" ? "" : `&filter=${f.key}`}`}
            className={cn(
              "rounded-md px-3 py-1.5 text-xs font-medium transition-colors",
              filter === f.key
                ? "bg-accent/10 text-foreground"
                : "text-muted hover:bg-surface-hover hover:text-foreground"
            )}
          >
            {f.label}
          </Link>
        ))}
      </div>

      {/* Lista de preguntas */}
      <div className="mt-4 flex flex-col gap-3">
        {questions.length === 0 && (
          <p className="rounded-lg border border-border bg-surface p-4 text-sm text-muted">
            No hay preguntas en este filtro.
          </p>
        )}
        {questions.map((q, i) => (
          <QuestionReview key={q.id} question={q} index={i} />
        ))}
      </div>
    </div>
  );
}

function QuestionReview({
  question: q,
  index,
}: {
  question: ReviewQuestion;
  index: number;
}) {
  const status =
    q.answered_correctly === true
      ? { label: "Correcta", cls: "bg-success/15 text-success" }
      : q.answered_correctly === false
        ? { label: "Incorrecta", cls: "bg-danger/15 text-danger" }
        : { label: "No respondida", cls: "bg-surface-hover text-muted" };

  return (
    <details className="group rounded-xl border border-border bg-surface open:border-border-strong">
      <summary className="flex cursor-pointer list-none items-center justify-between gap-3 px-4 py-3">
        <div className="flex min-w-0 items-center gap-3">
          <span className="text-xs text-muted">{index + 1}</span>
          <span className="truncate text-sm text-foreground">{q.stem}</span>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <span className="hidden text-xs text-muted sm:inline">
            {q.skill_node_name}
          </span>
          <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-medium", status.cls)}>
            {status.label}
          </span>
        </div>
      </summary>

      <div className="flex flex-col gap-2 border-t border-border px-4 py-4">
        {q.alternatives.map((a) => (
          <div
            key={a.id}
            className={cn(
              "rounded-lg border px-3 py-2 text-sm",
              a.is_correct
                ? "border-success/40 bg-success/5"
                : a.selected
                  ? "border-danger/40 bg-danger/5"
                  : "border-border bg-background"
            )}
          >
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-muted">{a.label}</span>
              <span className="text-foreground">{a.text}</span>
              {a.is_correct && (
                <span className="ml-auto text-[10px] font-medium text-success">
                  ✓ Correcta
                </span>
              )}
              {a.selected && !a.is_correct && (
                <span className="ml-auto text-[10px] font-medium text-danger">
                  Tu respuesta
                </span>
              )}
            </div>
            {a.selected && !a.is_correct && a.distractor_justification && (
              <p className="mt-1.5 text-xs text-muted">
                {a.distractor_justification}
              </p>
            )}
          </div>
        ))}
      </div>
    </details>
  );
}
