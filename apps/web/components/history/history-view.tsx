"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { ProgressChart } from "@/components/history/progress-chart";
import { AvancePanel } from "@/components/history/avance-panel";
import { HitosPanel } from "@/components/history/hitos-panel";
import { avancePorPrueba, hitos } from "@/lib/progreso";
import { NOMBRE_CORTO } from "@/lib/colores-prueba";
import { ApiError, deleteExamAttempt, type ExamAttemptSummary } from "@/lib/api";
import { getClientToken, loginHref } from "@/lib/auth";
import { formatearTiempo } from "@/lib/tiempo";

const FECHA_FMT = new Intl.DateTimeFormat("es-CL", {
  day: "numeric",
  month: "long",
  year: "numeric",
});

/** Lo que la analítica aporta acá y el historial no sabe por su cuenta. */
export interface ContextoAnalitica {
  preguntasRespondidas: number;
  mejorRacha: number;
}

interface Props {
  intentos: ExamAttemptSummary[];
  /** Puede faltar: si la analítica falla, el historial se muestra igual. */
  analitica?: ContextoAnalitica | null;
}

export function HistoryView({ intentos, analitica }: Props) {
  const router = useRouter();
  const pathname = usePathname();
  const [borrando, setBorrando] = useState<number | null>(null);
  const [confirmarBorrado, setConfirmarBorrado] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const avances = useMemo(() => avancePorPrueba(intentos), [intentos]);

  const logros = useMemo(() => {
    const puntajes = intentos.map((i) => i.estimated_score ?? 0);
    return hitos({
      ensayos: intentos.length,
      // Si la analítica no respondió, las respuestas de los propios ensayos
      // son una cota inferior honesta: cuenta de menos, nunca de más.
      preguntasRespondidas:
        analitica?.preguntasRespondidas ??
        intentos.reduce((total, i) => total + i.answered, 0),
      mejorPuntaje: puntajes.length > 0 ? Math.max(...puntajes) : 0,
      mejorRacha: analitica?.mejorRacha ?? 0,
    });
  }, [intentos, analitica]);

  async function borrar(id: number) {
    setBorrando(id);
    setError(null);
    try {
      await deleteExamAttempt(id, getClientToken() ?? undefined);
      router.refresh();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push(loginHref(pathname));
        return;
      }
      setError("No se pudo eliminar el ensayo. Intenta de nuevo.");
    } finally {
      setBorrando(null);
    }
  }

  async function borrarTodo() {
    setError(null);
    try {
      const token = getClientToken() ?? undefined;
      for (const intento of intentos) {
        await deleteExamAttempt(intento.attempt_id, token);
      }
      setConfirmarBorrado(false);
      router.refresh();
    } catch {
      setError("No se pudo borrar todo el historial.");
    }
  }

  function descargar() {
    const contenido = JSON.stringify(
      { version: 1, exportado: new Date().toISOString(), intentos },
      null,
      2
    );
    const blob = new Blob([contenido], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `paes-m1-historial-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="mx-auto max-w-3xl">
      <header className="mb-6 flex items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Mi progreso</h1>
          <p className="mt-1 text-sm text-muted">
            Tu historial queda guardado en tu cuenta: lo ves desde cualquier
            dispositivo donde inicies sesión.
          </p>
        </div>
        <Link
          href="/examen"
          className="shrink-0 rounded-lg border border-border px-3 py-2 text-sm font-medium hover:bg-surface-hover"
        >
          Nuevo ensayo
        </Link>
      </header>

      {error && (
        <p className="mb-4 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">
          {error}
        </p>
      )}

      {intentos.length === 0 ? (
        <p className="rounded-xl border border-border bg-surface p-6 text-center text-muted">
          Todavía no has rendido ningún ensayo. Al terminar el primero aparecerá
          aquí tu progreso.
        </p>
      ) : (
        <>
          <AvancePanel avances={avances} />

          {/* Con un solo ensayo de cada prueba todavía no hay avance que medir.
              En vez de una tarjeta vacía, se nombra el punto de partida: es el
              número contra el que va a compararse el resto del año. */}
          {avances.length === 0 && (
            <section className="mb-6 rounded-2xl border border-border bg-surface p-5 sm:p-6">
              <p className="text-xs font-medium tracking-wide text-muted uppercase">
                Tu punto de partida
              </p>
              <p className="mt-1 text-5xl leading-none font-bold sm:text-6xl">
                {intentos[0].estimated_score ?? "—"}
                <span className="ml-2 align-middle text-lg font-semibold text-muted">
                  puntos
                </span>
              </p>
              <p className="mt-2.5 text-sm text-muted">
                Es tu primer ensayo de {NOMBRE_CORTO[intentos[0].subject]}. Rinde
                uno más y esta pantalla empieza a mostrarte cuánto subiste desde
                acá.
              </p>
            </section>
          )}

          <HitosPanel logrados={logros.logrados} siguientes={logros.siguientes} />

          {intentos.length >= 2 && (
            <section className="mb-6 rounded-xl border border-border bg-surface p-4">
              <ProgressChart intentos={intentos} />
            </section>
          )}

          {/* Vista de lista: misma información del gráfico, accesible sin color */}
          <section className="mb-6">
            <h2 className="mb-3 text-sm font-semibold">Detalle de los ensayos</h2>
            <ul className="space-y-2">
              {intentos.map((intento) => (
                <li
                  key={intento.attempt_id}
                  className="flex items-center gap-3 rounded-xl border border-border bg-surface p-3.5"
                >
                  <div className="min-w-0 flex-1">
                    <p className="font-medium">
                      {intento.total_questions} preguntas · ritmo {intento.pace}
                    </p>
                    <p className="mt-0.5 text-xs text-muted" suppressHydrationWarning>
                      {FECHA_FMT.format(new Date(intento.started_at))} ·{" "}
                      {intento.correct} correctas ·{" "}
                      {formatearTiempo(intento.elapsed_seconds)}
                    </p>
                  </div>
                  <span className="shrink-0 text-xl font-bold tabular-nums">
                    {intento.estimated_score ?? "—"}
                  </span>
                  <button
                    type="button"
                    onClick={() => borrar(intento.attempt_id)}
                    disabled={borrando === intento.attempt_id}
                    aria-label="Eliminar este ensayo del historial"
                    className="shrink-0 rounded px-2 py-1 text-muted transition-colors hover:bg-surface-hover hover:text-danger disabled:opacity-40"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          </section>

          <div className="flex flex-col gap-2 sm:flex-row">
            <button
              type="button"
              onClick={descargar}
              className="flex-1 rounded-lg border border-border px-4 py-2.5 text-sm font-medium hover:bg-surface-hover"
            >
              Descargar respaldo (JSON)
            </button>
            <button
              type="button"
              onClick={() => setConfirmarBorrado(true)}
              className="flex-1 rounded-lg border border-danger/40 px-4 py-2.5 text-sm font-medium text-danger hover:bg-danger/10"
            >
              Borrar todo el historial
            </button>
          </div>
        </>
      )}

      {confirmarBorrado && (
        <div className="fixed inset-0 z-30 flex items-center justify-center bg-foreground/40 p-4">
          <div className="w-full max-w-sm rounded-xl border border-border bg-background p-5">
            <h2 className="text-lg font-bold">¿Borrar todo el historial?</h2>
            <p className="mt-2 text-sm text-muted">
              Se eliminarán los {intentos.length} ensayos guardados. Esta acción
              no se puede deshacer. Si quieres conservarlos, descarga primero el
              respaldo.
            </p>
            <div className="mt-5 flex gap-2">
              <button
                type="button"
                onClick={() => setConfirmarBorrado(false)}
                className="flex-1 rounded-lg border border-border px-4 py-2.5 font-medium hover:bg-surface-hover"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={borrarTodo}
                className="flex-1 rounded-lg bg-danger px-4 py-2.5 font-semibold text-on-fill hover:opacity-90"
              >
                Borrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
