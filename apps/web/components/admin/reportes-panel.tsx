"use client";

import { useState } from "react";
import { cn } from "@paes-m1/utils";
import { marcarReporteRevisado, type PreguntaReportada } from "@/lib/api";
import { getClientToken } from "@/lib/auth";

/**
 * Las preguntas que los alumnos marcaron como malas.
 *
 * Es la otra mitad del botón de reportar: sin esta pantalla, el aviso entra a
 * la base y ahí se queda. Y como la decisión se toma mirando la pregunta
 * —¿está mal de verdad o el alumno se equivocó?—, el panel trae lo necesario
 * para decidir sin abrir `seed_data.py`: el enunciado, el nodo, la alternativa
 * que el banco da por correcta y lo que escribió cada persona.
 *
 * Agrupado por pregunta y ordenado por cuánta gente avisó: tres avisos de la
 * misma pregunta son una sola cosa que hacer, y son la que hay que hacer
 * primero.
 */

const FECHA = new Intl.DateTimeFormat("es-CL", {
  day: "numeric",
  month: "short",
  hour: "2-digit",
  minute: "2-digit",
});

const MOTIVOS: Record<string, string> = {
  respuesta_incorrecta: "la correcta está mal",
  varias_correctas: "hay más de una correcta",
  enunciado_confuso: "enunciado confuso",
  datos_erroneos: "datos que no calzan",
  otro: "otra cosa",
};

const CONTEXTOS: Record<string, string> = {
  ensayo: "rindiendo",
  revision: "revisando",
  practica: "practicando",
};

export function ReportesPanel({ reportes }: { reportes: PreguntaReportada[] }) {
  // Lo cerrado se saca de la lista en el momento, sin recargar: el panel es
  // una bandeja de entrada y se trabaja de arriba hacia abajo.
  const [cerradas, setCerradas] = useState<Set<number>>(new Set());
  const [cerrando, setCerrando] = useState<number | null>(null);

  const pendientes = reportes.filter((r) => !cerradas.has(r.question_id));

  if (pendientes.length === 0) {
    return (
      <div className="rounded-xl border border-border bg-surface p-5">
        <p className="text-sm font-medium text-success">Ninguna pregunta reportada</p>
        <p className="mt-1 text-sm text-muted">
          {reportes.length > 0
            ? "Todo lo que había reportado quedó revisado."
            : "Cuando un alumno marque una pregunta como mala, aparece acá con lo que escribió."}
        </p>
      </div>
    );
  }

  async function cerrar(questionId: number) {
    setCerrando(questionId);
    try {
      await marcarReporteRevisado(questionId, getClientToken() ?? undefined);
      setCerradas((previas) => new Set(previas).add(questionId));
    } catch {
      // Si falla, la fila se queda: cerrar es la acción que no puede mentir.
    } finally {
      setCerrando(null);
    }
  }

  return (
    <ul className="space-y-3">
      {pendientes.map((r) => (
        <li
          key={r.question_id}
          className="rounded-xl border border-border bg-surface p-4"
        >
          <div className="flex items-baseline justify-between gap-3">
            <p className="text-xs text-muted">
              <span className="font-semibold text-danger tabular-nums">{r.pendientes}</span>{" "}
              {r.pendientes === 1 ? "aviso" : "avisos"} · {r.skill_node_name} · pregunta{" "}
              <code className="text-[11px]">#{r.question_id}</code>
            </p>
            <p className="shrink-0 text-xs text-muted">{FECHA.format(new Date(r.ultimo_en))}</p>
          </div>

          <p className="mt-2 text-sm leading-relaxed text-foreground">{r.stem}</p>

          {r.respuesta_correcta && (
            <p className="mt-2 text-xs text-muted">
              En el banco la correcta es:{" "}
              <span className="font-medium text-success">{r.respuesta_correcta}</span>
            </p>
          )}

          <div className="mt-2.5 flex flex-wrap gap-1.5">
            {Object.entries(r.motivos).map(([motivo, veces]) => (
              <span
                key={motivo}
                className={cn(
                  "rounded-full px-2 py-0.5 text-[11px]",
                  motivo === "respuesta_incorrecta" || motivo === "varias_correctas"
                    ? "bg-danger/10 text-danger"
                    : "bg-surface-hover text-muted"
                )}
              >
                {MOTIVOS[motivo] ?? motivo} · {veces}
              </span>
            ))}
          </div>

          {r.comentarios.some((c) => c.comentario) && (
            <ul className="mt-2.5 space-y-1.5 border-l-2 border-border pl-3">
              {r.comentarios
                .filter((c) => c.comentario)
                .map((c, i) => (
                  <li key={i} className="text-xs leading-relaxed text-foreground">
                    “{c.comentario}”
                    <span className="text-muted"> — {CONTEXTOS[c.contexto] ?? c.contexto}</span>
                  </li>
                ))}
            </ul>
          )}

          <button
            type="button"
            onClick={() => void cerrar(r.question_id)}
            disabled={cerrando === r.question_id}
            className="mt-3 rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-muted transition hover:bg-surface-hover disabled:opacity-60"
          >
            {cerrando === r.question_id ? "Cerrando…" : "Marcar como revisada"}
          </button>
        </li>
      ))}
    </ul>
  );
}
