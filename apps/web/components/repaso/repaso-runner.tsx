"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { cn } from "@paes-m1/utils";
import {
  ApiError,
  responderRepaso,
  type RepasoPregunta,
  type RepasoRespuesta,
} from "@/lib/api";
import { getClientToken, loginHref } from "@/lib/auth";

const FECHA = new Intl.DateTimeFormat("es-CL", { day: "numeric", month: "long" });

/**
 * Una sesión de repaso: las preguntas que falló, de vuelta.
 *
 * La diferencia con Modo Práctica no está en la mecánica --se elige una
 * alternativa y se corrige-- sino en QUÉ se muestra al fallar. Acá cada
 * alternativa incorrecta trae escrito el error exacto que induce a elegirla, y
 * esa es la única razón por la que la segunda vez sale mejor que la primera:
 * el alumno no vuelve a leer la solución correcta, lee por qué su cabeza fue
 * hacia otro lado.
 */
export function RepasoRunner({
  preguntas,
  pendientesTotales,
}: {
  preguntas: RepasoPregunta[];
  pendientesTotales: number;
}) {
  const router = useRouter();
  const [indice, setIndice] = useState(0);
  const [elegida, setElegida] = useState<number | null>(null);
  const [resultado, setResultado] = useState<RepasoRespuesta | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [aciertos, setAciertos] = useState(0);
  const [dominadas, setDominadas] = useState(0);

  const pregunta = preguntas[indice];
  const terminado = indice >= preguntas.length;

  async function responder(alternativaId: number) {
    if (resultado || enviando) return;
    setElegida(alternativaId);
    setEnviando(true);
    setError(null);
    try {
      const r = await responderRepaso(pregunta.question_id, alternativaId, getClientToken() ?? undefined);
      setResultado(r);
      if (r.is_correct) setAciertos((n) => n + 1);
      if (r.dominada) setDominadas((n) => n + 1);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.push(loginHref("/repaso"));
        return;
      }
      setError("No se pudo guardar tu respuesta. Intenta de nuevo.");
      setElegida(null);
    } finally {
      setEnviando(false);
    }
  }

  function siguiente() {
    setElegida(null);
    setResultado(null);
    setIndice((i) => i + 1);
  }

  if (terminado) {
    const quedan = Math.max(0, pendientesTotales - preguntas.length);
    return (
      <div className="mx-auto max-w-2xl text-center">
        <p className="text-5xl leading-none font-bold text-success sm:text-6xl">
          {aciertos}
          <span className="text-2xl font-semibold text-muted">/{preguntas.length}</span>
        </p>
        <h1 className="mt-4 text-2xl font-bold">Repaso terminado</h1>
        <p className="mt-2 text-muted">
          {dominadas > 0 && (
            <>
              <strong className="text-foreground">
                {dominadas} {dominadas === 1 ? "pregunta salió" : "preguntas salieron"} de la
                cola para siempre.
              </strong>{" "}
            </>
          )}
          Las que acertaste vuelven más adelante; las que fallaste, mañana.
        </p>

        <div className="mt-8 flex flex-col gap-2 sm:flex-row sm:justify-center">
          {quedan > 0 ? (
            <button
              type="button"
              onClick={() => router.refresh()}
              className="rounded-lg bg-accent px-5 py-2.5 font-semibold text-accent-foreground hover:opacity-90"
            >
              Repasar las {quedan} que quedan
            </button>
          ) : (
            <Link
              href="/examen"
              className="rounded-lg bg-accent px-5 py-2.5 font-semibold text-accent-foreground hover:opacity-90"
            >
              Rendir un ensayo
            </Link>
          )}
          <Link
            href="/panel"
            className="rounded-lg border border-border px-5 py-2.5 font-medium hover:bg-surface-hover"
          >
            Volver al panel
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <header className="mb-5">
        <div className="flex items-baseline justify-between gap-3">
          <p className="text-sm font-medium">
            Pregunta {indice + 1} de {preguntas.length}
          </p>
          <p className="text-xs text-muted">{pregunta.node_name}</p>
        </div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-surface-hover">
          <div
            className="h-full rounded-full bg-accent transition-[width] duration-500"
            style={{ width: `${(indice / preguntas.length) * 100}%` }}
          />
        </div>
      </header>

      {/* Cuántas veces se le ha resistido. Es lo que convierte "otra pregunta"
          en "esta es LA que no me sale", y hace que valga la pena leer bien. */}
      {pregunta.veces_fallada > 0 && (
        <p className="mb-4 inline-flex items-center gap-1.5 rounded-full border border-accent-warm/30 bg-accent-warm/10 px-3 py-1 text-xs font-medium text-accent-warm-strong">
          La has fallado {pregunta.veces_fallada}{" "}
          {pregunta.veces_fallada === 1 ? "vez" : "veces"}
        </p>
      )}

      {pregunta.passage && (
        <div className="mb-5 max-h-72 overflow-y-auto rounded-xl border border-border bg-surface p-4 text-sm leading-relaxed whitespace-pre-line">
          {pregunta.passage}
        </div>
      )}

      <p className="text-lg leading-relaxed font-medium whitespace-pre-line">
        {pregunta.stem}
      </p>

      {pregunta.image_url && (
        // eslint-disable-next-line @next/next/no-img-element
        <img src={pregunta.image_url} alt="" className="mt-4 max-w-full rounded-lg" />
      )}

      <ul className="mt-5 space-y-2">
        {pregunta.alternatives.map((alt) => {
          const esCorrecta = resultado?.correct_alternative_id === alt.id;
          const esElegida = elegida === alt.id;
          return (
            <li key={alt.id}>
              <button
                type="button"
                onClick={() => responder(alt.id)}
                disabled={resultado !== null || enviando}
                className={cn(
                  "flex w-full items-start gap-3 rounded-xl border p-3.5 text-left transition-colors",
                  resultado === null && "border-border hover:bg-surface-hover",
                  resultado !== null && esCorrecta && "border-success bg-success/10",
                  resultado !== null &&
                    esElegida &&
                    !esCorrecta &&
                    "border-danger bg-danger/10",
                  resultado !== null && !esCorrecta && !esElegida && "border-border opacity-55"
                )}
              >
                <span className="shrink-0 font-mono font-semibold">{alt.label}</span>
                <span>{alt.text}</span>
              </button>
            </li>
          );
        })}
      </ul>

      {error && (
        <p className="mt-4 rounded-lg border border-danger/40 bg-danger/10 px-3 py-2 text-sm text-danger">
          {error}
        </p>
      )}

      {resultado && (
        <div className="mt-5 rounded-xl border border-border bg-surface p-4">
          <p
            className={cn(
              "font-semibold",
              resultado.is_correct ? "text-success" : "text-danger"
            )}
          >
            {resultado.is_correct ? "Correcta" : "Incorrecta"}
          </p>

          {/* Lo primero que se lee al fallar es POR QUÉ eligió lo que eligió,
              no la solución. La solución la puede leer cualquiera sin haberse
              equivocado; esto solo le sirve a quien cayó justo acá. */}
          {resultado.distractor_justification && (
            <div className="mt-3 rounded-lg border-l-2 border-accent-warm bg-accent-warm/5 py-2 pl-3">
              <p className="text-xs font-medium tracking-wide text-accent-warm-strong uppercase">
                Dónde se te fue
              </p>
              <p className="mt-1 text-sm">{resultado.distractor_justification}</p>
            </div>
          )}

          {resultado.explanation && (
            <p className="mt-3 text-sm leading-relaxed whitespace-pre-line text-muted">
              {resultado.explanation}
            </p>
          )}

          <p className="mt-3 text-xs text-muted">
            {resultado.dominada
              ? "La dominaste: no vuelve a aparecer."
              : resultado.proxima_fecha
                ? `Vuelve el ${FECHA.format(new Date(`${resultado.proxima_fecha}T12:00:00`))}.`
                : null}
          </p>

          <button
            type="button"
            onClick={siguiente}
            autoFocus
            className="mt-4 w-full rounded-lg bg-accent px-4 py-2.5 font-semibold text-accent-foreground hover:opacity-90"
          >
            {indice + 1 === preguntas.length ? "Terminar" : "Siguiente"}
          </button>
        </div>
      )}
    </div>
  );
}
